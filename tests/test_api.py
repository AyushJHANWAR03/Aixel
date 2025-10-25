import pytest
import requests
import time

API_BASE = "http://localhost:8000"

def test_health_check():
    """Test health endpoint"""
    response = requests.get(f"{API_BASE}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_track_event():
    """Test event tracking endpoint"""
    event = {
        "event_type": "page_view",
        "session_id": "test-session-123",
        "page_url": "/test",
        "metadata": {"test": True}
    }
    response = requests.post(f"{API_BASE}/api/track", json=event)
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert "id" in response.json()

def test_funnel_endpoint():
    """Test funnel metrics endpoint"""
    response = requests.get(f"{API_BASE}/api/funnel?hours=24")
    assert response.status_code == 200
    data = response.json()
    assert "ad_clicks" in data
    assert "landings" in data
    assert "product_views" in data
    assert "adds" in data
    assert "purchases" in data

def test_insights_endpoint():
    """Test AI insights generation"""
    metrics = {
        "ad_clicks": 1000,
        "landings": 500,
        "product_views": 200,
        "adds": 100,
        "purchases": 50
    }
    response = requests.post(f"{API_BASE}/api/generate_insights", json={"metrics": metrics})
    assert response.status_code == 200
    data = response.json()
    assert "observations" in data
    assert "recommendations" in data
    assert len(data["observations"]) > 0
    assert len(data["recommendations"]) > 0
