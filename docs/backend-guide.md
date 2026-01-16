# Backend Usage Guide

This covers running the Flask API and the live camera helper without touching the Docker stack.

## Prerequisites
- Python 3.9+ with `pip install -r backend/requirements.txt`
- YOLO weights/config in `backend/` (run `bash backend/download.sh`)
- C++ optimizer compiled: `g++ -std=c++17 -O3 -fopenmp -o backend/Algo1 backend/Algo.cpp`
- Ensure `backend/uploads`, `backend/outputs`, and `backend/data` are writable

## Modes

### 1) API mode (default)
```bash
cd backend
python app.py
```
Endpoints:
- `POST /upload` — multipart form with exactly 4 files under key `videos`
  - Allowed extensions: .mp4 .avi .mov .mkv .webm .flv .wmv
  - MIME must start with `video/`
  - Max per-file size: `MAX_UPLOAD_SIZE_MB` (default 200 MB) env; total capped by Flask `MAX_CONTENT_LENGTH`
- `GET /stats` — summary of CSV logs
- `GET /health` — component readiness (weights/binary presence)

Rate limiting (per-IP): `RATE_LIMIT_REQUESTS` (default 10) per `RATE_LIMIT_WINDOW` seconds (default 60).
CSV logs are written to `backend/data/` (`results.csv`, `analytics.csv`).

### 2) Live camera mode
Runs detection on 4 live streams and prints optimizer + RL output (does not start the API server).
```bash
cd backend
python app.py --real --camera rtsp://cam1 --camera rtsp://cam2 --camera rtsp://cam3 --camera 0
# or via env
CAM_SOURCES=rtsp://cam1,rtsp://cam2,rtsp://cam3,0 python app.py --real
```
Requirements: four accessible sources (RTSP/HTTP URLs or device indices). Add `--verbose` to log optimizer output.

## Environment Variables
- `MAX_UPLOAD_SIZE_MB` — per-file size limit in MB (default 200)
- `DEBUG_UPLOAD` — when `1`, includes extra debug info in responses (default 1)
- `RATE_LIMIT_REQUESTS` / `RATE_LIMIT_WINDOW` — rate limit settings
- `CAM_SOURCES` — comma-separated camera list for `--real` mode

## Quick Testing
```bash
# With local sample videos
curl -F "videos=@uploads/video_0.mp4" \
     -F "videos=@uploads/video_1.mp4" \
     -F "videos=@uploads/video_2.mp4" \
     -F "videos=@uploads/video_3.mp4" \
     http://localhost:5000/upload

curl http://localhost:5000/health
curl http://localhost:5000/stats
```

## Troubleshooting
- Missing weights/config: re-run `bash backend/download.sh`
- Optimizer missing: recompile `Algo1`
- Permissions: ensure `backend/uploads` and `backend/data` are writable
- Oversized/invalid uploads: check extensions/MIME and `MAX_UPLOAD_SIZE_MB`
