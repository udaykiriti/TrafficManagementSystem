#  AI Traffic Management System

[![Frontend](https://img.shields.io/badge/frontend-React-61dafb?logo=react&logoColor=white)](https://reactjs.org/)
[![Backend](https://img.shields.io/badge/backend-Flask-000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Vision](https://img.shields.io/badge/vision-YOLOv4-ff6f00)](https://github.com/AlexeyAB/darknet)
[![Optimizer](https://img.shields.io/badge/optimizer-C%2B%2B17-00599c?logo=c%2B%2B&logoColor=white)](https://isocpp.org/)
[![Container](https://img.shields.io/badge/infra-Docker-2496ed?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

> **Revolutionizing urban flow with intelligent, adaptive real-time monitoring.**

---

##  Overview

The **Smart Adaptive Traffic Management System** isn't just a signal controller; it's a brain for city intersections. By fusing **Computer Vision (YOLOv4)** with **High-Performance Computing (C++)**, we analyze live video feeds to dynamically adjust traffic signal timings.

**The Goal?** Minimize wait times, reduce congestion, and get everyone where they're going faster. 

---

##  See it in Action

| **Real-time Detection** | **Dashboard Analytics** |
|:-------------------:|:-------------------:|
| ![Detection Demo](https://via.placeholder.com/400x225.png?text=YOLO+Detection+GIF+Coming+Soon) *Process live feeds to count vehicles instantly.* | ![Dashboard Demo](https://via.placeholder.com/400x225.png?text=Dashboard+UI+GIF+Coming+Soon) *Visualize data and control signals from a sleek UI.* |

---

##  Features

- ** Eagle-Eye Detection:** Utilizes **YOLOv4** for state-of-the-art vehicle detection and counting.
- ** Intelligent Optimization:** Runs a genetic algorithm in **C++** for lightning-fast signal timing adjustments.
- ** Interactive Dashboard:** A modern **React** frontend to upload videos, view live analytics, and monitor system health.
- ** Multi-Source Input:** Support for uploaded video files or live RTSP camera feeds.
- ** Dockerized:** Fully containerized for easy deployment anywhere.

---

##  Tech Stack

- **Frontend:** React, Material UI
- **Backend:** Flask (Python)
- **AI/ML:** YOLOv4, OpenCV
- **Core Logic:** C++17 (Genetic Algorithm)
- **DevOps:** Docker, Docker Compose

---

##  Getting Started

### Prerequisites
- [Docker Engine](https://docs.docker.com/engine/install/) 20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) 2.0+
- 4GB+ RAM (AI models are hungry! Try to feed moree...)

###  Quick Start (Recommended)

We have a magic script to set everything up for you!

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/CaProject.git
cd CaProject

# 2. Run the interactive setup script
bash scripts/setup.sh
```
Follow the on-screen instructions to choose between Docker (recommended) or Manual setup.

**Access points:**
- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **API:** [http://localhost:5000](http://localhost:5000)
- **Health Check:** [http://localhost:5000/health](http://localhost:5000/health)

###  Manual Setup (Without Script)

<details>
<summary>Click to expand manual instructions</summary>

**Backend:**
```bash
cd backend
pip install -r requirements.txt
bash download.sh  # Download weights
g++ -std=c++17 -O3 -fopenmp -o Algo1 Algo.cpp
python app.py
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```
</details>

---

##  Usage Modes

1.  **File Upload Mode:** Upload 4 video files representing an intersection via the Web UI.
2.  **Live Camera Mode:** Connect 4 RTSP streams for real-time management.
    ```bash
    # Example
    python app.py --real --camera rtsp://cam1 --camera rtsp://cam2 ...
    ```

---

##  Contributing

Contributions make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

##  Acknowledgments

- **YOLOv4** for the incredible object detection speed and accuracy.
- **OpenCV** for making computer vision accessible.
- The open-source community for all the amazing tools.
