from collections import defaultdict
from functools import wraps
import time
from flask import request, jsonify, current_app

RATE_LIMIT_REQUESTS = 10  # Max requests
RATE_LIMIT_WINDOW = 60    # Per 60 seconds
request_counts = defaultdict(list)  # IP -> list of timestamps

def rate_limit(func):
    """Simple rate limiter decorator."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        client_ip = request.remote_addr or 'unknown'
        now = time.time()
        
        # Clean old timestamps
        request_counts[client_ip] = [
            ts for ts in request_counts[client_ip] 
            if now - ts < RATE_LIMIT_WINDOW
        ]
        
        # Periodic cleanup of stale IPs (every ~100 calls or check)
        # To avoid overhead on every request, we can do a quick check or just leave it.
        # But a better approach for production:
        if len(request_counts) > 1000:
            # Prune all stale IPs
            to_remove = []
            for ip, timestamps in request_counts.items():
                if not timestamps or (now - timestamps[-1] > RATE_LIMIT_WINDOW):
                    to_remove.append(ip)
            for ip in to_remove:
                del request_counts[ip]

        # Check rate limit
        if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
            current_app.logger.warning(f"Rate limit exceeded for {client_ip}")
            return jsonify({
                'error': 'Rate limit exceeded',
                'detail': f'Max {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds',
                'retry_after': int(RATE_LIMIT_WINDOW - (now - request_counts[client_ip][0]))
            }), 429
        
        # Record this request
        request_counts[client_ip].append(now)
        return func(*args, **kwargs)
    return wrapper
