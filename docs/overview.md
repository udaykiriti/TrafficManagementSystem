# Project Overview

The **AI Traffic Management System** is an intelligent urban traffic optimization platform designed to dynamically control traffic signals using real-time vehicle density analysis.

The system integrates:

- Computer Vision (YOLO-based vehicle detection)
- Genetic Algorithms (signal timing optimization)
- Reinforcement Learning (adaptive refinement)

Its primary objective is to minimize overall vehicle waiting time and improve traffic flow efficiency across multi-lane intersections.

---

# System Architecture

The system follows a modular, loosely-coupled architecture composed of four core components:

---

## 1. Frontend (User Interface)

- **Framework:** React.js
- **Purpose:** Interactive monitoring and control dashboard

### Responsibilities
- Uploads video feeds for traffic simulation
- Displays real-time vehicle statistics
- Visualizes optimized traffic signal durations
- Shows analytics and historical data trends

---

## 2. Backend API (Orchestration Layer)

- **Framework:** Flask (Python)
- **Role:** Central coordination engine

### Responsibilities
- Handles video ingestion and validation
- Triggers vehicle detection pipeline
- Invokes the C++ optimization engine
- Applies Reinforcement Learning refinement
- Manages logging, analytics, and persistence
- Returns structured JSON responses to frontend

---

## 3. Vision Engine (Perception Layer)

- **Model:** YOLOv4 / YOLOv4-tiny
- **Library:** OpenCV (DNN module)

### Responsibilities
- Detects vehicles across four lanes simultaneously
- Counts vehicle instances per frame
- Computes lane-wise vehicle density vectors

### Output
A structured vehicle density vector:

```
[density_lane_1, density_lane_2, density_lane_3, density_lane_4]
```

This vector is passed to the optimization core.

---

## 4. Optimization Core (Decision Engine)

- **Language:** C++17
- **Algorithm:** Genetic Algorithm (GA)
- **Executable:** `Algo1`

### Responsibilities
- Simulates thousands of traffic signal timing combinations
- Evolves candidate solutions across generations
- Minimizes total vehicle waiting time
- Outputs the optimal green-light duration per lane

### Reinforcement Learning Refinement
- Implemented in Python
- Adjusts GA results using:
  - Historical optimization logs
  - Time-of-day patterns
  - Traffic behavior trends

---

# Data Flow

The system follows this execution pipeline:

### Step 1: Input
User provides:
- 4 uploaded video files (one per lane), OR
- 4 live RTSP camera streams

---

### Step 2: Processing

1. **Detection Phase**
   - YOLO model detects and counts vehicles per lane.

2. **Optimization Phase**
   - Vehicle counts are passed to the C++ executable (`Algo1`).
   - The Genetic Algorithm evolves signal timing configurations.

3. **Refinement Phase**
   - The best GA candidate is adjusted by the RL agent.

---

### Step 3: Output

The backend returns a structured JSON response:

```json
{
  "lane_1": 32,
  "lane_2": 18,
  "lane_3": 25,
  "lane_4": 15
}
```

These values represent optimized green-light durations (in seconds).

---

# Project Structure

| Path | Description |
|------|------------|
| `frontend/` | React dashboard source code |
| `backend/` | Flask API, AI models, and orchestration logic |
| `backend/Algo.cpp` | Genetic Algorithm implementation (C++) |
| `backend/app.py` | Flask application entry point |
| `backend/yolov4.py` | Vehicle detection logic |
| `backend/data/` | Generated logs and analytics |
| `docs/` | Project documentation |
| `Makefile` | Operational commands and automation |

---

# Execution Modes

## 1. API Mode (Server Mode)

Standard web interaction mode.

### Run via Docker
```bash
make up
```

### Run manually
```bash
python app.py
```

### Access
http://localhost:5000

---

## 2. Live Camera Mode (Edge Mode)

Headless execution for real-time traffic streams.

```bash
python app.py --real --camera <url1> <url2> <url3> <url4>
```

### Output
- Prints optimized signal durations to console
- Logs results to CSV files

---

# Analytics & Logging

The system persists performance metrics inside:

```
backend/data/
```

### Files

- `results.csv`  
  Logs each optimization run (input densities vs. output timings)

- `analytics.csv`  
  Stores aggregated system performance metrics for long-term analysis

> [!IMPORTANT]
> Analytics files grow over time. Consider periodic cleanup or database migration for production deployments.

---

# Design Principles

- Modular and loosely coupled architecture
- Hybrid optimization (GA + RL)
- Deterministic core with adaptive refinement
- Scalable for multi-intersection deployment
- Container-ready (Docker support)

---

# Future Enhancements

- Multi-intersection coordination
- Edge device GPU acceleration
- Distributed optimization engine
- Real-time traffic prediction models
- WebSocket-based live dashboard updates
