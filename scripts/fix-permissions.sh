#!/bin/bash
# Consolidated script to fix Docker and upload permissions
set -e

# Change to project root directory (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Function to display help message
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Fixes permissions for Docker execution and backend upload directories."
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help message and exit"
    echo ""
}

# Parse command line arguments
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

# Detect Docker Compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD=""
fi

cat << "EOF"

██████╗ ███████╗██████╗ ███╗   ███╗██╗███████╗███████╗██╗ ██████╗ ███╗   ██╗
██╔══██╗██╔════╝██╔══██╗████╗ ████║██║██╔════╝██╔════╝██║██╔═══██╗████╗  ██║
██████╔╝█████╗  ██████╔╝██╔████╔██║██║███████╗███████╗██║██║   ██║██╔██╗ ██║
██╔═══╝ ██╔══╝  ██╔══██╗██║╚██╔╝██║██║╚════██║╚════██║██║██║   ██║██║╚██╗██║
██║     ███████╗██║  ██║██║ ╚═╝ ██║██║███████║███████║██║╚██████╔╝██║ ╚████║
╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚══════╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝

EOF

# Check what fix is needed
echo "Select fix type:"
echo "  1) Fix upload directory permissions (quick)"
echo "  2) Fix Docker group permissions (requires logout)"
echo "  3) Both"
echo ""
read -p "Enter choice [1-3]: " CHOICE

fix_upload_permissions() {
    echo ""
    echo ">>> Fixing upload directory permissions"
    
    # Ensure directories exist
    mkdir -p backend/uploads backend/outputs backend/data
    chmod 777 backend/uploads backend/outputs backend/data
    
    echo "Current permissions:"
    ls -ld backend/uploads backend/outputs backend/data
    
    # Try to restart container
    echo ""
    echo "[Restart]: Restarting backend container..."
    if [ -n "$DOCKER_COMPOSE_CMD" ]; then
        $DOCKER_COMPOSE_CMD restart backend 2>/dev/null && echo " [ OK ] Container restarted" || echo " [ !! ] Container not running or not found"
    elif command -v docker &> /dev/null; then
        docker restart traffic-backend 2>/dev/null && echo " [ OK ] Container restarted" || echo " [ !! ] Container not running or not found"
    else 
         echo " [ WARN ] Docker command not found, skipping container restart."
    fi
    
    # Wait and test
    sleep 3
    echo ""
    echo "[Waiting]: Testing write permissions in container..."
    if [ -n "$DOCKER_COMPOSE_CMD" ]; then
        if $DOCKER_COMPOSE_CMD exec -T backend touch /app/backend/uploads/.test 2>/dev/null; then
            echo " [ SUCCESS ] Uploads directory is writable!"
            $DOCKER_COMPOSE_CMD exec -T backend rm /app/backend/uploads/.test 2>/dev/null
        else
            echo " [ FAILURE ] Container not running or test failed"
        fi
    else
         echo " [ SKIP ] Cannot test container permissions (docker-compose not found)."
    fi
}

fix_docker_permissions() {
    echo ""
    echo ">>> Fixing Docker group permissions"
    
    # Check if Docker daemon is running
    if sudo systemctl is-active --quiet docker 2>/dev/null; then
        echo " [ OK ] Docker daemon is running"
    else
        echo "Starting Docker daemon..."
        sudo systemctl start docker
        sudo systemctl enable docker
    fi
    
    echo "Adding user '$USER' to docker group..."
    sudo usermod -aG docker $USER
    
    echo ""
    echo " [ DONE ] To apply changes, choose one:"
    echo "  1) Run: newgrp docker"
    echo "  2) Log out and log back in"
    echo "  3) Reboot your system"
}

case $CHOICE in
    1)
        fix_upload_permissions
        ;;
    2)
        fix_docker_permissions
        ;;
    3)
        fix_docker_permissions
        fix_upload_permissions
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "[Complete]: Fix Complete!"
