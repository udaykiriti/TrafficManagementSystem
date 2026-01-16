#!/bin/bash
# Consolidated script to fix Docker and upload permissions

set -e

# Change to project root directory (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "========================================="
echo "  Permission Fix Script"
echo "========================================="
echo ""

# Check what fix is needed
echo "Select fix type:"
echo "  1) Fix upload directory permissions (quick)"
echo "  2) Fix Docker group permissions (requires logout)"
echo "  3) Both"
echo ""
read -p "Enter choice [1-3]: " CHOICE

fix_upload_permissions() {
    echo ""
    echo "=== Fixing upload directory permissions ==="
    
    # Ensure directories exist
    mkdir -p backend/uploads backend/outputs backend/data
    chmod 777 backend/uploads backend/outputs backend/data
    
    echo "Current permissions:"
    ls -ld backend/uploads backend/outputs backend/data
    
    # Try to restart container
    echo ""
    echo "Restarting backend container..."
    if command -v docker &> /dev/null; then
        docker restart traffic-backend 2>/dev/null && echo "✓ Container restarted" || echo "Container not running or not found"
    elif command -v podman &> /dev/null; then
        podman restart traffic-backend 2>/dev/null && echo "✓ Container restarted" || echo "Container not running or not found"
    fi
    
    # Wait and test
    sleep 3
    echo ""
    echo "Testing write permissions in container..."
    if docker exec traffic-backend touch /app/uploads/.test 2>/dev/null; then
        echo "✓ SUCCESS: Uploads directory is writable!"
        docker exec traffic-backend rm /app/uploads/.test 2>/dev/null
    else
        echo "Container not running or test failed"
    fi
}

fix_docker_permissions() {
    echo ""
    echo "=== Fixing Docker group permissions ==="
    
    # Check if Docker daemon is running
    if sudo systemctl is-active --quiet docker 2>/dev/null; then
        echo "✓ Docker daemon is running"
    else
        echo "Starting Docker daemon..."
        sudo systemctl start docker
        sudo systemctl enable docker
    fi
    
    echo "Adding user '$USER' to docker group..."
    sudo usermod -aG docker $USER
    
    echo ""
    echo "✓ Done! To apply changes, choose one:"
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
echo "========================================="
echo "  Fix Complete!"
echo "========================================="
