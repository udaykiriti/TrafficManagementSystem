# Comprehensive Windows Backend Setup Guide

This guide provides a detailed, step-by-step walkthrough for setting up and running the AI Traffic Management System backend on a Windows machine without Docker.

---

## 1. Prerequisites & Environment Setup

### 1.1 Python Installation
1.  **Download**: Install Python 3.10 or newer from [python.org](https://www.python.org/).
2.  **PATH**: During installation, ensure the **"Add Python to PATH"** checkbox is selected.
3.  **Verify**: Open PowerShell or CMD and run:
    ```powershell
    python --version
    ```

### 1.2 C++ Build Tools (MinGW-w64)
The optimization core requires a C++ compiler with C++17 support.
1.  **Install**: We recommend [MinGW-w64](https://www.mingw-w64.org/) via [MSYS2](https://www.msys2.org/).
2.  **Configure**: After installation, add the `bin` folder (e.g., `C:\msys64\mingw64\bin`) to your system environment variables (PATH).
3.  **Verify**: Run:
    ```powershell
    g++ --version
    ```

---

## 2. Installation Steps

### 2.1 Clone Repository
```powershell
git clone https://github.com/udaykiriti/TrafficManagementSystem
cd TrafficManagementSystem
```

### 2.2 Install Python Dependencies
```powershell
# From the project root
pip install -r backend/requirements.txt
```

### 2.3 Download YOLOv4 Model Files
The computer vision component requires weight and configuration files. Execute the following PowerShell commands to download them into the `backend/` directory:

**YOLOv4 (Standard):**
```powershell
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4.weights' -OutFile 'backend/yolov4.weights'"
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg' -OutFile 'backend/yolov4.cfg'"
```

**YOLOv4-tiny (Optimized for speed):**
```powershell
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights' -OutFile 'backend/yolov4-tiny.weights'"
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg' -OutFile 'backend/yolov4-tiny.cfg'"
```

### 2.4 Compile the Genetic Algorithm Core
The optimization engine must be compiled into a binary named `Algo1`:
```powershell
# From the project root
g++ -std=c++17 -O3 -fopenmp -o backend/Algo1 backend/Algo.cpp
```
*Note: If your compiler does not support OpenMP, omit `-fopenmp`.*

---

## 3. Configuration Verification

Before running, ensure the following directory structure is present:
- `backend/Algo1` (The compiled binary)
- `backend/yolov4.weights`
- `backend/yolov4-tiny.weights`
- `backend/yolov4.cfg`
- `backend/yolov4-tiny.cfg`

---

## 4. Running the Backend

Launch the Flask server from the root directory:
```powershell
python backend/app.py
```

### Accessing the API
- **Base URL**: `http://localhost:5000`
- **Health Check**: `http://localhost:5000/health`

A healthy response should look like this:
```json
{
  "components": {
    "api": "ok",
    "ga_binary": "ok",
    "yolo_config": "ok",
    "yolo_weights": "ok"
  },
  "status": "healthy",
  "timestamp": "..."
}
```

---

## 5. Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **"g++" not recognized** | Add your MinGW/MSYS2 bin folder to the System PATH. |
| **"python" not recognized** | Ensure Python is added to PATH or use `py` or `python3`. |
| **503 Service Unavailable** | Check the `/health` endpoint. If any component is "missing", verify the filenames in the `backend/` folder. |
| **Permission Denied** | Run PowerShell as Administrator for weight downloads or dependency installation. |
