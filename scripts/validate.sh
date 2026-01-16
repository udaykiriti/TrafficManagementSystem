#!/bin/bash

# Validation script to check Docker integration
# Run this before committing to verify everything is set up correctly

set -e

# Change to project root directory (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo " Validating Docker Integration..."
echo ""

ERRORS=0

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo " Docker is installed"
else
    echo " Docker is not installed"
    ERRORS=$((ERRORS + 1))
fi

# Check if Docker Compose is installed
if command -v docker-compose &> /dev/null; then
    echo " Docker Compose is installed"
else
    echo " Docker Compose is not installed"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo " Checking required files..."

# Check Docker files
REQUIRED_FILES=(
    "docker-compose.yml"
    "docker-compose.dev.yml"
    "Makefile"
    "scripts/setup.sh"
    ".dockerignore"
    "backend/Dockerfile"
    "backend/.dockerignore"
    "backend/.env.example"
    "frontend/Dockerfile"
    "frontend/Dockerfile.dev"
    "frontend/.dockerignore"
    "frontend/.env.example"
    "frontend/nginx.conf"
    "docs/docker/README.md"
    "docs/docker/QUICK_START.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo " $file"
    else
        echo " Missing: $file"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo " Validating file contents..."

# Check if docker-compose.yml has required services
if grep -q "backend:" docker-compose.yml && grep -q "frontend:" docker-compose.yml; then
    echo " docker-compose.yml has backend and frontend services"
else
    echo " docker-compose.yml missing required services"
    ERRORS=$((ERRORS + 1))
fi

# Check if Dockerfile builds C++ code
if grep -q "g++.*Algo" backend/Dockerfile; then
    echo " Backend Dockerfile compiles C++ algorithm"
else
    echo " Backend Dockerfile missing C++ compilation"
    ERRORS=$((ERRORS + 1))
fi

# Check if frontend uses multi-stage build
if grep -q "FROM.*AS builder" frontend/Dockerfile; then
    echo " Frontend uses multi-stage build"
else
    echo " Frontend missing multi-stage build"
    ERRORS=$((ERRORS + 1))
fi

# Check if nginx.conf exists
if [ -f "frontend/nginx.conf" ]; then
    if grep -q "location /api/" frontend/nginx.conf; then
        echo " Nginx configured with API proxy"
    else
        echo "  Warning: Nginx may not have API proxy configured"
    fi
fi

# Check if setup script is executable
if [ -x "scripts/setup.sh" ]; then
    echo " scripts/setup.sh is executable"
else
    echo "  Warning: scripts/setup.sh is not executable (run: chmod +x scripts/setup.sh)"
fi

echo ""
echo " Checking YOLO weights..."

if [ -f "backend/yolov4-tiny.weights" ]; then
    SIZE=$(du -h backend/yolov4-tiny.weights | cut -f1)
    echo " YOLO weights found ($SIZE)"
else
    echo "  YOLO weights not found (will be downloaded during setup)"
fi

echo ""
echo " Testing Docker Compose configuration..."

# Validate docker-compose files
if docker-compose config > /dev/null 2>&1; then
    echo " docker-compose.yml is valid"
else
    echo " docker-compose.yml has errors"
    ERRORS=$((ERRORS + 1))
fi

if docker-compose -f docker-compose.dev.yml config > /dev/null 2>&1; then
    echo " docker-compose.dev.yml is valid"
else
    echo " docker-compose.dev.yml has errors"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo " Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $ERRORS -eq 0 ]; then
    echo " All checks passed! Docker integration is complete."
    echo ""
    echo " Ready to start:"
    echo "   ./scripts/setup.sh   # Interactive setup"
    echo "   make setup           # Download weights and build"
    echo "   make up              # Start services"
    exit 0
else
    echo " Found $ERRORS error(s). Please fix before proceeding."
    exit 1
fi
