# app.py
from flask import Flask, request, jsonify, current_app
from flask_cors import CORS
import os
import subprocess
import json
import threading
from yolov4 import detect_cars
import time
import re


app = Flask(__name__)
CORS(app)


GA_BINARY = os.path.abspath("./Algo")
MAX_LOG_LINES = 500

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
        parsed_stdout["_error"] = "C++ returned non-zero exit code"
        parsed_stdout["_returncode"] = proc.returncode

    return parsed_stdout

def run_cpp_optimizer_stream(cars, timeout_seconds=60, verbose=True):
    """
    Stream runner: starts the C++ binary and forwards stderr lines to Flask logger
    in real time. Returns parsed stdout JSON at the end. Useful for live console logs.
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
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    except Exception as e:
        return {"error": "failed to start C++ binary", "detail": str(e)}

    stderr_lines = []

    def forward_stderr(stderr_pipe):
        for line in stderr_pipe:
            line = line.rstrip("\n")
            stderr_lines.append(line)
            try:
                current_app.logger.info("[GA] %s", line)
            except RuntimeError:
                print("[GA]", line)
        stderr_pipe.close()

    stderr_thread = threading.Thread(target=forward_stderr, args=(proc.stderr,), daemon=True)
    stderr_thread.start()

    try:
        stdout, _ = proc.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        proc.kill()
        stderr_thread.join(timeout=1)
        return {"error": "C++ optimizer timed out and was killed"}

    stderr_thread.join(timeout=1)

    stdout = (stdout or "").strip()
    combined_stderr = "\n".join(stderr_lines).strip()

    if proc.returncode != 0:
        return {"error": "C++ failed", "returncode": proc.returncode, "stdout": stdout, "stderr": combined_stderr}

    try:
        parsed = json.loads(stdout)
    except Exception:
        parsed = {"raw_stdout": stdout}

    parsed["_logs_stderr"] = combined_stderr
    return parsed

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

@app.route('/upload', methods=['POST'])
def upload_files():
    start_ts = time.time()
    app.logger.info("Received /upload request")

    files = request.files.getlist('videos')
    if len(files) != 4:
        msg = f"Wrong number of files: got {len(files)} (need 4)"
        app.logger.error(msg)
        return jsonify({'error': 'Please upload exactly 4 videos', 'detail': msg}), 400

    if not os.path.exists('uploads'):
        os.makedirs('uploads', exist_ok=True)

    video_paths = []
    save_errors = []
    for i, file in enumerate(files):
        video_path = os.path.join('uploads', f'video_{i}.mp4')
        try:
            file.save(video_path)
            app.logger.info("Saved uploaded file -> %s", video_path)
            video_paths.append(video_path)
        except Exception as e:
            app.logger.exception("Failed to save uploaded file %s", video_path)
            save_errors.append({"index": i, "path": video_path, "error": str(e)})

    if save_errors:
        return jsonify({"error": "Failed to save uploaded files", "details": save_errors}), 500

    num_cars_list = []
    detect_logs = []
    
    for video_file in video_paths:
        try:
            app.logger.info("Running detect_cars on %s", video_file)
            num_cars = detect_cars(video_file)
            app.logger.info("detect_cars returned: %s for %s", str(num_cars), video_file)
            if not isinstance(num_cars, int):
                try:
                    num_cars = int(num_cars)
                    app.logger.info("Casted detect_cars output to int: %d", num_cars)
                except Exception as e:
                    app.logger.exception("detect_cars returned non-int and could not be cast")
                    return jsonify({"error": "detect_cars returned non-integer", "value": str(num_cars)}), 500
            num_cars_list.append(num_cars)
            detect_logs.append({"video": video_file, "cars": num_cars})
        except Exception as e:
            app.logger.exception("detect_cars raised exception for %s", video_file)
            return jsonify({'error': 'car detection failed', 'detail': str(e)}), 500

    app.logger.info("All detections done: %s", num_cars_list)

    try:
        app.logger.info("Calling C++ optimizer with cars=%s", num_cars_list)
        result = run_cpp_optimizer(num_cars_list, timeout_seconds=30, verbose=True)
        app.logger.info("C++ optimizer returned: %s", str(result if isinstance(result, dict) else "<non-dict>"))
    except Exception as e:
        app.logger.exception("Exception while calling optimizer")
        return jsonify({"error": "Exception while calling optimizer", "detail": str(e)}), 500

    if isinstance(result, dict) and result.get("error"):
        app.logger.error("Optimizer error: %s", result)
        result["_detect_info"] = detect_logs
        result["_elapsed_seconds"] = time.time() - start_ts
        return jsonify(result), 500

    response = {"result": result}
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
@app.route('/upload_stream', methods=['POST'])
def upload_files_stream():

    files = request.files.getlist('videos')
    if len(files) != 4:
        return jsonify({'error': 'Please upload exactly 4 videos'}), 400

    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    video_paths = []
    for i, file in enumerate(files):
        video_path = os.path.join('uploads', f'video_{i}.mp4')
        file.save(video_path)
        video_paths.append(video_path)

    num_cars_list = []
    for video_file in video_paths:
        try:
            num_cars = detect_cars(video_file)
            if not isinstance(num_cars, int):
                num_cars = int(num_cars)
        except Exception as e:
            return jsonify({'error': 'car detection failed', 'detail': str(e)}), 500
        num_cars_list.append(num_cars)

    result = run_cpp_optimizer_stream(num_cars_list, timeout_seconds=60, verbose=True)

    if isinstance(result, dict) and result.get("error"):
        return jsonify(result), 500
    return jsonify(result), 200

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(host='0.0.0.0', port=5000, debug=True)
