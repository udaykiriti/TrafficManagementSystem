#!/bin/bash

# COMPLETE PROJECT SETUP AND RUN SCRIPT
# AI Traffic Management System

set -e  # Exit on error

# Change to project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Output helpers
print_step() {
    echo -e "\n>>> $1"
}

print_success() {
    echo " [ OK ] $1"
}

print_error() {
    echo " [ FAIL ] $1"
}

print_warning() {
    echo " [ WARN ] $1"
}

# Banner
cat << "EOF"
  ____  _____ _____ _   _ ____  
 / ___|| ____|_   _| | | |  _ \ 
 \___ \|  _|   | | | | | |_) |
  ___) | |___  | | | |_| |  __/
 |____/|_____| |_|  \___/|_|    
                                
================================
 TRAFFIC MANAGEMENT SYSTEM
================================
EOF

# STEP 1: Check Prerequisites
print_step "Checking prerequisites..."

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
    echo "Please install Docker Desktop or Docker Engine."
    exit 1
fi

# STEP 2: Download YOLO Weights
print_step "Checking YOLO weights..."

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

# STEP 3: Create Environment Files
print_step "Setting up environment files..."

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

# STEP 4: Create Required Directories
print_step "Creating required directories..."

mkdir -p backend/uploads
mkdir -p backend/outputs
mkdir -p backend/data

print_success "Directories created: uploads, outputs, data"

# STEP 5: Ask User for Deployment Mode
print_step "Choose deployment mode..."

echo ""
echo "Select how you want to run the project:"
echo "  1)  Docker (Recommended - Easy, Isolated)"
echo "  2)  Manual (Traditional - Direct on your machine)"
echo ""
read -p "Enter your choice [1-2]: " MODE_CHOICE

if [ "$MODE_CHOICE" = "1" ]; then
    # DOCKER MODE
    print_step "Setting up Docker deployment..."
    
    echo ""
    echo "Select Docker mode:"
    echo "  1) Production (Optimized, recommended)"
    echo "  2) Development (Hot reload for code changes)"
    echo ""
    read -p "Enter choice [1-2]: " DOCKER_MODE
    
    print_step "Building Docker images (this may take 5-10 minutes)..."
    
    if [ "$DOCKER_MODE" = "2" ]; then
        # Development mode
        docker-compose -f docker-compose.dev.yml build
        print_success "Docker images built successfully (development mode)"
        
        print_step "Starting services in development mode..."
        docker-compose -f docker-compose.dev.yml up -d
    else
        # Production mode
        docker-compose build
        print_success "Docker images built successfully (production mode)"
        
        print_step "Starting services in production mode..."
        docker-compose up -d
    fi
    
    print_step "Waiting for services to be ready..."
    sleep 10
    
    print_step "Checking service status..."
    docker-compose ps
    
    print_success "Docker containers are running!"
    
    echo ""
    echo "Service URLs:"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:5000"
    echo "    Health:    http://localhost:5000/health"
    
elif [ "$MODE_CHOICE" = "2" ]; then
    # MANUAL MODE
    print_step "Setting up manual deployment..."
    
    # Check Python
    print_step "Checking Python..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python installed: $PYTHON_VERSION"
    else
        print_error "Python 3 is not installed!"
        exit 1
    fi
    
    # Check Node.js
    print_step "Checking Node.js..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js installed: $NODE_VERSION"
    else
        print_error "Node.js is not installed!"
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
    print_step "Checking C++ compiler..."
    if command -v g++ &> /dev/null; then
        GCC_VERSION=$(g++ --version | head -n1)
        print_success "g++ installed: $GCC_VERSION"
    else
        print_error "g++ is not installed!"
        exit 1
    fi
    
    # Setup Backend
    print_step "Setting up Backend..."
    
    cd backend
    print_step "Installing Python dependencies..."
    pip3 install -r requirements.txt
    print_success "Python dependencies installed"
    
    print_step "Compiling C++ Genetic Algorithm..."
    g++ -std=c++17 -O3 -march=native -fopenmp -o Algo1 Algo.cpp
    if [ -f "Algo1" ]; then
        print_success "C++ algorithm compiled successfully"
    else
        print_error "Failed to compile C++ algorithm"
        exit 1
    fi
    cd ..
    
    # Setup Frontend
    print_step "Setting up Frontend..."
    cd frontend
    print_step "Installing Node.js dependencies..."
    npm install
    print_success "Node.js dependencies installed"
    cd ..
    
    # Start Services
    print_step "Starting services..."
    
    print_step "Starting backend server..."
    cd backend
    nohup python3 app.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    cd ..
    print_success "Backend started (PID: $BACKEND_PID)"
    
    sleep 5
    
    print_step "Starting frontend server..."
    cd frontend
    nohup npm start > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    cd ..
    print_success "Frontend started (PID: $FRONTEND_PID)"
    
    print_step "Waiting for services to be ready (30 seconds)..."
    sleep 30
    
    print_success "Services are starting up!"
    echo ""
    echo "Service URLs:"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:5000"
else
    print_error "Invalid choice!"
    exit 1
fi

# Final Steps
echo ""
cat << "EOF"
        SETUP COMPLETE!
EOF
echo ""
echo " Next Steps:"
echo "  1. Open your browser: http://localhost:3000"
echo "  2. Upload 4 traffic videos (one for each lane)"
echo "  3. Wait for AI processing"
echo "  4. View optimized traffic signal timings!"
echo ""
echo " Documentation:"
echo "  • docs/docker/README.md - Detailed Docker documentation"
echo "  • README.md - Project overview"
echo ""
print_success "Ready to optimize traffic! "
echo ""