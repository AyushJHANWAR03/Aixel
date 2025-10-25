from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import EventCreate, FunnelMetrics, InsightsRequest, InsightsResponse
from .crud import (
    create_event,
    get_funnel_metrics,
    get_user_analytics,
    get_campaign_performance,
    get_revenue_metrics,
    get_event_timeline,
    get_recent_events
)
from .openai_client import generate_insights
import json
from datetime import datetime

app = FastAPI(title="AI Customer Journey Tracker")

# CORS for demo site and dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/track")
def track_event(event: EventCreate):
    """Ingest a single event"""
    try:
        event_dict = event.dict()
        if event_dict['timestamp'] is None:
            event_dict['timestamp'] = datetime.utcnow()

        # Convert metadata dict to JSON string for postgres
        event_dict['metadata'] = json.dumps(event_dict['metadata'])

        event_id = create_event(event_dict)
        return {"ok": True, "id": str(event_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/funnel", response_model=FunnelMetrics)
def get_funnel(hours: int = 168):
    """Get funnel metrics for the past N hours"""
    try:
        metrics = get_funnel_metrics(hours)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate_insights", response_model=InsightsResponse)
def get_insights(request: InsightsRequest):
    """Generate AI insights from metrics"""
    try:
        insights = generate_insights(request.metrics)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user_analytics")
def get_users(hours: int = 168):
    """Get user analytics for the past N hours"""
    try:
        analytics = get_user_analytics(hours)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/campaign_performance")
def get_campaigns(hours: int = 168):
    """Get campaign performance metrics"""
    try:
        campaigns = get_campaign_performance(hours)
        return campaigns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/revenue_metrics")
def get_revenue(hours: int = 168):
    """Get revenue metrics"""
    try:
        revenue = get_revenue_metrics(hours)
        return revenue
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/event_timeline")
def get_timeline(hours: int = 168):
    """Get event timeline data"""
    try:
        timeline = get_event_timeline(hours)
        return timeline
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recent_events")
def get_recent(limit: int = 20):
    """Get most recent events"""
    try:
        events = get_recent_events(limit)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}
