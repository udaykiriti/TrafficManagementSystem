#!/bin/bash
# Entrypoint script to fix volume permissions at container startup

echo "=== Fixing volume permissions ==="

# Ensure directories exist and are writable
mkdir -p /app/uploads /app/outputs /app/data
chmod -R 777 /app/uploads /app/outputs /app/data

echo "Permissions set:"
ls -la /app/uploads /app/outputs /app/data

echo "=== Starting Flask application ==="
exec python app.py
