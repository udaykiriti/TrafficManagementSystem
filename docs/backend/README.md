# Backend Documentation

## Overview

The backend is the core processing unit of the Traffic Management System. It orchestrates video ingestion, object detection (YOLOv4), genetic optimization (C++), and result serving via a Flask REST API.

## Directory Structure

- **app.py**: The entry point for the Flask application.
- **Algo.cpp**: The C++ implementation of the Genetic Algorithm for signal timing optimization.
- **yolov4.py**: Python wrapper for the Darknet YOLOv4 object detection model.
- **rl_agent.py**: Reinforcement learning module for refining optimized timings.
- **uploads/**: Temporary storage for incoming video files.
- **outputs/**: Storage for processed video results.
- **data/**: CSV logs for system analytics and performance tracking.

## Installation and Setup

### Prerequisites
- Python 3.10+
- GCC Compiler (with OpenMP support)
- YOLOv4 Weights (downloaded via `download.sh`)

### Manual Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Compile the C++ optimizer:
   ```bash
   g++ -std=c++17 -O3 -fopenmp -o Algo1 Algo.cpp
   ```
4. Download YOLO weights:
   ```bash
   bash download.sh
   ```
5. Start the server:
   ```bash
   python app.py
   ```

## API Reference

### POST /upload
Accepts four video files representing the four lanes of an intersection.
- **Payload:** `multipart/form-data` with key `videos` containing 4 files.
- **Response:** JSON object containing optimal green light durations for each lane.

### GET /health
Checks the operational status of the system.
- **Response:** 200 OK if all components (weights, binary) are present.

### GET /stats
Retrieves aggregated system performance metrics from the CSV logs.

## Core Components

### Object Detection
The system uses YOLOv4 (You Only Look Once) to detect vehicles in video frames. It processes frames in parallel to maximize throughput.

### Genetic Optimization
A C++ executable (`Algo1`) receives vehicle counts and performs a genetic algorithm simulation. It evolves population parameters to minimize total vehicle wait time at the intersection.

### Reinforcement Learning
An optional RL agent refines the output of the genetic algorithm based on historical data and time-of-day patterns to ensure long-term adaptability.
