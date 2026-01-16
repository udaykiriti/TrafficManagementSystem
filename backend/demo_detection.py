#!/usr/bin/env python3

import cv2 as cv
import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLASS_FILE = os.path.join(BASE_DIR, 'classes.txt')
CONFIG_FILE = os.path.join(BASE_DIR, 'yolov4-tiny.cfg')
WEIGHTS_FILE = os.path.join(BASE_DIR, 'yolov4-tiny.weights')

CONF_THRESHOLD = 0.2
NMS_THRESHOLD = 0.4
INPUT_SIZE = 608 
VEHICLE_CLASSES = {'car', 'motorbike', 'bus', 'truck', 'bicycle'}

COLORS = {
    'car': (0, 255, 0),       # Green
    'truck': (0, 0, 255),     # Red
    'bus': (255, 0, 0),       # Blue
    'motorbike': (0, 255, 255), # Yellow
    'bicycle': (255, 0, 255), # Magenta
}


def create_model():
    """Initialize YOLO model."""
    if not os.path.exists(WEIGHTS_FILE):
        raise FileNotFoundError(f"Missing weights: {WEIGHTS_FILE}")
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Missing config: {CONFIG_FILE}")
    
    net = cv.dnn.readNet(WEIGHTS_FILE, CONFIG_FILE)
    
    # Try CUDA, fallback to CPU
    try:
        if cv.cuda.getCudaEnabledDeviceCount() > 0:
            net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
            net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)
            print("[YOLO] Using CUDA GPU acceleration")
        else:
            raise Exception("No CUDA")
    except:
        net.setPreferableBackend(cv.dnn.DNN_BACKEND_DEFAULT)
        net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
        print("[YOLO] Using CPU backend")
    
    model = cv.dnn_DetectionModel(net)
    model.setInputParams(size=(INPUT_SIZE, INPUT_SIZE), scale=1/255, swapRB=True)
    
    with open(CLASS_FILE, 'r') as f:
        class_names = [c.strip() for c in f.readlines()]
    
    return model, class_names


def process_video(input_path, output_path):
    """Process video and create output with detections."""
    
    print(f"[Demo] Loading model...")
    model, class_names = create_model()
    
    print(f"[Demo] Opening video: {input_path}")
    cap = cv.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {input_path}")
    
    # Get video properties
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    
    print(f"[Demo] Video: {width}x{height} @ {fps:.1f} FPS, {total_frames} frames")
    
    # Output video writer
    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    out = cv.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    start_time = time.time()
    total_vehicles = 0
    max_vehicles = 0
    
    print(f"[Demo] Processing frames...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Detect objects
        classes, scores, boxes = model.detect(frame, CONF_THRESHOLD, NMS_THRESHOLD)
        
        # Count and draw vehicles
        vehicle_count = 0
        for classid, score, box in zip(classes, scores, boxes):
            class_name = class_names[classid]
            if class_name in VEHICLE_CLASSES:
                vehicle_count += 1
                color = COLORS.get(class_name, (0, 255, 0))
                
                # Draw bounding box
                x, y, w, h = box
                cv.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                
                # Draw label
                label = f"{class_name}: {score:.2f}"
                label_size, _ = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv.rectangle(frame, (x, y - 20), (x + label_size[0], y), color, -1)
                cv.putText(frame, label, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        total_vehicles += vehicle_count
        max_vehicles = max(max_vehicles, vehicle_count)
        
        # Draw stats overlay
        elapsed = time.time() - start_time
        current_fps = frame_count / elapsed if elapsed > 0 else 0
        
        # Semi-transparent overlay
        overlay = frame.copy()
        cv.rectangle(overlay, (10, 10), (300, 120), (0, 0, 0), -1)
        frame = cv.addWeighted(overlay, 0.6, frame, 0.4, 0)
        
        cv.putText(frame, f"Vehicles in frame: {vehicle_count}", (20, 40), 
                   cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv.putText(frame, f"Max vehicles: {max_vehicles}", (20, 70), 
                   cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv.putText(frame, f"FPS: {current_fps:.1f} | Frame: {frame_count}/{total_frames}", (20, 100), 
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        out.write(frame)
        
        # Progress update
        if frame_count % 50 == 0:
            progress = (frame_count / total_frames) * 100
            print(f"[Demo] Progress: {progress:.1f}% ({frame_count}/{total_frames}) - {current_fps:.1f} FPS")
    
    cap.release()
    out.release()
    
    elapsed = time.time() - start_time
    avg_vehicles = total_vehicles / frame_count if frame_count > 0 else 0
    
    print(f"\n[Demo] Complete!")
    print(f"[Demo] Output saved to: {output_path}")
    print(f"[Demo] Stats:")
    print(f"       - Total frames: {frame_count}")
    print(f"       - Processing time: {elapsed:.1f}s")
    print(f"       - Average FPS: {frame_count/elapsed:.1f}")
    print(f"       - Max vehicles in frame: {max_vehicles}")
    print(f"       - Average vehicles per frame: {avg_vehicles:.1f}")
    
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python demo_detection.py <input_video> [output_video]")
        print("\nExample:")
        print("  python demo_detection.py uploads/video_0.mp4 outputs/demo_output.mp4")
        sys.exit(1)
    
    input_video = sys.argv[1]
    
    if not os.path.exists(input_video):
        print(f"Error: Input video not found: {input_video}")
        sys.exit(1)
    
    # Default output path
    if len(sys.argv) >= 3:
        output_video = sys.argv[2]
    else:
        os.makedirs('outputs', exist_ok=True)
        base_name = os.path.splitext(os.path.basename(input_video))[0]
        output_video = f"outputs/{base_name}_detection.mp4"
    
    process_video(input_video, output_video)
