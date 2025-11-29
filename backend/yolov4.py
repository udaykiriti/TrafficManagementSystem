import cv2 as cv
import time
from collections import deque
import numpy as np
from scipy.signal import find_peaks

def detect_cars(video_file):
    # Set thresholds
    Conf_threshold = 0.4
    NMS_threshold = 0.4

    # Define colors for different classes (used if you want to save annotated frames)
    COLORS = [(0, 255, 0), (0, 0, 255), (255, 0, 0), 
              (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    # Load class names from file
    with open('classes.txt', 'r') as f:
        class_name = [cname.strip() for cname in f.readlines()]

    # Load the network
    net = cv.dnn.readNet('yolov4-tiny.weights', 'yolov4-tiny.cfg')

    # Use CPU backend and target to avoid CUDA errors
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_DEFAULT)
    net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

    # Initialize the detection model
    model = cv.dnn_DetectionModel(net)
    model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)

    # Open the video file
    cap = cv.VideoCapture(video_file)
    starting_time = time.time()
    frame_counter = 0

    # Deque to keep track of car counts with timestamps
    car_counts = deque()  # Store (timestamp, car_count) tuples

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_counter += 1

        # Perform detection
        classes, scores, boxes = model.detect(frame, Conf_threshold, NMS_threshold)

        # Count the number of cars detected
        car_count = 0
        for (classid, score, box) in zip(classes, scores, boxes):
            if class_name[classid] == "car":  # adjust if class name differs
                car_count += 1
                # You can add code to save annotated frames if needed here,
                # but no imshow or window calls.

        # Record the car count with the current timestamp
        current_time = time.time()
        car_counts.append((current_time, car_count))
        
        # Remove counts older than 30 seconds
        while car_counts and car_counts[0][0] < current_time - 30:
            car_counts.popleft()

        # Extract car counts
        car_count_values = [count for _, count in car_counts]

        # Find peaks in car count values
        peaks, _ = find_peaks(car_count_values)

        # Calculate mean of peak values
        mean_peak_value = np.mean([car_count_values[i] for i in peaks]) if len(peaks) > 0 else 0

    cap.release()

    # Return the mean peak value (average number of cars at peaks)
    return mean_peak_value

# Example usage outside Flask:
# mean_peak_value = detect_cars('output.avi')
# print(f'Mean Peak Number of Cars Detected: {mean_peak_value}')