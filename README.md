# AI Traffic Management System
[![Frontend](https://img.shields.io/badge/frontend-React-61dafb?logo=react&logoColor=white)](#)
[![Backend](https://img.shields.io/badge/backend-Flask-000?logo=flask&logoColor=white)](#)
[![Vision](https://img.shields.io/badge/vision-YOLOv4-ff6f00)](#)
[![Optimizer](https://img.shields.io/badge/optimizer-C%2B%2B17-00599c?logo=c%2B%2B&logoColor=white)](#)
[![Container](https://img.shields.io/badge/infra-Docker-2496ed?logo=docker&logoColor=white)](#)

An AI based traffic management system with real-time monitoring

## Demo

![Traffic demo placeholder](https://dummyimage.com/960x540/0b1c2c/ffffff&text=Traffic+Flow+Demo+GIF+Placeholder)

## Overview

The Smart Adaptive Traffic Management System leverages AI and computer vision to optimize traffic flow at intersections. This system analyzes vehicle counts from video feeds, processes the data using machine learning models, and adjusts traffic signal timings to improve traffic flow.


## Features
- Vehicle Detection: Uses YOLOv4 for real-time vehicle detection from video feeds.
- Traffic Optimization: Employs a genetic algorithm to determine optimal green light times based on vehicle counts.
- Web Interface: Allows users to upload traffic videos, view processing results, and receive optimized traffic management recommendations.

## Starting Soon..

### Prerequisites

- Python 3.x
- Nodejs
- OpenCV
- YOLOv4 weights and configuration files
- Required Python packages (listed in requirements.txt)

## Setup

### Option 1: Docker (Recommended)

**Prerequisites:**
- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM for Docker [prefer more for some smoooth operatorr...]

**Quick Start:**

```bash
# Clone the repository
cd TrafficManagementSystem

# Download YOLO weights
cd backend && bash download.sh && cd ..

# Build and start with Docker Compose
docker-compose up -d

# Or use Makefile
make setup  # Download weights and build
make up     # Start services
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Health Check: http://localhost:5000/health

**Docker Commands:**
```bash
make help       # View all commands
make dev        # Development mode with hot reload
make logs       # View logs
make status     # Check container status
make down       # Stop services
make clean      # Clean up containers and volumes
```

See [Docker docs](docs/docker/docker-readme.md) for detailed Docker documentation.

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
bash download.sh  # Download YOLO weights
g++ -std=c++17 -O3 -fopenmp -o Algo1 Algo.cpp
python app.py
```

**Live camera mode (optional):**
```bash
# Provide 4 camera sources (RTSP/HTTP URLs or device indices) via flags or CAM_SOURCES env
python app.py --real --camera rtsp://cam1 --camera rtsp://cam2 --camera rtsp://cam3 --camera 0
# or
CAM_SOURCES=rtsp://cam1,rtsp://cam2,rtsp://cam3,0 python app.py --real
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

### Usage

Two modes:
- **Web upload**: Use the UI to upload 4 videos; backend optimizes timing.
- **Live cameras**: `python app.py --real` with 4 RTSP/HTTP/device sources.

Upload Traffic Videos: <br/>
Use the web interface to upload 4 traffic videos. The system will process the videos and display optimized green light times based on the analysis.

## Acknowledgments

- YOLOv4: For vehicle detection.
- OpenCV: For video processing.
- Genetic Algorithm: For optimizing traffic light timings.
- Algorithm implemented in cpp for performance

## Note :
- if possible create uploads && outputs dir in backend dir