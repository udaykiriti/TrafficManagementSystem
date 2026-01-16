# Docker Guide

This comprehensive guide covers the containerized deployment of the AI Traffic Management System, designed for both development and production environments.

---

## 📋 Prerequisites

*   **Docker Engine:** Version 20.10+
*   **Docker Compose:** Version 2.0+
*   **System Resources:** Minimum 4GB RAM (8GB Recommended for heavy loads).
*   **Ports:** Ensure ports `3000` (Frontend) and `5000` (Backend) are free.

---

## ⚡ Quick Start

The fastest way to get running is via the included `Makefile`.

### 1. Preparation
Download necessary AI models and build the Docker images.
```bash
make setup
```

### 2. Launch (Production)
Start the system in detached mode.
```bash
make up
```
*   **Frontend:** [http://localhost:3000](http://localhost:3000)
*   **Backend:** [http://localhost:5000](http://localhost:5000)

### 3. Launch (Development)
Start with hot-reloading enabled for code changes.
```bash
make dev
```

### 4. Shutdown
Stop all containers and free up resources.
```bash
make down
```

---

## 🏗️ Architecture

The system is composed of two primary services orchestrated by Docker Compose:

### Service 1: `frontend`
*   **Image:** Custom build based on `nginx:alpine` (Production) or `node:18` (Dev).
*   **Port:** Maps host `3000` to container `80` (Prod) or `3000` (Dev).
*   **Role:** Serves the React application and proxies API requests in development.

### Service 2: `backend`
*   **Image:** Custom build based on `python:3.10-slim`.
*   **Port:** Maps host `5000` to container `5000`.
*   **Dependencies:** `g++`, `libgomp1` (OpenMP), `libgl1` (OpenCV).
*   **Volumes:**
    *   `uploads/`: Temporary storage for processed videos.
    *   `outputs/`: Location for generated results.
    *   `data/`: Persistent storage for CSV logs.

---

## 🔧 Configuration

Configuration is managed via environment variables.

### Backend (`backend/.env`)
| Variable | Default | Description |
| :--- | :--- | :--- |
| `FLASK_ENV` | `production` | Run mode (`production` or `development`). |
| `DEBUG_UPLOAD` | `1` | Enable verbose upload logging. |
| `RATE_LIMIT_REQUESTS` | `10` | API rate limit count. |

### Frontend (`frontend/.env`)
| Variable | Default | Description |
| :--- | :--- | :--- |
| `REACT_APP_API_URL` | `http://localhost:5000` | URL of the backend API. |

---

## 🛠️ Advanced Operations

### Inspecting Logs
View real-time logs from all services:
```bash
make logs
# OR
docker-compose logs -f
```

### Accessing Containers
Open a shell inside a running container for debugging:
```bash
# Backend Shell
make shell-backend

# Frontend Shell
make shell-frontend
```

### Data Backup
Back up the persistent CSV logs:
```bash
docker cp $(docker-compose ps -q backend):/app/backend/data ./backup_data
```

---

## ⚠️ Troubleshooting

**Error: "Image not found" or "Build failed"**
*   Ensure you ran `make setup` to download the YOLO weights before building.
*   Check your internet connection.

**Error: "Port already in use"**
*   Identify the process: `sudo lsof -i :5000`
*   Kill it or change the port mapping in `docker-compose.yml`.

**Performance Issues**
*   Increase Docker's memory limit in Docker Desktop settings.
*   Ensure the C++ optimizer is compiled with OpenMP (verified in `Dockerfile`).

---

## 🔒 Security

*   **Non-Root User:** The backend runs as a non-privileged user where possible.
*   **Network Isolation:** Services communicate on a private internal bridge network (`traffic-network`).
*   **Ephemeral Containers:** Containers are stateless; data persists only in defined volumes.
