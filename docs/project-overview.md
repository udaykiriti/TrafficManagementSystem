# Project Overview

Dynamic Traffic Management System with computer vision, genetic optimization, and RL refinement.

## Architecture
- **Frontend (React)**: Uploads four lane videos, shows results, and can display stats.
- **Backend (Flask)**: Handles uploads, detects vehicles via YOLOv4(-tiny), calls C++ genetic optimizer (`Algo1`), applies RL post-processing (`rl_agent.py`), logs CSV analytics, and exposes `/health` and `/stats`.
- **C++ Optimizer**: `backend/Algo1` (built from `Algo.cpp`) computes green times using GA.
- **YOLO Models**: Weights/config in `backend/` (`yolov4-tiny` by default; full YOLOv4 optional).
- **Data/Logs**: CSV logs in `backend/data/` (`results.csv`, `analytics.csv`), uploads in `backend/uploads`, outputs in `backend/outputs`.
- **Docs**: Docker guides in `docs/docker/`; backend usage in `docs/BACKEND_USAGE.md`.

## Run Modes
- **API mode (default)**: `cd backend && python app.py`
  - `POST /upload` expects exactly 4 videos (`videos` form field). Enforces extensions, MIME, and per-file size via `MAX_UPLOAD_SIZE_MB` (default 200 MB) and Flask `MAX_CONTENT_LENGTH`.
  - `GET /health`, `GET /stats`.
  - Rate limiting: `RATE_LIMIT_REQUESTS` per `RATE_LIMIT_WINDOW` (defaults 10 per 60s).
- **Live camera mode**: `python app.py --real --camera <cam1> --camera <cam2> --camera <cam3> --camera <cam4> [--verbose]`
  - Alternatively set `CAM_SOURCES=cam1,cam2,cam3,cam4`.
  - Runs detection + optimizer + RL once and prints results (no API server).

## Setup Checklist
1) `pip install -r backend/requirements.txt`
2) `bash backend/download.sh` to fetch weights/config
3) `g++ -std=c++17 -O3 -fopenmp -o backend/Algo1 backend/Algo.cpp`
4) Ensure writable dirs: `backend/uploads`, `backend/outputs`, `backend/data`
5) (Frontend) `cd frontend && npm install && npm start`

## Environment Variables (common)
- `MAX_UPLOAD_SIZE_MB` — per-file upload cap (default 200)
- `DEBUG_UPLOAD` — `1` to include debug fields in responses
- `RATE_LIMIT_REQUESTS`, `RATE_LIMIT_WINDOW` — rate limits
- `CAM_SOURCES` — comma-list for live mode
- Frontend: `REACT_APP_API_URL`, `REACT_APP_ENVIRONMENT`

## Key Files
- `backend/app.py` — Flask API + CLI switch for live mode
- `backend/yolov4.py` — detection with multiprocessing
- `backend/rl_agent.py` — time-of-day-aware RL refinement
- `backend/csv_logger.py` — CSV logging & summaries
- `backend/stream_ingest.py` — live camera helper
- `backend/Algo.cpp` / `Algo1` — GA optimizer
- `frontend/src/App.js` — main UI
- `frontend/src/logo.svg`, `public/logo*.png` — branding

## Docker (optional)
See `docs/docker/README.md` and `docs/docker/QUICK_START.md` for Compose-based build/run, dev mode, and troubleshooting.
