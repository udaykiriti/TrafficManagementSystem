import os
import time
from flask import request, jsonify, Blueprint, current_app
from werkzeug.utils import secure_filename

from src.optimizer import run_cpp_optimizer, GA_BINARY
from src.validation import is_valid_video_file, ALLOWED_VIDEO_EXTENSIONS, ALLOWED_VIDEO_MIME_PREFIXES
from src.limiter import rate_limit
from csv_logger import log_result, log_analytics, get_results_summary, get_analytics_summary, get_recent_data
from rl_agent import get_rl_recommendation
from yolov4 import detect_cars_parallel

api = Blueprint('api', __name__)

@api.route('/test_optimize', methods=['POST'])
def test_optimize():
    """
    Quick test endpoint — POST JSON: {"cars":[N,S,W,E]}
    Returns optimizer result (with logs).
    """
    data = request.get_json(force=True)
    cars = data.get("cars")
    if not cars or len(cars) != 4:
        return jsonify({"error":"send JSON {\"cars\":[N,S,W,E]}"}), 400

    result = run_cpp_optimizer(cars, verbose=True)
    if isinstance(result, dict) and result.get("error"):
        return jsonify(result), 500
    return jsonify(result), 200


@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    status = {
        'status': 'healthy',
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'components': {
            'api': 'ok',
            'ga_binary': 'ok' if os.path.exists(GA_BINARY) else 'missing',
            'yolo_weights': 'ok' if os.path.exists('yolov4-tiny.weights') else 'missing',
            'yolo_config': 'ok' if os.path.exists('yolov4-tiny.cfg') else 'missing'
        }
    }
    # Overall status is unhealthy if any component is missing
    if 'missing' in status['components'].values():
        status['status'] = 'degraded'
        return jsonify(status), 503
    return jsonify(status), 200


@api.route('/upload', methods=['POST'])
@rate_limit
def upload_files():
    start_ts = time.time()
    current_app.logger.info("Received /upload request")

    files = request.files.getlist('videos')
    if len(files) != 4:
        msg = f"Wrong number of files: got {len(files)} (need 4)"
        current_app.logger.error(msg)
        return jsonify({'error': 'Please upload exactly 4 videos', 'detail': msg}), 400

    # Validate video file formats
    invalid_files = []
    invalid_mime = []
    oversized_files = []
    MAX_UPLOAD_SIZE_MB = current_app.config["MAX_UPLOAD_SIZE_MB"]
    for i, f in enumerate(files):
        if not is_valid_video_file(f.filename):
            invalid_files.append({'index': i, 'filename': f.filename})
            continue
        
        mimetype = (f.mimetype or '').lower()
        if mimetype and not mimetype.startswith(ALLOWED_VIDEO_MIME_PREFIXES):
            invalid_mime.append({'index': i, 'filename': f.filename, 'mimetype': mimetype})
        
        size_bytes = f.content_length
        if size_bytes is None:
            try:
                pos = f.stream.tell()
                f.stream.seek(0, os.SEEK_END)
                size_bytes = f.stream.tell()
                f.stream.seek(pos)
            except Exception:
                size_bytes = None
        
        if size_bytes is not None and size_bytes > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            oversized_files.append({
                'index': i,
                'filename': f.filename,
                'size_mb': round(size_bytes / (1024 * 1024), 2)
            })
    
    if invalid_files:
        current_app.logger.error(f"Invalid video formats: {invalid_files}")
        return jsonify({
            'error': 'Invalid video format detected',
            'detail': f'Supported formats: {list(ALLOWED_VIDEO_EXTENSIONS)}',
            'invalid_files': invalid_files
        }), 400
    
    if invalid_mime:
        current_app.logger.error(f"Invalid MIME types: {invalid_mime}")
        return jsonify({
            'error': 'Invalid video MIME type detected',
            'detail': 'Only video MIME types are allowed',
            'invalid_files': invalid_mime
        }), 400
    
    if oversized_files:
        current_app.logger.error(f"Oversized uploads: {oversized_files}")
        return jsonify({
            'error': 'File too large',
            'detail': f'Maximum allowed size is {MAX_UPLOAD_SIZE_MB} MB per file',
            'invalid_files': oversized_files
        }), 400


    UPLOADS_DIR = current_app.config["UPLOADS_DIR"]
    # Ensure uploads directory exists
    try:
        os.makedirs(UPLOADS_DIR, exist_ok=True)
    except Exception as e:
        current_app.logger.error(f"Cannot create uploads directory: {e}")
        return jsonify({"error": "Server configuration error", "detail": f"Cannot create uploads directory: {str(e)}"}), 500

    video_paths = []
    save_errors = []
    for i, file in enumerate(files):
        filename = secure_filename(f'video_{i}.mp4')
        video_path = os.path.join(UPLOADS_DIR, filename)
        try:
            current_app.logger.info(f"Attempting to save file {i} to: {video_path}")
            file.save(video_path)
            current_app.logger.info(f"Successfully saved uploaded file -> {video_path}")
            video_paths.append(video_path)
        except PermissionError as e:
            current_app.logger.exception(f"Permission denied saving to {video_path}")
            save_errors.append({"index": i, "path": video_path, "error": f"Permission denied: {str(e)}"})
        except Exception as e:
            current_app.logger.exception(f"Failed to save uploaded file {video_path}")
            save_errors.append({"index": i, "path": video_path, "error": str(e)})

    if save_errors:
        return jsonify({"error": "Failed to save uploaded files", "details": save_errors}), 500

    # Use parallel processing with multiprocessing (spawn mode - no semaphore leaks)
    current_app.logger.info("Starting parallel video detection for %d videos", len(video_paths))
    
    try:
        # Allow up to 4 parallel workers (one per lane) to maximize CPU usage
        results, errors = detect_cars_parallel(video_paths, max_workers=4)
        
        num_cars_list = results
        detection_errors = []
        detect_logs = []
        
        for i, (count, error) in enumerate(zip(results, errors)):
            if error:
                detection_errors.append({'index': i, 'error': error})
                detect_logs.append({"video": video_paths[i], "error": error})
                current_app.logger.error(f"Detection error for lane {i}: {error}")
            else:
                detect_logs.append({"video": video_paths[i], "cars": count})
                current_app.logger.info(f"Lane {i}: {count} cars detected")
                
    except Exception as e:
        current_app.logger.exception("Parallel detection failed")
        return jsonify({"error": "Video detection failed", "detail": str(e)}), 500
    
    # Check if any detections failed
    if detection_errors:
        return jsonify({
            'error': 'Car detection failed for some lanes',
            'detection_errors': detection_errors,
            'partial_results': num_cars_list
        }), 500

    current_app.logger.info("All detections done: %s", num_cars_list)

    try:
        current_app.logger.info("Calling C++ optimizer with cars=%s", num_cars_list)
        result = run_cpp_optimizer(num_cars_list, timeout_seconds=30, verbose=True)
        if isinstance(result, dict):
            # Log a clean summary without the large raw logs/events
            log_summary = {k: v for k, v in result.items() if not k.startswith('_log')}
            current_app.logger.info("C++ optimizer returned: %s", log_summary)
        else:
            current_app.logger.info("C++ optimizer returned: <non-dict>")
    except Exception as e:
        current_app.logger.exception("Exception while calling optimizer")
        return jsonify({"error": "Exception while calling optimizer", "detail": str(e)}), 500

    if isinstance(result, dict) and result.get("error"):
        current_app.logger.error("Optimizer error: %s", result)
        result["_detect_info"] = detect_logs
        result["elapsed_seconds"] = time.time() - start_ts
        return jsonify(result), 500

    # RL Recommendation
    try:
        rl_rec = get_rl_recommendation(num_cars_list, result)
        current_app.logger.info("RL Recommendation: %s", str(rl_rec))
    except Exception as e:
        current_app.logger.exception("RL Recommendation failed")
        rl_rec = {"error": "RL recommendation failed", "detail": str(e)}

    response = {"result": result, "rl_recommendation": rl_rec}
    
    # Log to CSV
    try:
        delay = result.get('delay', 0) if isinstance(result, dict) else 0
        elapsed = time.time() - start_ts
        log_result(num_cars_list, result, rl_rec, delay, elapsed)
        log_analytics(num_cars_list, result, 'success')
        current_app.logger.info("Results logged to CSV")
    except Exception as e:
        current_app.logger.warning("Failed to log to CSV: %s", str(e))
    
    DEBUG_UPLOAD = current_app.config["DEBUG_UPLOAD"]
    if DEBUG_UPLOAD:
        logs = None
        if isinstance(result, dict):
            logs = result.pop("_logs_stderr", None)
        response["detected_cars"] = num_cars_list
        response["detect_logs"] = detect_logs
        response["cpp_logs_stderr"] = logs
        response["elapsed_seconds"] = time.time() - start_ts
        if isinstance(result, dict):
            response.update(result)

    return jsonify(response), 200


@api.route('/stats', methods=['GET'])
def get_stats():
    """Get summary statistics from CSV logs."""
    try:
        results_summary = get_results_summary()
        analytics_summary = get_analytics_summary()
        recent_data = get_recent_data(20)
        return jsonify({
            'results': results_summary,
            'analytics': analytics_summary,
            'recent': recent_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
