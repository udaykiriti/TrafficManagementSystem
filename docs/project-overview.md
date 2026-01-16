# Project Overview

The **AI Traffic Management System** is a sophisticated solution designed to optimize urban traffic flow through intelligent signal control. It integrates computer vision, genetic algorithms, and reinforcement learning to dynamically adjust traffic lights based on real-time demand.

---

##  System Architecture

The system operates on a modular architecture comprising four main components:

### 1. Frontend (User Interface)
- **Framework:** React.js
- **Role:** serves as the control dashboard.
- **Capabilities:**
  - Uploads video feeds for simulation.
  - Displays real-time traffic statistics.
  - visualizes optimized signal timings.

### 2. Backend API (Orchestrator)
- **Framework:** Flask (Python)
- **Role:** Acts as the central nervous system.
- **Responsibilities:**
  - Handles video ingestion and validation.
  - Triggers the computer vision pipeline.
  - Invokes the C++ optimization engine.
  - Applies Reinforcement Learning (RL) post-processing.
  - Maintains system logs and analytics.

### 3. Vision Engine (Perception)
- **Core:** YOLOv4 / YOLOv4-tiny
- **Library:** OpenCV (DNN module)
- **Role:** Detects and counts vehicles across four distinct lanes simultaneously.
- **Output:** Vehicle density vectors used as input for the optimizer.

### 4. Optimization Core (Decision Making)
- **Language:** C++17
- **Algorithm:** Genetic Algorithm (GA)
- **Role:** Simulates thousands of potential signal timing configurations to find the most efficient schedule that minimizes total waiting time.
- **Refinement:** An RL Agent (Python) further refines these times based on historical patterns and time-of-day logic.

---

##  Data Flow

1.  **Input:** User uploads 4 video files (one per lane) OR connects 4 live RTSP streams.
2.  **Processing:**
    *   **Detection:** Backend counts cars in each lane using YOLO.
    *   **Optimization:** Counts are sent to the C++ executable (`Algo1`).
    *   **Evolution:** The GA evolves a population of signal timings.
    *   **Refinement:** The best candidate is adjusted by the RL agent.
3.  **Output:** JSON response containing the optimal green light duration for each lane, returned to the frontend.

---

##  Key Directories & Files

| Path | Description |
| :--- | :--- |
| `frontend/` | React application source code. |
| `backend/` | Flask application, AI models, and scripts. |
| `backend/Algo.cpp` | Source code for the Genetic Algorithm. |
| `backend/app.py` | Main entry point for the API server. |
| `backend/yolov4.py` | Object detection logic. |
| `docs/` | Comprehensive documentation. |
| `Makefile` | operational commands. |

---

##  Execution Modes

### API Mode (Server)
The standard mode for web interaction.
- **Command:** `make up` (Docker) or `python app.py` (Manual)
- **Access:** http://localhost:5000

### Live Camera Mode (Edge)
A headless mode for processing live streams directly.
- **Command:** `python app.py --real --camera <url1> ...`
- **Output:** Prints optimized timings to the console.

---

##  Analytics
The system persists performance data to CSV files in `backend/data/`:
- `results.csv`: Log of every optimization run (inputs vs. outputs).
- `analytics.csv`: Aggregated system performance metrics.