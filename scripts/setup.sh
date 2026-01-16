#!/bin/bash

# =============================================================================
# COMPLETE PROJECT SETUP AND RUN SCRIPT
# Dynamic Traffic Management System
# =============================================================================
# This script will set up and run the entire project from scratch
# =============================================================================

set -e  # Exit on error

# Change to project root directory (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print colored message
print_step() {
    echo -e "${BLUE}==>${NC} ${CYAN}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Banner
echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     TRAFFIC MANAGEMENT SYSTEM - COMPLETE SETUP            ║
║                                                           ║
║   This script will set up and run the entire project      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# =============================================================================
# STEP 1: Check Prerequisites
# =============================================================================
print_step "STEP 1: Checking prerequisites..."

MISSING_DEPS=0

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    print_success "Docker installed: $DOCKER_VERSION"
else
    print_error "Docker is NOT installed"
    MISSING_DEPS=$((MISSING_DEPS + 1))
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    print_success "Docker Compose installed: $COMPOSE_VERSION"
else
    print_error "Docker Compose is NOT installed"
    MISSING_DEPS=$((MISSING_DEPS + 1))
fi

if [ $MISSING_DEPS -gt 0 ]; then
    echo ""
    print_error "Missing required dependencies!"
    echo ""
    echo "Please install:"
    echo "  • Docker Desktop: https://www.docker.com/products/docker-desktop"
    echo "  • Or Docker Engine: https://docs.docker.com/engine/install/"
    echo ""
    exit 1
fi

echo ""

# =============================================================================
# STEP 2: Download YOLO Weights
# =============================================================================
print_step "STEP 2: Checking YOLO weights..."

if [ -f "backend/yolov4-tiny.weights" ]; then
    SIZE=$(du -h backend/yolov4-tiny.weights | cut -f1)
    print_success "YOLO weights already exist ($SIZE)"
else
    print_warning "YOLO weights not found. Downloading..."
    cd backend
    
    if [ -f "download.sh" ]; then
        bash download.sh
    else
        echo "Downloading YOLOv4-tiny weights (23MB)..."
        wget -q --show-progress https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights
    fi
    
    cd ..
    
    if [ -f "backend/yolov4-tiny.weights" ]; then
        print_success "YOLO weights downloaded successfully"
    else
        print_error "Failed to download YOLO weights"
        exit 1
    fi
fi

echo ""

# =============================================================================
# STEP 3: Create Environment Files
# =============================================================================
print_step "STEP 3: Setting up environment files..."

# Backend .env
if [ ! -f "backend/.env" ]; then
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        print_success "Created backend/.env"
    else
        cat > backend/.env << 'ENVEOF'
FLASK_ENV=production
DEBUG_UPLOAD=1
PYTHONUNBUFFERED=1
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW=60
ENVEOF
        print_success "Created backend/.env with defaults"
    fi
else
    print_success "backend/.env already exists"
fi

# Frontend .env
if [ ! -f "frontend/.env" ]; then
    if [ -f "frontend/.env.example" ]; then
        cp frontend/.env.example frontend/.env
        print_success "Created frontend/.env"
    else
        cat > frontend/.env << 'ENVEOF'
REACT_APP_API_URL=http://localhost:5000
REACT_APP_ENVIRONMENT=production
ENVEOF
        print_success "Created frontend/.env with defaults"
    fi
else
    print_success "frontend/.env already exists"
fi

echo ""

# =============================================================================
# STEP 4: Create Required Directories
# =============================================================================
print_step "STEP 4: Creating required directories..."

mkdir -p backend/uploads
mkdir -p backend/outputs
mkdir -p backend/data

print_success "Directories created: uploads, outputs, data"

echo ""

# =============================================================================
# STEP 5: Ask User for Deployment Mode
# =============================================================================
print_step "STEP 5: Choose deployment mode..."

echo ""
echo "Select how you want to run the project:"
echo ""
echo "  1)  Docker (Recommended - Easy, Isolated)"
echo "     • No need to install Python, Node.js, or dependencies"
echo "     • Everything runs in containers"
echo "     • Easy to start/stop"
echo ""
echo "  2)  Manual (Traditional - Direct on your machine)"
echo "     • Requires Python 3.10+, Node.js 18+, and all dependencies"
echo "     • Runs directly on your system"
echo ""
read -p "Enter your choice [1-2]: " MODE_CHOICE

echo ""

if [ "$MODE_CHOICE" = "1" ]; then
    # =============================================================================
    # DOCKER MODE
    # =============================================================================
    print_step "🐳 Setting up Docker deployment..."
    
    # Ask for production or development
    echo ""
    echo "Select Docker mode:"
    echo "  1) Production (Optimized, recommended)"
    echo "  2) Development (Hot reload for code changes)"
    echo ""
    read -p "Enter choice [1-2]: " DOCKER_MODE
    
    echo ""
    print_step "Building Docker images (this may take 5-10 minutes)..."
    
    if [ "$DOCKER_MODE" = "2" ]; then
        # Development mode
        docker-compose -f docker-compose.dev.yml build
        print_success "Docker images built successfully (development mode)"
        
        echo ""
        print_step "Starting services in development mode..."
        docker-compose -f docker-compose.dev.yml up -d
    else
        # Production mode
        docker-compose build
        print_success "Docker images built successfully (production mode)"
        
        echo ""
        print_step "Starting services in production mode..."
        docker-compose up -d
    fi
    
    # Wait for services to be ready
    echo ""
    print_step "Waiting for services to be ready..."
    sleep 10
    
    # Check status
    print_step "Checking service status..."
    docker-compose ps
    
    echo ""
    print_success "Docker containers are running!"
    
    echo ""
    print_step "Service URLs:"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:5000"
    echo "    Health:    http://localhost:5000/health"
    
    echo ""
    echo "Useful commands:"
    echo "  docker-compose logs -f          # View logs"
    echo "  docker-compose ps               # Check status"
    echo "  docker-compose restart          # Restart services"
    echo "  docker-compose down             # Stop services"
    echo ""
    echo "Or use Makefile shortcuts:"
    echo "  make logs                       # View logs"
    echo "  make status                     # Check status"
    echo "  make restart                    # Restart"
    echo "  make down                       # Stop"
    
elif [ "$MODE_CHOICE" = "2" ]; then
    # =============================================================================
    # MANUAL MODE
    # =============================================================================
    print_step "💻 Setting up manual deployment..."
    
    # Check Python
    echo ""
    print_step "Checking Python..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python installed: $PYTHON_VERSION"
    else
        print_error "Python 3 is not installed!"
        echo "Please install Python 3.10+ from https://www.python.org/"
        exit 1
    fi
    
    # Check Node.js
    print_step "Checking Node.js..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js installed: $NODE_VERSION"
    else
        print_error "Node.js is not installed!"
        echo "Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm installed: $NPM_VERSION"
    else
        print_error "npm is not installed!"
        exit 1
    fi
    
    # Check C++ compiler
    echo ""
    print_step "Checking C++ compiler..."
    if command -v g++ &> /dev/null; then
        GCC_VERSION=$(g++ --version | head -n1)
        print_success "g++ installed: $GCC_VERSION"
    else
        print_error "g++ is not installed!"
        echo "Please install build tools:"
        echo "  Ubuntu/Debian: sudo apt install build-essential"
        echo "  macOS: xcode-select --install"
        exit 1
    fi
    
    # =============================================================================
    # Setup Backend
    # =============================================================================
    echo ""
    print_step "Setting up Backend..."
    
    cd backend
    
    # Install Python dependencies
    print_step "Installing Python dependencies..."
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    # Compile C++ algorithm
    print_step "Compiling C++ Genetic Algorithm..."
    if [ -f "Algo.cpp" ]; then
        g++ -std=c++17 -O3 -march=native -fopenmp -o Algo1 Algo.cpp
        if [ -f "Algo1" ]; then
            print_success "C++ algorithm compiled successfully"
        else
            print_error "Failed to compile C++ algorithm"
            exit 1
        fi
    else
        print_error "Algo.cpp not found!"
        exit 1
    fi
    
    cd ..
    
    # =============================================================================
    # Setup Frontend
    # =============================================================================
    echo ""
    print_step "Setting up Frontend..."
    
    cd frontend
    
    # Install Node dependencies
    print_step "Installing Node.js dependencies (this may take a few minutes)..."
    npm install
    print_success "Node.js dependencies installed"
    
    cd ..
    
    # =============================================================================
    # Start Services
    # =============================================================================
    echo ""
    print_step "Starting services..."
    
    # Start backend in background
    print_step "Starting backend server..."
    cd backend
    nohup python3 app.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    cd ..
    print_success "Backend started (PID: $BACKEND_PID)"
    
    # Wait a bit for backend to start
    sleep 5
    
    # Start frontend in background
    print_step "Starting frontend server..."
    cd frontend
    nohup npm start > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    cd ..
    print_success "Frontend started (PID: $FRONTEND_PID)"
    
    # Wait for services
    print_step "Waiting for services to be ready (30 seconds)..."
    sleep 30
    
    echo ""
    print_success "Services are starting up!"
    
    echo ""
    print_step "Service URLs:"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:5000"
    echo "    Health:    http://localhost:5000/health"
    
    echo ""
    echo "View logs:"
    echo "  tail -f backend.log            # Backend logs"
    echo "  tail -f frontend.log           # Frontend logs"
    
    echo ""
    echo "Stop services:"
    echo "  kill \$(cat backend.pid)        # Stop backend"
    echo "  kill \$(cat frontend.pid)       # Stop frontend"
    
else
    print_error "Invalid choice!"
    exit 1
fi

# =============================================================================
# Final Steps
# =============================================================================
echo ""
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║               SETUP COMPLETE!                             ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo " Next Steps:"
echo ""
echo "  1. Open your browser: http://localhost:3000"
echo "  2. Upload 4 traffic videos (one for each lane)"
echo "  3. Wait for AI processing"
echo "  4. View optimized traffic signal timings!"
echo ""

echo " Documentation:"
echo "  • QUICK_START.md - Quick reference guide"
echo "  • README.Docker.md - Docker documentation"
echo "  • README.md - Project overview"
echo ""

echo " Need Help?"
echo "  • Check logs for errors"
echo "  • Read troubleshooting in README.Docker.md"
echo "  • Verify health: curl http://localhost:5000/health"
echo ""

print_success "Ready to optimize traffic! "
echo ""
