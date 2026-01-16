# Docker Upload Fix - Applied

## Problem
The Docker container was unable to save uploaded video files due to permission issues with the mounted volume (`./backend/uploads`).

## Root Cause
When Docker mounts a host directory as a volume, it preserves the host's ownership/permissions. The container's non-root user (appuser) couldn't write to the mounted directory.

## Solution Applied

### 1. **Modified Dockerfile** (`backend/Dockerfile`)
   - Changed container to run as `root` instead of `appuser`
   - This allows the container to handle volume mount permissions properly
   
### 2. **Created Entrypoint Script** (`backend/entrypoint.sh`)
   - Fixes permissions on startup: `chmod 777 uploads outputs data`
   - Ensures directories are writable before starting Flask
   
### 3. **Updated Docker Command**
   - Changed from `CMD ["python", "app.py"]` to `CMD ["./entrypoint.sh"]`
   - The entrypoint fixes permissions then starts the app

## How to Apply the Fix

Run the fix permissions script:
```bash
./scripts/fix-permissions.sh
```

Or manually:
```bash
# Stop containers
docker-compose down

# Fix host permissions
chmod 777 backend/uploads backend/outputs backend/data

# Rebuild backend
docker-compose build --no-cache backend

# Start services
docker-compose up -d

# Verify
docker exec traffic-backend touch /app/uploads/.test
```

## Verification

After rebuild, check:
1. Container logs show: "Permissions set" message
2. Test write: `docker exec traffic-backend touch /app/uploads/.test`
3. Upload videos through frontend at http://localhost:3000
4. Backend logs should show: "Successfully saved uploaded file"

## Files Changed
- `backend/Dockerfile` - Run as root, use entrypoint
- `backend/entrypoint.sh` - New startup script (fixes permissions)
- `scripts/fix-permissions.sh` - Consolidated fix script

## Security Note
Running as root in container is generally not ideal for production. For production deployments, consider:
- Using Docker's `user` directive with proper UID/GID mapping
- Setting `--user` flag at runtime
- Using init containers to fix permissions
- Using named volumes instead of bind mounts
