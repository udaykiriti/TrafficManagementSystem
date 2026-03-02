# Windows Backend Setup Guide (Manual)

This document provides instructions for setting up and running the AI Traffic Management System backend on Windows without using Docker.

## Prerequisites

1.  **Python 3.10+**: Ensure Python is installed and added to your PATH.
2.  **G++ (MinGW/MSVC)**: Required for compiling the optimization core.
3.  **Git/Bash**: Recommended for running shell scripts (optional if using PowerShell).

## Installation Steps

### 1. Install Python Dependencies
Navigate to the root directory and install the required packages:
```powershell
pip install -r backend/requirements.txt
```

### 2. Download YOLO Model Weights
The system requires pre-trained YOLOv4 weights for vehicle detection. Download them into the `backend/` directory:
```powershell
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4.weights' -OutFile 'backend/yolov4.weights'"
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights' -OutFile 'backend/yolov4-tiny.weights'"
```

### 3. Compile the Optimization Engine
The Genetic Algorithm core is written in C++. Compile it using G++:
```powershell
g++ -std=c++17 -O3 -fopenmp -o backend/Algo1 backend/Algo.cpp
```
*Note: If OpenMP is not supported by your compiler, you can remove `-fopenmp`.*

## Running the Backend

Start the Flask application from the root directory:
```powershell
python backend/app.py
```
The backend will be available at:
- **API**: `http://localhost:5000`
- **Health Check**: `http://localhost:5000/health`

## Troubleshooting

- **503 Status Code**: If the `/health` endpoint returns 503, ensure that the weights and config files are present in the `backend/` directory.
- **C++ Compilation Errors**: Ensure you have a C++17 compliant compiler installed and configured.
