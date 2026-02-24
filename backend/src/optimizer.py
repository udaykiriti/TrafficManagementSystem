import os
import subprocess
import json
import re

GA_BINARY = os.path.abspath("./Algo1")
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
        parsed_stdout["error"] = "C++ returned non-zero exit code"
        parsed_stdout["_returncode"] = proc.returncode

    return parsed_stdout
