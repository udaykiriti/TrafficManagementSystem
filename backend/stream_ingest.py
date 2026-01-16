#!/usr/bin/env python3
"""
Live camera ingestion helper (non-invasive to core API).
Samples frames from RTSP/USB cameras, counts vehicles with YOLO, then runs the C++ optimizer + RL.
"""

import argparse
import time
from typing import List, Tuple

import cv2 as cv

from yolov4 import _create_model, VEHICLE_CLASSES, CONF_THRESHOLD, NMS_THRESHOLD
from app import run_cpp_optimizer
from rl_agent import get_rl_recommendation


def _count_frame(model, class_names, frame) -> int:
    classes, scores, boxes = model.detect(frame, CONF_THRESHOLD, NMS_THRESHOLD)
    return int(sum(1 for cid in classes if class_names[cid] in VEHICLE_CLASSES))


def detect_single_stream(source: str, model, class_names, warmup_frames: int = 5, timeout: int = 10) -> Tuple[int, str]:
    """
    Sample a few frames from a live camera/RTSP/USB source and return a vehicle count.
    Returns (count, error_message). On error, count is 0 and error_message is non-empty.
    """
    cap = cv.VideoCapture(source)
    if not cap.isOpened():
        return 0, f"Could not open camera source: {source}"

    start = time.time()
    last_frame = None

    while warmup_frames > 0 and time.time() - start < timeout:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.05)
            continue
        last_frame = frame
        warmup_frames -= 1

    cap.release()

    if last_frame is None:
        return 0, f"No frames read from source: {source}"

    try:
        count = _count_frame(model, class_names, last_frame)
        return count, ""
    except Exception as e:
        return 0, f"Detection failed for {source}: {e}"


def detect_cameras(camera_sources: List[str]) -> Tuple[List[int], List[str]]:
    """Detect vehicles on a list of camera sources sequentially."""
    model, class_names = _create_model()
    counts = []
    errors = []

    for idx, src in enumerate(camera_sources):
        count, err = detect_single_stream(src, model, class_names)
        counts.append(count)
        errors.append(err)
        print(f"[Stream] Cam {idx}: count={count} err={err}")

    return counts, errors


def run_live_optimization(camera_sources: List[str], verbose: bool = True):
    """
    Runs detection on all cameras, then invokes GA optimizer and RL recommendation.
    Returns (result_dict, errors).
    """
    counts, errors = detect_cameras(camera_sources)
    if any(errors):
        print("[Stream] Detection errors: ", errors)

    if len(counts) != 4:
        return {"error": f"Expected 4 camera sources, got {len(counts)}", "counts": counts}, errors

    result = run_cpp_optimizer(counts, verbose=verbose)
    rl_rec = get_rl_recommendation(counts, result if isinstance(result, dict) else {})

    payload = {
        "detected_cars": counts,
        "optimizer_result": result,
        "rl_recommendation": rl_rec,
    }
    return payload, errors


def main():
    parser = argparse.ArgumentParser(description="Live camera ingestion helper (non-API).")
    parser.add_argument(
        "--camera",
        action="append",
        required=True,
        help="Camera source (RTSP/HTTP URL or device index). Pass exactly 4 (use multiple --camera flags).",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose optimizer output")
    args = parser.parse_args()

    camera_sources = args.camera
    payload, errors = run_live_optimization(camera_sources, verbose=args.verbose)

    print("\n=== Live Optimization Result ===")
    print(payload)
    if any(errors):
        print("\nErrors:", errors)


if __name__ == "__main__":
    main()
