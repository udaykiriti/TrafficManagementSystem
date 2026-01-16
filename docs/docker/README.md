# Docker Deployment Guide

## Overview

This guide details the containerized deployment of the Traffic Management System using Docker and Docker Compose. This is the recommended method for ensuring consistency across development and production environments.

## Services

### Frontend Container
- **Base Image:** `nginx:alpine` (Production) / `node:18` (Development)
- **Port Mapping:** Host:3000 -> Container:80 (Prod) / 3000 (Dev)
- **Role:** Serves the React application and handles reverse proxying in development.

### Backend Container
- **Base Image:** `python:3.10-slim`
- **Port Mapping:** Host:5000 -> Container:5000
- **Dependencies:** Includes system libraries for OpenCV (`libgl1`) and OpenMP (`libgomp1`).
- **Persistence:** Mounts volumes for `uploads`, `outputs`, and `data` to ensure data retention across restarts.

## Setup Instructions

### 1. Preparation
Ensure all necessary model weights are downloaded and images are built.
```bash
make setup
```

### 2. Starting Services

**Production Mode:**
Starts optimized containers in the background.
```bash
make up
```

**Development Mode:**
Starts containers with volume mounting for hot-reloading code changes.
```bash
make dev
```

### 3. Stopping Services
Stops and removes all running containers.
```bash
make down
```

## Configuration

Environment variables are passed to containers via `.env` files located in the `frontend/` and `backend/` directories.

### Backend Variables
- `FLASK_ENV`: Sets the application environment (`production` or `development`).
- `MAX_UPLOAD_SIZE_MB`: Limits the size of video uploads (default: 200).

### Frontend Variables
- `REACT_APP_API_URL`: Specifies the backend API endpoint.

## Troubleshooting

- **Build Failures:** Ensure `make setup` has been run to download large weight files before building the Docker context.
- **Port Conflicts:** Verify that ports 3000 and 5000 are not in use by other services.
- **Permission Issues:** Ensure the user running Docker has write permissions to the `backend/data` directory for volume mounting.