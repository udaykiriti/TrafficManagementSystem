# Makefile for AI Traffic Management System

.PHONY: help setup up down logs status clean dev restart shell-backend shell-frontend

# Default target: Help
help:
	@echo " AI Traffic Management System - Make Commands"
	@echo "==============================================="
	@echo "  make setup        - Download weights and build Docker images"
	@echo "  make up           - Start all services in production mode (detached)"
	@echo "  make dev          - Start all services in development mode"
	@echo "  make down         - Stop all services"
	@echo "  make restart      - Restart all services"
	@echo "  make logs         - View logs from all services"
	@echo "  make status       - Check status of containers"
	@echo "  make clean        - Stop services and remove containers/volumes"
	@echo "  make shell-backend  - Access backend container shell"
	@echo "  make shell-frontend - Access frontend container shell"

# Setup: Download weights and build images
setup:
	@echo "  Downloading YOLO weights..."
	cd backend && bash download.sh
	@echo "  Building Docker images..."
	docker-compose build

# Start services (Production)
up:
	@echo " Starting services (Production)..."
	docker-compose up -d
	@echo " Services started!"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:5000"

# Start services (Development)
dev:
	@echo "  Starting services (Development)..."
	docker-compose -f docker-compose.dev.yml up --build

# Stop services
down:
	@echo " Stopping services..."
	docker-compose down

# Restart services
restart: down up

# View logs
logs:
	docker-compose logs -f

# Check status
status:
	docker-compose ps

# Clean everything
clean:
	@echo " Cleaning up..."
	docker-compose down -v --rmi local
	@echo " Clean complete."

# Shell access
shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend sh
