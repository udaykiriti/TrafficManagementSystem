"""
YOLOv4-tiny Car Detection Module - Memory-Safe Parallel Processing
Features: CUDA auto-detection, multiprocessing with spawn, memory limits
"""

import cv2 as cv
import time
import os
import gc
import sys
import numpy as np
import multiprocessing as mp

# <!--- Configuration --->
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLASS_FILE = os.path.join(BASE_DIR, 'classes.txt')
CONFIG_FILE = os.path.join(BASE_DIR, 'yolov4-tiny.cfg')
WEIGHTS_FILE = os.path.join(BASE_DIR, 'yolov4-tiny.weights')
FULL_CFG_FILE = os.path.join(BASE_DIR, 'yolov4.cfg')
FULL_WEIGHTS_FILE = os.path.join(BASE_DIR, 'yolov4.weights')
TINY_CFG_FILE = CONFIG_FILE
TINY_WEIGHTS_FILE = WEIGHTS_FILE

# <!--- Performance tuning ---->
cv.setNumThreads(1)
cv.ocl.setUseOpenCL(False)

# <!--- Model configuration ---->
MODEL_TYPE = 'full'          # 'full' (YOLOv4) or 'tiny' (YOLOv4-tiny)
CONF_THRESHOLD = 0.2         # Detection confidence threshold
NMS_THRESHOLD = 0.4          # Non-maximum suppression threshold
INPUT_SIZE = 416             # Input resolution (lower = faster, higher = more accurate)
SKIP_FRAMES = 5              # Process 1 frame every (SKIP_FRAMES + 1)
MAX_PARALLEL_WORKERS = max(4, mp.cpu_count())     # Max concurrent processes (default to at least 4 for 4 lanes)

# <!--- Target classes (COCO) ---->
VEHICLE_CLASSES = {'car', 'motorbike', 'bus', 'truck', 'bicycle'}


def get_optimal_backend():
    """Auto-detect best backend (CUDA > OpenCL > CPU)"""
    try:
        if cv.cuda.getCudaEnabledDeviceCount() > 0:
            print("[YOLO] CUDA detected - using GPU acceleration", flush=True)
            return cv.dnn.DNN_BACKEND_CUDA, cv.dnn.DNN_TARGET_CUDA
    except:
        pass
    print("[YOLO] Using CPU backend", flush=True)
    return cv.dnn.DNN_BACKEND_DEFAULT, cv.dnn.DNN_TARGET_CPU

def create_model():
    """Create a new model instance (for use in subprocess)."""
    # <!--- Choose files based on MODEL_TYPE ---->
    if MODEL_TYPE == 'full':
        cfg_path = FULL_CFG_FILE
        weights_path = FULL_WEIGHTS_FILE
    else:  # <!-- 'tiny' -->
        cfg_path = TINY_CFG_FILE
        weights_path = TINY_WEIGHTS_FILE

    if not os.path.exists(weights_path):
        raise FileNotFoundError(f"Missing weights: {weights_path}")
    if not os.path.exists(cfg_path):
        raise FileNotFoundError(f"Missing config: {cfg_path}")
    
    net = cv.dnn.readNet(weights_path, cfg_path)
    backend, target = get_optimal_backend()
    net.setPreferableBackend(backend)
    net.setPreferableTarget(target)
    
    model = cv.dnn_DetectionModel(net)
    model.setInputParams(size=(INPUT_SIZE, INPUT_SIZE), scale=1/255, swapRB=True)
    
    # <!--- Load class names --->
    with open(CLASS_FILE, 'r') as f:
        class_names = [c.strip() for c in f.readlines()]
    
    return model, class_names


def _detect_cars_worker(video_file, result_queue, worker_id):
    """
    Worker function for multiprocessing.
    Creates its own model instance to avoid sharing issues.
    """
    try:
        print(f"[YOLO-W{worker_id}] Starting detection for {video_file}", flush=True)
        
        # <!--- Each worker creates its own model --->
        model, class_names = create_model()
        
        if not os.path.exists(video_file):
            result_queue.put((worker_id, video_file, None, f"File not found: {video_file}"))
            return
        
        cap = cv.VideoCapture(video_file)
        if not cap.isOpened():
            result_queue.put((worker_id, video_file, None, f"Could not open video: {video_file}"))
            return
        
        total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
        fps_video = cap.get(cv.CAP_PROP_FPS) or 30
        
        print(f"[YOLO-W{worker_id}] Processing {video_file}: {total_frames} frames @ {fps_video:.1f} FPS", flush=True)
        
        start_time = time.time()
        car_counts = []
        frame_idx = 0
        processed_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # <!--- Skip frames for speed --->
            if frame_idx % (SKIP_FRAMES + 1) == 0:
                # <!--- Detect vehicles in frame (all types: car, truck, bus, motorbike, bicycle) --->
                classes, scores, boxes = model.detect(frame, CONF_THRESHOLD, NMS_THRESHOLD)
                vehicle_count = sum(1 for cid in classes if class_names[cid] in VEHICLE_CLASSES)
                car_counts.append(vehicle_count)
                processed_count += 1
                
                # <!--- Progress update every 100 processed frames --->
                if processed_count % 100 == 0:
                    elapsed = time.time() - start_time
                    fps = processed_count / elapsed if elapsed > 0 else 0
                    print(f"[YOLO-W{worker_id}] Progress: {processed_count} frames ({fps:.1f} FPS)", flush=True)
            
            frame_idx += 1
            frame = None  # <!--- Release memory --->
        
        cap.release()
        
        elapsed = time.time() - start_time
        actual_fps = processed_count / elapsed if elapsed > 0 else 0
        print(f"[YOLO-W{worker_id}] Done: {processed_count} frames in {elapsed:.2f}s ({actual_fps:.1f} FPS)", flush=True)
        
        if not car_counts:
            result_queue.put((worker_id, video_file, 0, None))
            return
        
        # <!--- Return the MAXIMUM number of vehicles seen in any frame --->
        # <!--- This represents peak traffic load for signal timing --->
        max_vehicles = max(car_counts)
        avg_vehicles = np.mean(car_counts)
        
        print(f"[YOLO-W{worker_id}] Stats: max={max_vehicles}, avg={avg_vehicles:.1f}, frames={len(car_counts)}", flush=True)
        
        # <!--- Use maximum for traffic signal optimization --->
        result = int(max_vehicles)
        result_queue.put((worker_id, video_file, result, None))
        
        # <!--- Cleanup --->
        del model, class_names
        gc.collect()
        
    except Exception as e:
        print(f"[YOLO-W{worker_id}] Error: {e}", flush=True)
        result_queue.put((worker_id, video_file, None, str(e)))


def detect_cars(video_file):
    """
    Detect cars in a single video file.
    Uses subprocess to isolate memory and prevent leaks in main process.
    """
    # <!--- Use spawn method to avoid fork issues with semaphores --->
    ctx = mp.get_context('spawn')
    result_queue = ctx.Queue()
    
    proc = ctx.Process(
        target=_detect_cars_worker,
        args=(video_file, result_queue, 0)
    )
    proc.start()
    
    # <!--- Wait for result with timeout (5 minutes max per video) --->
    try:
        proc.join(timeout=300)
        
        if proc.is_alive():
            print(f"[YOLO] Timeout - terminating worker for {video_file}", flush=True)
            proc.terminate()
            proc.join(timeout=5)
            if proc.is_alive():
                proc.kill()
            return 0
        
        # <!--- Get result from queue --->
        if not result_queue.empty():
            worker_id, vfile, count, error = result_queue.get_nowait()
            if error:
                raise RuntimeError(f"Detection failed: {error}")
            return count if count is not None else 0
        else:
            return 0
            
    except Exception as e:
        print(f"[YOLO] Error in detect_cars: {e}", flush=True)
        if proc.is_alive():
            proc.terminate()
            proc.join(timeout=5)
        raise
    finally:
        result_queue.close()
        gc.collect()


def detect_cars_parallel(video_files, max_workers=None):
    """
    Process multiple videos in parallel using multiprocessing.
    Uses spawn method to avoid fork semaphore issues.
    Returns list of (car_count, error) tuples for each video.
    """
    if max_workers is None:
        max_workers = min(MAX_PARALLEL_WORKERS, len(video_files))
    
    print(f"[YOLO] Processing {len(video_files)} videos with {max_workers} parallel workers", flush=True)
    
    # Use spawn context to avoid fork issues
    ctx = mp.get_context('spawn')
    result_queue = ctx.Queue()
    
    results = [None] * len(video_files)
    errors = [None] * len(video_files)
    
    # Process videos in batches to limit concurrent memory usage
    active_procs = {}
    video_idx = 0
    completed = 0
    
    start_time = time.time()
    
    while completed < len(video_files):
        # Start new workers if we have capacity and videos remaining
        while len(active_procs) < max_workers and video_idx < len(video_files):
            video_file = video_files[video_idx]
            print(f"[YOLO] Starting worker {video_idx} for {video_file}", flush=True)
            
            proc = ctx.Process(
                target=_detect_cars_worker,
                args=(video_file, result_queue, video_idx)
            )
            proc.start()
            active_procs[video_idx] = proc
            video_idx += 1
        
        # Check for completed workers
        for idx in list(active_procs.keys()):
            proc = active_procs[idx]
            if not proc.is_alive():
                proc.join()
                del active_procs[idx]
        
        # Collect results from queue
        while not result_queue.empty():
            try:
                worker_id, vfile, count, error = result_queue.get_nowait()
                results[worker_id] = count if count is not None else 0
                errors[worker_id] = error
                completed += 1
                print(f"[YOLO] Worker {worker_id} completed: {count} vehicles (errors: {error})", flush=True)
            except:
                break
        
        # Small sleep to prevent busy-waiting
        if len(active_procs) > 0:
            time.sleep(0.1)
        
        # Timeout check (10 minutes total)
        if time.time() - start_time > 600:
            print("[YOLO] Overall timeout - terminating remaining workers", flush=True)
            for idx, proc in active_procs.items():
                if proc.is_alive():
                    proc.terminate()
                    results[idx] = 0
                    errors[idx] = "Timeout"
            break
    
    # Cleanup any remaining processes
    for proc in active_procs.values():
        if proc.is_alive():
            proc.terminate()
            proc.join(timeout=2)
    
    result_queue.close()
    gc.collect()
    
    elapsed = time.time() - start_time
    print(f"[YOLO] Parallel processing complete in {elapsed:.1f}s: {results}", flush=True)
    
    return results, errors


# For backwards compatibility - simple single-video function using subprocess
def detect_cars_safe(video_file):
    """
    Memory-safe single video detection.
    Alias for detect_cars that uses subprocess isolation.
    """
    return detect_cars(video_file)