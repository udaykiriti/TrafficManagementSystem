# Docker Setup for Dynamic Traffic Management System

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM available for Docker
- YOLO weights files (see below)

## Quick Start

### 1. Download YOLO Weights

Before building, download the required YOLO model weights:

```bash
cd backend
wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights
# Optional: Download full YOLOv4 for better accuracy
wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights
```

Or use the provided download script:
```bash
cd backend
bash download.sh
```

### 2. Build and Run (Production)

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

### 3. Development Mode (Hot Reload)

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Rebuild if needed
docker-compose -f docker-compose.dev.yml up --build
```

## Architecture

```
┌─────────────────────────────────────────────┐
│           Docker Network                    │
│  ┌─────────────┐      ┌──────────────┐      │
│  │  Frontend   │      │   Backend    │      │
│  │  (Nginx)    │─────▶│   (Flask)    │      │
│  │  Port: 3000 │      │  Port: 5000  │      │
│  └─────────────┘      └──────────────┘      │
│                              │              │
│                              ▼              │
│                       ┌──────────────┐      │
│                       │  Volumes     │      │
│                       │  - uploads   │      │
│                       │  - outputs   │      │
│                       │  - data/     │      │
│                       └──────────────┘      │
└─────────────────────────────────────────────┘
```

## Docker Commands

### Managing Services

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v

# View logs
docker-compose logs -f [service_name]

# Execute command in container
docker-compose exec backend bash
docker-compose exec frontend sh
```

### Building

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend

# Build without cache
docker-compose build --no-cache

# Pull latest base images
docker-compose pull
```

### Monitoring

```bash
# View container status
docker-compose ps

# View resource usage
docker stats

# Check health status
docker-compose ps | grep "healthy"

# Backend health check
curl http://localhost:5000/health

# Frontend health check
curl http://localhost:3000
```

## Volume Management

Persistent data is stored in volumes:

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect caproject_backend-data

# Backup data directory
docker-compose exec backend tar czf /tmp/data-backup.tar.gz /app/data
docker cp traffic-backend:/tmp/data-backup.tar.gz ./backup/

# Restore data
docker cp ./backup/data-backup.tar.gz traffic-backend:/tmp/
docker-compose exec backend tar xzf /tmp/data-backup.tar.gz -C /
```

## Environment Variables

### Backend

Create `backend/.env` file:

```env
FLASK_ENV=production
DEBUG_UPLOAD=1
PYTHONUNBUFFERED=1
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW=60
```

### Frontend

Create `frontend/.env` file:

```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_ENVIRONMENT=production
```

## Troubleshooting

### Backend Issues

```bash
# Check backend logs
docker-compose logs -f backend

# Check if YOLO weights are loaded
docker-compose exec backend ls -lh yolov4-tiny.weights

# Check compiled C++ binary
docker-compose exec backend ls -lh Algo1

# Test optimizer manually
docker-compose exec backend ./Algo1 10 15 20 12 --verbose

# Check Python dependencies
docker-compose exec backend pip list
```

### Frontend Issues

```bash
# Check frontend logs
docker-compose logs -f frontend

# Check nginx configuration
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# Test nginx syntax
docker-compose exec frontend nginx -t

# Check build files
docker-compose exec frontend ls -la /usr/share/nginx/html
```

### Network Issues

```bash
# Check network connectivity
docker-compose exec frontend ping backend
docker-compose exec backend ping frontend

# Inspect network
docker network inspect caproject_traffic-network

# Test backend API from frontend container
docker-compose exec frontend wget -qO- http://backend:5000/health
```

### Performance Issues

```bash
# Check container resources
docker stats

# Increase Docker memory limit (Docker Desktop)
# Settings → Resources → Memory → 4GB+

# Check disk space
docker system df

# Clean up unused resources
docker system prune -a
```

## Production Deployment

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml traffic

# Check services
docker stack services traffic

# Scale backend
docker service scale traffic_backend=3

# Remove stack
docker stack rm traffic
```

### Using Kubernetes

```bash
# Convert compose to k8s manifests
kompose convert -f docker-compose.yml

# Apply to cluster
kubectl apply -f .
```

## Security Best Practices

1. **Don't commit secrets**: Use `.env` files and `.dockerignore`
2. **Run as non-root**: Add `USER` directive in Dockerfile
3. **Scan images**: `docker scan traffic-backend`
4. **Use specific versions**: Avoid `latest` tags in production
5. **Enable content trust**: `export DOCKER_CONTENT_TRUST=1`

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build images
        run: docker-compose build
      
      - name: Run tests
        run: docker-compose up -d && sleep 10 && curl http://localhost:5000/health
      
      - name: Push to registry
        run: docker-compose push
```

## Performance Optimization

### Multi-stage Builds
Already implemented for frontend to reduce image size from ~1GB to ~50MB.

### Layer Caching
- Requirements/package files are copied before source code
- Use BuildKit: `DOCKER_BUILDKIT=1 docker-compose build`

### Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Verify health: `docker-compose ps`
3. Review this documentation
4. Check project README.md