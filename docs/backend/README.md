# Backend Documentation

---

# Overview

The backend serves as the central processing engine of the AI Traffic Management System.

It is responsible for:

- Video ingestion and validation
- Vehicle detection using YOLOv4
- Traffic signal optimization via a C++ Genetic Algorithm
- Reinforcement Learning refinement
- Serving results through a RESTful Flask API
- Persisting logs and analytics data

The backend coordinates communication between the perception layer (vision) and the decision layer (optimization).

---

# Directory Structure

```
backend/
│
├── app.py              # Flask application entry point
├── Algo.cpp            # Genetic Algorithm implementation (C++)
├── Algo                # Compiled optimizer binary
├── yolov4.py           # YOLO detection wrapper
├── rl_agent.py         # Reinforcement Learning refinement module
├── uploads/            # Temporary uploaded videos
├── outputs/            # Processed results
├── data/               # CSV analytics and logs
├── requirements.txt    # Python dependencies
└── download.sh         # YOLO weight downloader
```

---

# Installation and Setup

---

## Prerequisites

- Python 3.10+
- GCC compiler with OpenMP support
- YOLOv4 weight files

> [!IMPORTANT]
> Ensure GCC supports `-fopenmp` for parallel optimization execution.

---

## Manual Setup

Navigate to backend directory:

```bash
cd backend
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Compile the C++ Genetic Algorithm:

```bash
g++ -std=c++17 -O3 -Wall -Wextra -fopenmp -o Algo Algo.cpp
```

Download YOLO weights:

```bash
bash download.sh
```

Start the Flask server:

```bash
python app.py
```

Backend will be accessible at:

```
http://localhost:5000
```

---

# API Reference

---

## POST `/upload`

Uploads four traffic lane videos for optimization.

### Request

- Content-Type: `multipart/form-data`
- Key: `videos`
- Expected: 4 video files (one per lane)

### Response (JSON)

```json
{
  "lane_1": 30,
  "lane_2": 20,
  "lane_3": 25,
  "lane_4": 15
}
```

Each value represents optimized green-light duration (in seconds).

---

## GET `/health`

Checks system readiness and operational status.

### Response

- `200 OK` → Backend is alive and dependencies are available
- Confirms:
  - YOLO weights exist
  - C++ optimizer binary exists
  - Flask server running

> [!NOTE]
> This endpoint is primarily used to verify whether the backend service is alive and ready to process requests.

---

## GET `/stats`

Returns aggregated analytics data from CSV logs.

### Response

- Aggregated performance metrics
- Historical optimization statistics
- System efficiency summaries

---

# Core Components

---

## 1. Object Detection (Perception Layer)

- Model: YOLOv4
- Framework: OpenCV (DNN)

### Responsibilities

- Process frames from uploaded videos
- Detect and classify vehicles
- Count vehicles per lane
- Generate density vector for optimization

Parallel frame processing is used where possible to maximize throughput.

---

## 2. Genetic Optimization (Decision Engine)

- Language: C++17
- Executable: `Algo`
- Parallelization: OpenMP

The compiled C++ binary receives vehicle density values as input and performs a Genetic Algorithm simulation.

### Why C++?

- Faster execution compared to interpreted Python
- Saves Compiled time.[cuz , here the main thing is performance]
- Reduced computation time for large population simulations
- Efficient multi-threaded execution using OpenMP
- Direct CPU-level optimization

The optimizer:

- Evolves candidate signal timing configurations
- Minimizes total vehicle waiting time
- Returns the best candidate solution

> [!IMPORTANT]
> The binary executable is used to reduce computation overhead and improve optimization speed.

---

## 3. Reinforcement Learning Refinement

The RL module (`rl_agent.py`) refines the GA output.

### Purpose

- Prevent starvation of low-density lanes
- Adjust timings based on:
  - Historical optimization logs
  - Time-of-day patterns
  - Traffic distribution trends

The RL agent ensures fairness and long-term adaptability.

---

# Data Persistence

Optimization results are stored inside:

```
backend/data/
```

### Files

- `results.csv` → Logs individual optimization runs
- `analytics.csv` → Aggregated performance metrics

> [!IMPORTANT]
> For production-scale deployment, consider replacing CSV storage with a database system.

---

# Performance Notes

- C++ optimizer uses multi-threading via OpenMP.
- YOLO inference may benefit from GPU acceleration.
- Large video uploads may impact memory usage.
- Consider asynchronous processing for scalability.

---

# Known Limitations

- Live camera (RTSP) integration is currently under development.
- GPU acceleration support depends on deployment configuration.
- CSV-based logging is not suitable for distributed scaling.

> [!NOTE]
> Live camera mode algorithm improvements are actively being developed.

---

# Future Improvements

- Async job queue (Celery / Redis)
- GPU-accelerated YOLO inference
- Database-backed analytics
- Distributed optimization across multiple intersections
- Advanced RL policy learning
