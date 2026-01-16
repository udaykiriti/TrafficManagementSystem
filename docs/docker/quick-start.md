#  Quick Start Guide - Docker Setup

## Prerequisites
- Docker Engine 20.10+ installed
- Docker Compose 2.0+ installed
- 4GB+ RAM available

## One-Command Setup

```bash
./scripts/setup.sh
```

This interactive script will:
1. Check Docker installation
2. Download YOLO weights (if missing)
3. Create .env files
4. Build Docker images
5. Start services

## Manual Setup

### Step 1: Download YOLO Weights
```bash
cd backend
bash download.sh
cd ..
```

### Step 2: Create Environment Files
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### Step 3: Build and Start
```bash
# Production mode
docker-compose up -d

# Or development mode (hot reload)
docker-compose -f docker-compose.dev.yml up
```

## Access Application

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

## Common Commands

```bash
# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop services
docker-compose down

# Restart
docker-compose restart

# Shell access
docker-compose exec backend bash
docker-compose exec frontend sh
```

## Using Makefile (Easier)

```bash
make help       # Show all commands
make setup      # Initial setup
make up         # Start services
make dev        # Development mode
make logs       # View logs
make status     # Check status
make health     # Health check
make down       # Stop services
make clean      # Clean everything
make test       # Run tests
```

## Test the System

1. Open http://localhost:3000
2. Upload 4 traffic videos
3. Wait for processing
4. View optimized signal timings
5. Check analytics dashboard

## Troubleshooting

### Services won't start
```bash
# Check Docker daemon
docker info

# Check ports
netstat -tulpn | grep -E '3000|5000'

# Rebuild from scratch
make clean && make build && make up
```

### Backend errors
```bash
# Check logs
docker-compose logs backend

# Check if weights exist
docker-compose exec backend ls -lh yolov4-tiny.weights

# Check compiled binary
docker-compose exec backend ./Algo1 10 15 20 12
```

### Frontend not loading
```bash
# Check logs
docker-compose logs frontend

# Check nginx config
docker-compose exec frontend nginx -t

# Rebuild frontend
docker-compose build frontend
docker-compose restart frontend
```

## Next Steps

- Read [README.Docker.md](README.Docker.md) for detailed documentation
- Check [DOCKER_SUMMARY.md](DOCKER_SUMMARY.md) for all changes
- See main [README.md](README.md) for project overview

## Support

If issues persist:
1. Check logs: `make logs`
2. Verify health: `make health`
3. Try clean rebuild: `make clean && make setup`
4. Review error.log in backend directory

Happy traffic optimizing! 
