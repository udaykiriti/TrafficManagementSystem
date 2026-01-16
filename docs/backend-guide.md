# Backend Technical Guide

This document provides a deep dive into the backend architecture, configuration, and manual operation.

---

## 🛠️ Prerequisites (Manual Setup)

If you are not using Docker, ensure your environment meets these requirements:

1.  **Python 3.10+**: with dependencies installed via `pip install -r backend/requirements.txt`.
2.  **GCC Compiler**: Support for C++17 and OpenMP (`sudo apt install build-essential`).
3.  **YOLO Weights**: Downloaded to `backend/` using `bash backend/download.sh`.
4.  **Directory Structure**: The following folders must exist and be writable:
    *   `backend/uploads/`
    *   `backend/outputs/`
    *   `backend/data/`

---

## 🖥️ Server API Mode

The Flask application acts as a RESTful API.

### Starting the Server
```bash
cd backend
python app.py
```

### Key Endpoints

| Method | Endpoint | Description | 
| :--- | :--- | :--- | 
| `POST` | `/upload` | **Main Endpoint.** Accepts 4 video files (`videos` key). Returns optimized timings. | 
| `GET` | `/health` | Checks if weights exist and the binary is compiled. | 
| `GET` | `/stats` | Returns aggregated analytics from CSV logs. | 

### Configuration (Environment Variables)

| Variable | Default | Description | 
| :--- | :--- | :--- | 
| `MAX_UPLOAD_SIZE_MB` | `200` | Max size per uploaded video file (MB). | 
| `RATE_LIMIT_REQUESTS`| `10` | Max requests allowed per IP. | 
| `RATE_LIMIT_WINDOW` | `60` | Time window for rate limiting (seconds). | 
| `DEBUG_UPLOAD` | `1` | Enable verbose debug output in API responses. | 

---

## 🎥 Live Camera Mode (Edge Deployment)

This mode bypasses the Flask server and processes video streams directly. Ideal for deployment on edge devices like NVIDIA Jetson.

### Command Syntax
```bash
python app.py --real --camera <source1> --camera <source2> --camera <source3> --camera <source4>
```

### Sources
- **RTSP:** `rtsp://user:pass@ip:port/stream`
- **HTTP:** `http://ip:port/video`
- **USB/Local:** `0`, `1` (Device Index)

### Example
```bash
# Using Environment Variable
export CAM_SOURCES="rtsp://cam1,rtsp://cam2,rtsp://cam3,0"
python app.py --real
```

---

## 🧠 The Genetic Algorithm (C++)

The core optimization logic resides in `backend/Algo.cpp`.

### Compilation
The binary must be compiled with OpenMP support for parallel processing.
```bash
g++ -std=c++17 -O3 -fopenmp -o backend/Algo1 backend/Algo.cpp
```

### Input/Output Interface
- **Input:** Space-separated integers representing vehicle counts for 4 lanes.
- **Output:** Space-separated integers representing green light duration (in seconds) for each lane.

---

## 🧪 Testing & Validation

### Health Check
```bash
curl http://localhost:5000/health
```

### Upload Test
```bash
curl -F "videos=@lane1.mp4" \
     -F "videos=@lane2.mp4" \
     -F "videos=@lane3.mp4" \
     -F "videos=@lane4.mp4" \
     http://localhost:5000/upload
```

---

## ⚠️ Troubleshooting

**Issue: `Algo1` not found**
*   **Fix:** Run the compilation command listed above.

**Issue: YOLO weights missing**
*   **Fix:** Run `bash backend/download.sh`.

**Issue: 413 Request Entity Too Large**
*   **Fix:** Increase `MAX_UPLOAD_SIZE_MB` in `.env` or check Flask's `MAX_CONTENT_LENGTH`.