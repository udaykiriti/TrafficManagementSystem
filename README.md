#                   AI Traffic Management System

[![Frontend](https://img.shields.io/badge/frontend-React-61dafb?logo=react&logoColor=white)](https://reactjs.org/)
[![Backend](https://img.shields.io/badge/backend-Flask-000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Vision](https://img.shields.io/badge/vision-YOLOv4-ff6f00)](https://github.com/AlexeyAB/darknet)
[![Optimizer](https://img.shields.io/badge/optimizer-C%2B%2B17-00599c?logo=c%2B%2B&logoColor=white)](https://isocpp.org/)
[![Container](https://img.shields.io/badge/infra-Docker-2496ed?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

The AI Traffic Management System is an end-to-end solution designed to reduce urban congestion by dynamically adjusting traffic signal timings based on real-time vehicle density. The system utilizes computer vision for vehicle detection and a high-performance genetic algorithm to optimize traffic flow at four-way intersections.

### Core Workflow
1. **Data Ingestion:** The system receives video feeds from four cameras (one per lane) or processes uploaded video files.
2. **Vehicle Detection:** YOLOv4-tiny identifies and counts vehicles in each frame, categorizing them to estimate lane pressure.
3. **Traffic Optimization:** The vehicle counts are passed to a Genetic Algorithm implemented in C++17. This algorithm simulates various timing scenarios to find the configuration that minimizes total waiting time.
4. **Signal Implementation:** The optimized green-light durations are returned to the dashboard for monitoring and implementation.

---

## Technical Features

- **Object Detection:** Implements YOLOv4 (You Only Look Once) via OpenCV's DNN module for high-speed vehicle identification.
- **Optimization Engine:** Uses a Genetic Algorithm (GA) written in C++ for performance. The GA evolves a population of signal timing solutions to find a near-optimal balance for the intersection.
- **Real-time Analytics:** A React-based web interface provides live visualizations of traffic density and system performance.
- **Flexible Deployment:** Support for Docker and Docker Compose ensures the system can be deployed on edge devices or central servers with minimal configuration.
- **RTSP Support:** Capable of streaming directly from IP cameras for production environments.

---

## Technology Stack

| Layer | Technologies |
|:---|:---|
| **Frontend** | React |
| **Backend API** | Flask (Python 3.10) |
| **Vision Processing** | OpenCV, Darknet (YOLOv4) |
| **Optimization Core** | C++17, OpenMP [parallel..] |
| **Infrastructure** | Docker, Docker Compose, Nginx |

---

## Installation and Setup

> [!IMPORTANT]
> **Prerequisites**
> Make sure your system has
> - Docker Engine 20.10 or higher  
> - Docker Compose 2.0 or higher  
> - Minimum 8GB RAM recommended for AI model inference


### Automated Setup (Recommended)
The project includes a Makefile to automate common deployment tasks. For detailed information regarding containerization and orchestration, please refer to the [Docker Documentation](docs/docker/README.md).

1. **Clone the repository**
   ```bash
   git clone https://github.com/udaykiriti/TrafficManagementSystem
   cd TrafficManagementSystem
   ```

2. **Initialize the environment**
   This command downloads the required YOLO weights and builds the Docker containers.
   ```bash
   make setup
   ```

3. **Start the services**
   ```bash
   make up
   ```

## Application Access

> **Web Dashboard**  
> http://localhost:3000  
> User interface for monitoring and control.

---

> **Backend API**  
> http://localhost:5000  
> REST API endpoints.

---

> **API Health Check**  
> http://localhost:5000/health  
> Verify backend service status.

## Documentation

Full project documentation is available in the [`docs/`](docs/) directory.

- [Project Overview](docs/overview.md)
- [Docker Guide](docs/docker/README.md)
- [Backend Documentation](docs/backend/README.md)
- [Frontend Documentation](docs/frontend/README.md)


## Docker Deployment

The application is fully containerized using Docker and Docker Compose. This ensures a consistent environment for both development and production. For comprehensive instructions on building, running, and troubleshooting the Docker containers, see the [Detailed Docker Guide](docs/docker/README.md).

---

## Project Management Commands

| Command | Description |
|:---|:---|
| `make setup` | Downloads model weights and builds Docker images. |
| `make up` | Starts all services in the background. |
| `make dev` | Starts services in development mode with hot-reloading enabled. |
| `make logs` | Displays real-time output from all service containers. |
| `make down` | Stops and removes all running containers. |
| `make clean` | Removes containers, volumes, and local images. |
| `make help` | Lists all available Makefile targets. |

---

## Manual Installation

For environments where Docker is not available, follow these steps:

### Backend Configuration
1. Install Python dependencies: `pip install -r backend/requirements.txt`
2. Download YOLO weights: `cd backend && bash download.sh`
3. Compile the optimization engine: `g++ -std=c++17 -O3 -fopenmp -o backend/Algo1 backend/Algo.cpp`
4. Start the Flask server: `python backend/app.py`

### Frontend Configuration
1. Install Node dependencies: `cd frontend && npm install`
2. Start the development server: `npm start`

---

## Contributing

1. Fork the project.
2. Create a feature branch (`git checkout -b <feature/OptimizationUpdate>`).
3. Commit your changes (`git commit -m "Improve GA convergence speed"`).
4. Push to the branch (`git push origin feature/OptimizationUpdate`).
5. Open a Pull Request.

---

## Acknowledgments

- **AlexeyAB/darknet:** For the YOLOv4 implementation[not done yet.].
- **OpenCV Team:** For the vision processing libraries.
- **Genetic Algorithm:** Core logic based on standard evolutionary strategy principles.