# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess
import json
import argparse
from yolov4 import detect_cars
import time
import re
from rl_agent import get_rl_recommendation

from csv_logger import log_result, log_analytics, get_results_summary, get_analytics_summary, get_recent_data
from collections import defaultdict
from functools import wraps


app = Flask(__name__)
CORS(app)

# Request/Upload limits (per file and overall request)
MAX_UPLOAD_SIZE_MB = int(os.environ.get("MAX_UPLOAD_SIZE_MB", "200"))
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE_MB * 4 * 1024 * 1024  # 4 files

# Ensure uploads directory exists and is writable at startup
UPLOADS_DIR = os.path.abspath('uploads')
try:
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    # Test write permissions
    test_file = os.path.join(UPLOADS_DIR, '.write_test')
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    app.logger.info(f"Uploads directory ready: {UPLOADS_DIR}")
except Exception as e:
    app.logger.error(f"Failed to initialize uploads directory: {e}")
    app.logger.error(f"Directory: {UPLOADS_DIR}, exists: {os.path.exists(UPLOADS_DIR)}")
    if os.path.exists(UPLOADS_DIR):
        import stat
        st = os.stat(UPLOADS_DIR)
        app.logger.error(f"Permissions: {oct(st.st_mode)}, Owner: {st.st_uid}:{st.st_gid}")

# --- Rate Limiting ---
RATE_LIMIT_REQUESTS = 10  # Max requests
RATE_LIMIT_WINDOW = 60    # Per 60 seconds
request_counts = defaultdict(list)  # IP -> list of timestamps

def rate_limit(func):
    """Simple rate limiter decorator."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        client_ip = request.remote_addr or 'unknown'
        now = time.time()
        
        # Clean old timestamps
        request_counts[client_ip] = [
            ts for ts in request_counts[client_ip] 
            if now - ts < RATE_LIMIT_WINDOW
        ]
        
        # Check rate limit
        if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
            app.logger.warning(f"Rate limit exceeded for {client_ip}")
            return jsonify({
                'error': 'Rate limit exceeded',
                'detail': f'Max {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds',
                'retry_after': int(RATE_LIMIT_WINDOW - (now - request_counts[client_ip][0]))
            }), 429
        
        # Record this request
        request_counts[client_ip].append(now)
        return func(*args, **kwargs)
    return wrapper


GA_BINARY = os.path.abspath("./Algo1")
MAX_LOG_LINES = 500

# Allowed video extensions for validation
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'}
ALLOWED_VIDEO_MIME_PREFIXES = ('video/',)

def is_valid_video_file(filename):
    """Check if file has a valid video extension."""
    if not filename:
        return False
    ext = os.path.splitext(filename.lower())[1]
    return ext in ALLOWED_VIDEO_EXTENSIONS


_RE_INVOC = re.compile(r"cars\s*=\s*\[?([\d,\s]+)\]?")
_RE_START = re.compile(r"pop_size=(\d+)\s+max_iter=(\d+)\s+green_min=(\d+)\s+green_max=(\d+)\s+cycle_time=(\d+)")
_RE_STARTING_BEST = re.compile(r"starting best delay\s*=\s*([0-9.]+)")
_RE_ITER_NEW = re.compile(r"\[iter\s*(\d+)\]\s*new best delay\s*=\s*([0-9.]+)\s*(?:\s+green\s*=\s*\[([0-9,\s]+)\])?")
_RE_ITER_BEST = re.compile(r"\[iter\s*(\d+)\]\s*best delay\s*=\s*([0-9.]+)")
_RE_END_FINAL = re.compile(r"Final greens:\s*N=(\d+)\s*S=(\d+)\s*W=(\d+)\s*E=(\d+)")

def parse_log_lines_to_events(lines):
    events = []
    leftover = []

    for ln in lines:
        s = ln.strip()
        if not s:
            continue

        m = _RE_INVOC.search(s)
        if m:
            nums = [int(x.strip()) for x in m.group(1).split(",") if x.strip()]
            events.append({"type": "invocation", "cars": nums})
            continue

        m = _RE_START.search(s)
        if m:
            events.append({
                "type": "start",
                "pop_size": int(m.group(1)),
                "max_iter": int(m.group(2)),
                "green_min": int(m.group(3)),
                "green_max": int(m.group(4)),
                "cycle_time": int(m.group(5))
            })
            continue

        m = _RE_STARTING_BEST.search(s)
        if m:
            events.append({"type": "starting_best", "best_delay": float(m.group(1))})
            continue

        m = _RE_ITER_NEW.search(s)
        if m:
            it = int(m.group(1))
            best = float(m.group(2))
            greens = None
            if m.group(3):
                greens = [int(x.strip()) for x in m.group(3).split(",") if x.strip()]
            events.append({"type": "iter", "iter": it, "event": "new_best", "best_delay": best, "greens": greens})
            continue

        m = _RE_ITER_BEST.search(s)
        if m:
            it = int(m.group(1))
            best = float(m.group(2))
            events.append({"type": "iter", "iter": it, "event": "best_unchanged", "best_delay": best})
            continue

        m = _RE_END_FINAL.search(s)
        if m:
            greens = [int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))]
            events.append({"type": "end", "final_greens": greens})
            continue

        leftover.append(s)

    return events, leftover

def run_cpp_optimizer(cars, timeout_seconds=20, verbose=True):
    """
    Runs GA C++ binary; returns parsed stdout (or raw) and structured logs:
      - _logs_events: list of parsed event dicts (iter/new_best/start/end etc.)
      - _logs_text: leftover text lines not parsed
      - _logs_raw: joined stderr (trimmed)
    """
    if not os.path.exists(GA_BINARY):
        return {"error": "C++ binary not found", "path": GA_BINARY}

    try:
        args = [GA_BINARY] + [str(int(x)) for x in cars]
    except Exception as e:
        return {"error": "invalid input for optimizer", "detail": str(e)}

    if verbose:
        args.append("--verbose")

    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        return {"error": "C++ optimizer timed out"}
    except Exception as e:
        return {"error": "failed to run C++ binary", "detail": str(e)}

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "")
    stderr_lines_all = stderr.splitlines()

    stderr_lines = stderr_lines_all[-MAX_LOG_LINES:] if len(stderr_lines_all) > MAX_LOG_LINES else stderr_lines_all

    events, leftover = parse_log_lines_to_events(stderr_lines)

    try:
        parsed_stdout = json.loads(stdout) if stdout else {}
    except Exception:
        parsed_stdout = {"raw_stdout": stdout}

    if isinstance(parsed_stdout, dict):
        parsed_stdout["_logs_events"] = events
        parsed_stdout["_logs_text"] = leftover
        parsed_stdout["_logs_raw"] = "\n".join(stderr_lines)
    else:
        parsed_stdout = {
            "result": parsed_stdout,
            "_logs_events": events,
            "_logs_text": leftover,
            "_logs_raw": "\n".join(stderr_lines)
        }

    if proc.returncode != 0:
        parsed_stdout["error"] = "C++ returned non-zero exit code"
        parsed_stdout["_returncode"] = proc.returncode

    return parsed_stdout

@app.route('/test_optimize', methods=['POST'])
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


DEBUG_UPLOAD = os.environ.get("DEBUG_UPLOAD", "1") == "1"

@app.route('/health', methods=['GET'])
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


@app.route('/upload', methods=['POST'])
@rate_limit
def upload_files():
    start_ts = time.time()
    app.logger.info("Received /upload request")

    files = request.files.getlist('videos')
    if len(files) != 4:
        msg = f"Wrong number of files: got {len(files)} (need 4)"
        app.logger.error(msg)
        return jsonify({'error': 'Please upload exactly 4 videos', 'detail': msg}), 400

    # Validate video file formats
    invalid_files = []
    invalid_mime = []
    oversized_files = []
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
        app.logger.error(f"Invalid video formats: {invalid_files}")
        return jsonify({
            'error': 'Invalid video format detected',
            'detail': f'Supported formats: {list(ALLOWED_VIDEO_EXTENSIONS)}',
            'invalid_files': invalid_files
        }), 400
    
    if invalid_mime:
        app.logger.error(f"Invalid MIME types: {invalid_mime}")
        return jsonify({
            'error': 'Invalid video MIME type detected',
            'detail': 'Only video MIME types are allowed',
            'invalid_files': invalid_mime
        }), 400
    
    if oversized_files:
        app.logger.error(f"Oversized uploads: {oversized_files}")
        return jsonify({
            'error': 'File too large',
            'detail': f'Maximum allowed size is {MAX_UPLOAD_SIZE_MB} MB per file',
            'invalid_files': oversized_files
        }), 400


    # Ensure uploads directory exists
    try:
        os.makedirs(UPLOADS_DIR, exist_ok=True)
    except Exception as e:
        app.logger.error(f"Cannot create uploads directory: {e}")
        return jsonify({"error": "Server configuration error", "detail": f"Cannot create uploads directory: {str(e)}"}), 500

    video_paths = []
    save_errors = []
    for i, file in enumerate(files):
        video_path = os.path.join(UPLOADS_DIR, f'video_{i}.mp4')
        try:
            app.logger.info(f"Attempting to save file {i} to: {video_path}")
            file.save(video_path)
            app.logger.info(f"Successfully saved uploaded file -> {video_path}")
            video_paths.append(video_path)
        except PermissionError as e:
            app.logger.exception(f"Permission denied saving to {video_path}")
            save_errors.append({"index": i, "path": video_path, "error": f"Permission denied: {str(e)}"})
        except Exception as e:
            app.logger.exception(f"Failed to save uploaded file {video_path}")
            save_errors.append({"index": i, "path": video_path, "error": str(e)})

    if save_errors:
        return jsonify({"error": "Failed to save uploaded files", "details": save_errors}), 500

    # Import parallel detection function
    from yolov4 import detect_cars_parallel
    
    # Use parallel processing with multiprocessing (spawn mode - no semaphore leaks)
    app.logger.info("Starting parallel video detection for %d videos", len(video_paths))
    
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
                app.logger.error(f"Detection error for lane {i}: {error}")
            else:
                detect_logs.append({"video": video_paths[i], "cars": count})
                app.logger.info(f"Lane {i}: {count} cars detected")
                
    except Exception as e:
        app.logger.exception("Parallel detection failed")
        return jsonify({"error": "Video detection failed", "detail": str(e)}), 500
    
    # Check if any detections failed
    if detection_errors:
        return jsonify({
            'error': 'Car detection failed for some lanes',
            'detection_errors': detection_errors,
            'partial_results': num_cars_list
        }), 500

    app.logger.info("All detections done: %s", num_cars_list)

    try:
        app.logger.info("Calling C++ optimizer with cars=%s", num_cars_list)
        result = run_cpp_optimizer(num_cars_list, timeout_seconds=30, verbose=True)
        if isinstance(result, dict):
            # Log a clean summary without the large raw logs/events
            log_summary = {k: v for k, v in result.items() if not k.startswith('_log')}
            app.logger.info("C++ optimizer returned: %s", log_summary)
        else:
            app.logger.info("C++ optimizer returned: <non-dict>")
    except Exception as e:
        app.logger.exception("Exception while calling optimizer")
        return jsonify({"error": "Exception while calling optimizer", "detail": str(e)}), 500

    if isinstance(result, dict) and result.get("error"):
        app.logger.error("Optimizer error: %s", result)
        result["_detect_info"] = detect_logs
        result["elapsed_seconds"] = time.time() - start_ts
        return jsonify(result), 500

    # RL Recommendation
    try:
        rl_rec = get_rl_recommendation(num_cars_list, result)
        app.logger.info("RL Recommendation: %s", str(rl_rec))
    except Exception as e:
        app.logger.exception("RL Recommendation failed")
        rl_rec = {"error": "RL recommendation failed", "detail": str(e)}

    response = {"result": result, "rl_recommendation": rl_rec}
    
    # Log to CSV
    try:
        delay = result.get('delay', 0) if isinstance(result, dict) else 0
        elapsed = time.time() - start_ts
        log_result(num_cars_list, result, rl_rec, delay, elapsed)
        log_analytics(num_cars_list, result, 'success')
        app.logger.info("Results logged to CSV")
    except Exception as e:
        app.logger.warning("Failed to log to CSV: %s", str(e))
    
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


@app.route('/stats', methods=['GET'])
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Traffic optimizer API / live camera runner")
    parser.add_argument('--real', action='store_true', help='Run live camera ingestion instead of API server')
    parser.add_argument('--camera', action='append', help='Camera source (use multiple --camera entries, expected 4)')
    parser.add_argument('--verbose', action='store_true', help='Verbose optimizer output')
    args = parser.parse_args()

    if args.real:
        sources = args.camera if args.camera else []
        if not sources:
            env_sources = os.environ.get("CAM_SOURCES", "")
            sources = [s.strip() for s in env_sources.split(",") if s.strip()]
        if len(sources) != 4:
            print(f"[Live] Expected 4 camera sources, got {len(sources)}. Provide --camera four times or CAM_SOURCES comma-list.")
            raise SystemExit(1)

        try:
            from stream_ingest import run_live_optimization
        except Exception as e:
            print(f"[Live] Failed to import stream_ingest: {e}")
            raise SystemExit(1)

        payload, errors = run_live_optimization(sources, verbose=args.verbose)
        print("\n=== Live Optimization Result ===")
        print(payload)
        if any(errors):
            print("\nErrors:", errors)
    else:
        try:
            os.makedirs(UPLOADS_DIR, exist_ok=True)
            app.logger.info(f"Starting Flask app with uploads directory: {UPLOADS_DIR}")
        except Exception as e:
            app.logger.error(f"Cannot create uploads directory: {e}")
        app.run(host='0.0.0.0', port=5000, debug=True)
