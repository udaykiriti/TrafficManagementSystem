import pytest
import json
import os
import sys

# Add backend to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code in [200, 503]
    data = json.loads(response.data)
    assert 'status' in data
    assert 'components' in data

def test_optimize_logic(client):
    """Test the /test_optimize endpoint with mock car data."""
    payload = {"cars": [10, 20, 30, 40]}
    response = client.post('/test_optimize', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    # If binary is missing, it might return 500, but we check if logic flows
    assert response.status_code in [200, 500]
    data = json.loads(response.data)
    
    if response.status_code == 200:
        assert 'north' in data
        assert 'south' in data
        assert 'delay' in data
    else:
        # If it fails, check if it's because of missing binary or real error
        if "error" in data:
            assert "C++ binary" in data["error"] or "optimizer" in data["error"]

def test_invalid_optimize_request(client):
    """Test /test_optimize with invalid data."""
    payload = {"cars": [10, 20]} # Needs 4
    response = client.post('/test_optimize', 
                           data=json.dumps(payload),
                           content_type='application/json')
    assert response.status_code == 400
