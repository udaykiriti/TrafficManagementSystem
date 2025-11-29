#!/usr/bin/env python3
import os, sys, time, traceback
import cv2 as cv
import numpy as np

# import your detect_cars function if you still want peak-mean (optional)
from yolov4 import detect_cars

# python3 detect_run.py /path/to/video.mp4 [out_prefix]
VIDEO_PATH = sys.argv[1] if len(sys.argv) > 1 else None
OUT_PREFIX = sys.argv[2] if len(sys.argv) > 2 else "OutputVideo"
if not VIDEO_PATH:
    print("Usage: python3 detect_run.py /path/to/video.mp4 [out_prefix]")
    sys.exit(1)

CLASS_FILE = 'classes.txt'
CONFIG_FILE = 'yolov4-tiny.cfg'
WEIGHTS_FILE = 'yolov4-tiny.weights'
SCALE_FACTOR = 0.25
Conf_threshold = 0.6
NMS_threshold = 0.4

COLORS = [
    (0,255,0),(0,0,255),(255,0,0),
    (255,255,0),(255,0,255),(0,255,255)
]

# --- Simple centroid tracker (counts unique objects) ---
class CentroidTracker:
    def __init__(self, maxDisappeared=10, maxDistance=50):
        # next object ID to assign
        self.nextObjectID = 0
        # objectID -> centroid (x,y)
        self.objects = dict()
        # objectID -> number of consecutive frames it was missing
        self.disappeared = dict()
        self.maxDisappeared = maxDisappeared
        self.maxDistance = maxDistance
        # total unique count (incremented on register)
        self.total_count = 0

    def register(self, centroid):
        self.objects[self.nextObjectID] = centroid
        self.disappeared[self.nextObjectID] = 0
        self.total_count += 1
        self.nextObjectID += 1

    def deregister(self, objectID):
        if objectID in self.objects:
            del self.objects[objectID]
        if objectID in self.disappeared:
            del self.disappeared[objectID]

    def update(self, inputCentroids):
        """
        inputCentroids: list of (x, y) centroids detected in the current frame.
        Returns: current mapping objectID -> centroid
        """
        # No detections -> mark all current objects as disappeared
        if len(inputCentroids) == 0:
            for oid in list(self.disappeared.keys()):
                self.disappeared[oid] += 1
                if self.disappeared[oid] > self.maxDisappeared:
                    self.deregister(oid)
            return self.objects

        # First-time registration
        if len(self.objects) == 0:
            for c in inputCentroids:
                self.register(c)
            return self.objects

        # Build distance matrix between existing centroids and new centroids
        objectIDs = list(self.objects.keys())
        objectCentroids = np.array([self.objects[oid] for oid in objectIDs])
        inputCentroidsArr = np.array(inputCentroids)

        # compute pairwise Euclidean distances
        D = np.linalg.norm(objectCentroids[:, np.newaxis] - inputCentroidsArr[np.newaxis, :], axis=2)

        # greedy match: for small number of objects this is fine
        rows = D.min(axis=1).argsort()
        cols = D.argmin(axis=1)[rows]

        usedRows = set()
        usedCols = set()
        for row, col in zip(rows, cols):
            if row in usedRows or col in usedCols:
                continue
            if D[row, col] > self.maxDistance:
                continue
            oid = objectIDs[row]
            self.objects[oid] = tuple(inputCentroids[col])
            self.disappeared[oid] = 0
            usedRows.add(row)
            usedCols.add(col)

        # any unmatched existing objects -> increase disappeared counter
        unusedRows = set(range(0, D.shape[0])) - usedRows
        for row in unusedRows:
            oid = objectIDs[row]
            self.disappeared[oid] += 1
            if self.disappeared[oid] > self.maxDisappeared:
                self.deregister(oid)

        # any unmatched new centroids -> register as new objects
        unusedCols = set(range(0, D.shape[1])) - usedCols
        for col in unusedCols:
            self.register(tuple(inputCentroids[col]))

        return self.objects

# --- helpers ---
def force_cpu(net):
    try:
        net.setPreferableBackend(cv.dnn.DNN_BACKEND_DEFAULT)
        net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
        print("[INFO] Forcing DNN to use CPU backend/target")
    except Exception as e:
        print("[WARN] Could not set CPU backend/target:", e)


def safe_detect(model, frame, conf, nms):
    try:
        out = model.detect(frame, conf, nms)
    except Exception as e:
        print("[ERROR] model.detect exception:", e)
        return (), (), []
    if not out:
        return (), (), []
    try:
        classes, scores, boxes = out
    except Exception:
        return (), (), []
    if classes is None:
        return (), (), []
    return classes, scores, boxes

def draw_count_overlay(frame, text, position="top-left", font_scale=0.7, thickness=2):
    """Draw a filled rectangle + text for readability."""
    h, w = frame.shape[:2]
    font = cv.FONT_HERSHEY_SIMPLEX
    (text_w, text_h), baseline = cv.getTextSize(text, font, font_scale, thickness)
    pad_x = 10
    pad_y = 8
    rect_w = text_w + pad_x * 2
    rect_h = text_h + pad_y * 2

    if position == "top-left":
        x0, y0 = 10, 10
    elif position == "bottom-right":
        x0, y0 = w - rect_w - 10, h - rect_h - 10
    else:
        x0, y0 = 10, 10

    # filled background
    cv.rectangle(frame, (x0, y0), (x0 + rect_w, y0 + rect_h), (0, 0, 0), -1)
    # text (white)
    text_x = x0 + pad_x
    text_y = y0 + pad_y + text_h
    cv.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness, cv.LINE_AA)

# --- main processing ---
def main(video_path, out_prefix):
    try:
        print("=== START detect_run ===")
        if not os.path.exists(video_path):
            raise FileNotFoundError("Video not found: " + video_path)
        # make resource paths absolute to script directory
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        class_file = os.path.join(BASE_DIR, CLASS_FILE)
        cfg_file = os.path.join(BASE_DIR, CONFIG_FILE)
        weights_file = os.path.join(BASE_DIR, WEIGHTS_FILE)

        for req in (class_file, cfg_file, weights_file):
            if not os.path.exists(req):
                raise FileNotFoundError("Missing required file: " + req)
        with open(class_file,'r') as f:
            class_names = [c.strip() for c in f.readlines() if c.strip()]

        # Step 1: optionally run detect_cars to compute peak-mean (can skip if expensive)
        mean_peak_value = None
        try:
            print("[INFO] Running detect_cars (optional full-scan) ...")
            mean_peak_value = detect_cars(video_path)
            print(f"[INFO] detect_cars returned mean peak value: {mean_peak_value}")
        except Exception as e:
            print("[WARN] detect_cars raised an exception or was skipped:", e)
            mean_peak_value = None

        # --- Step 2: prepare model for per-frame annotation/writing ---
        net = cv.dnn.readNet(weights_file, cfg_file)
        force_cpu(net)
        model = cv.dnn_DetectionModel(net)
        model.setInputParams(size=(416,416), scale=1/255.0, swapRB=True)

        cap = cv.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError("Cannot open video: " + video_path)

        fw = int(cap.get(cv.CAP_PROP_FRAME_WIDTH) or 0)
        fh = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT) or 0)
        if fw == 0 or fh == 0:
            ret, tmp = cap.read()
            if not ret or tmp is None:
                raise RuntimeError("Cannot read a single frame to infer size")
            fh, fw = tmp.shape[:2]
            cap.set(cv.CAP_PROP_POS_FRAMES, 0)

        out_w = max(1, int(fw * SCALE_FACTOR))
        out_h = max(1, int(fh * SCALE_FACTOR))
        dim = (out_w, out_h)

        # ensure outputs directory exists
        outputs_dir = os.path.join(BASE_DIR, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)

        out_fname = os.path.join(outputs_dir, f"{out_prefix}.avi")
        print(f"[INFO] Video size: {fw}x{fh} -> {dim}. Output: {out_fname}")

        fourcc = cv.VideoWriter_fourcc('M','J','P','G')
        out = cv.VideoWriter(out_fname, fourcc, 30.0, dim)
        if not out.isOpened():
            print("[WARN] VideoWriter not opened. Output will not be saved to file.")

        saved_debug_frame = False
        start = time.time()
        frame_count = 0

        # vehicle classes set - lowercased; adjust to match your classes.txt
        vehicle_classes = {"car", "truck", "bus", "motorbike", "motorcycle", "bicycle", "van"}

        # create tracker: tune maxDisappeared and maxDistance for your video
        tracker = CentroidTracker(maxDisappeared=8, maxDistance=40)

        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                break
            frame_count += 1
            frame_small = cv.resize(frame, dim, interpolation=cv.INTER_AREA)

            classes, scores, boxes = safe_detect(model, frame_small, Conf_threshold, NMS_threshold)

            current_visible = 0
            inputCentroids = []

            if len(classes) > 0 and len(boxes) > 0:
                try:
                    for classid, score, box in zip(classes.flatten(), scores.flatten(), boxes):
                        cid = int(classid)
                        cname = class_names[cid] if cid < len(class_names) else str(cid)
                        color = COLORS[cid % len(COLORS)]
                        x,y,w,h = box
                        label = f"{cname}: {float(score):.2f}"
                        cv.rectangle(frame_small, (x,y),(x+w,y+h), color, 2)
                        cv.putText(frame_small, label, (x, y-6 if y-6>0 else y+12),
                                   cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                        # if this class is a vehicle, count and collect centroid
                        try:
                            if cname.lower() in vehicle_classes:
                                current_visible += 1
                                cx = int(x + w/2)
                                cy = int(y + h/2)
                                inputCentroids.append((cx, cy))
                        except Exception:
                            pass
                except Exception as e:
                    print("[WARN] drawing boxes error:", e)

            # update tracker with current centroids -> assigns IDs and increments total_count for new objects
            tracker.update(inputCentroids)

            # draw ids on frame for tracked objects
            for oid, centroid in tracker.objects.items():
                cx, cy = int(centroid[0]), int(centroid[1])
                cv.circle(frame_small, (cx, cy), 3, (0,255,255), -1)
                cv.putText(frame_small, f"ID:{oid}", (cx+6, cy-6), cv.FONT_HERSHEY_SIMPLEX, 0.45, (0,255,255), 1)

            # overlay current visible and total unique counts
            draw_count_overlay(frame_small, f"Vehicles: {current_visible}", position="top-left", font_scale=0.8, thickness=2)
            draw_count_overlay(frame_small, f"Total: {tracker.total_count}", position="bottom-right", font_scale=0.7, thickness=2)

            # optionally, also show mean peak returned earlier
            if mean_peak_value is not None:
                # small overlay near bottom-left to avoid overlap
                draw_count_overlay(frame_small, f"Peak-mean: {mean_peak_value:.2f}", position="top-left", font_scale=0.5, thickness=1)

            if not saved_debug_frame:
                try:
                    debug_jpg = os.path.join(outputs_dir, f"{out_prefix}_debug_frame.jpg")
                    cv.imwrite(debug_jpg, frame_small)
                    print("[DEBUG] Wrote", debug_jpg)
                    saved_debug_frame = True
                except Exception as e:
                    print("[WARN] could not write debug frame:", e)
            if out.isOpened():
                out.write(frame_small)
            # optional: stop early for faster debugging
            # if frame_count >= 500: break

        elapsed = time.time() - start
        fps = frame_count / elapsed if elapsed > 0 else 0.0
        print(f"[INFO] processed frames: {frame_count}, avg FPS: {fps:.2f}")
    except Exception as e:
        print("[FATAL]", e)
        traceback.print_exc()
    finally:
        try: out.release()
        except: pass
        try: cap.release()
        except: pass
        print("=== END detect_run ===")

if __name__ == '__main__':
    main(VIDEO_PATH, OUT_PREFIX)
