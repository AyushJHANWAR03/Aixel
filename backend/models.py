from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

class EventCreate(BaseModel):
    event_type: str
    timestamp: Optional[datetime] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    page_url: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    platform: Optional[str] = None
    device: Optional[str] = None
    revenue: Optional[float] = 0
    metadata: Optional[Dict] = Field(default_factory=dict)

class FunnelMetrics(BaseModel):
    ad_clicks: int
    landings: int
    product_views: int
    adds: int
    purchases: int

class InsightsRequest(BaseModel):
    metrics: Dict

class InsightsResponse(BaseModel):
    observations: list[str]
    recommendations: list[str]
