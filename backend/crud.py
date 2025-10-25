from sqlalchemy import text
from datetime import datetime, timedelta
from .db import SessionLocal

def create_event(event_data: dict):
    """Insert event into database"""
    db = SessionLocal()
    try:
        query = text("""
            INSERT INTO events (
                event_type, timestamp, session_id, user_id, page_url,
                utm_source, utm_medium, utm_campaign, platform, device,
                revenue, metadata
            ) VALUES (
                :event_type, :timestamp, :session_id, :user_id, :page_url,
                :utm_source, :utm_medium, :utm_campaign, :platform, :device,
                :revenue, CAST(:metadata AS jsonb)
            ) RETURNING id
        """)
        result = db.execute(query, event_data)
        db.commit()
        return result.fetchone()[0]
    finally:
        db.close()

def get_funnel_metrics(hours: int = 168):
    """Get aggregated funnel counts for the past N hours"""
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        query = text("""
            SELECT
                COUNT(*) FILTER (WHERE event_type = 'ad_click') as ad_clicks,
                COUNT(*) FILTER (WHERE event_type = 'page_view' AND metadata->>'landing' = 'true') as landings,
                COUNT(*) FILTER (WHERE event_type = 'product_view') as product_views,
                COUNT(*) FILTER (WHERE event_type = 'add_to_cart') as adds,
                COUNT(*) FILTER (WHERE event_type = 'purchase') as purchases
            FROM events
            WHERE timestamp >= :cutoff
        """)
        result = db.execute(query, {"cutoff": cutoff})
        row = result.fetchone()
        return {
            "ad_clicks": row[0] or 0,
            "landings": row[1] or 0,
            "product_views": row[2] or 0,
            "adds": row[3] or 0,
            "purchases": row[4] or 0
        }
    finally:
        db.close()

def get_user_analytics(hours: int = 168):
    """Get user analytics for the past N hours"""
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        query = text("""
            SELECT
                COUNT(DISTINCT user_id) FILTER (WHERE user_id IS NOT NULL) as total_users,
                COUNT(DISTINCT session_id) as total_sessions,
                COUNT(*) as total_events,
                COUNT(DISTINCT user_id) FILTER (WHERE event_type = 'user_signup') as new_users,
                COUNT(DISTINCT user_id) FILTER (WHERE event_type = 'user_login') as returning_users
            FROM events
            WHERE timestamp >= :cutoff
        """)
        result = db.execute(query, {"cutoff": cutoff})
        row = result.fetchone()
        return {
            "total_users": row[0] or 0,
            "total_sessions": row[1] or 0,
            "total_events": row[2] or 0,
            "new_users": row[3] or 0,
            "returning_users": row[4] or 0
        }
    finally:
        db.close()

def get_campaign_performance(hours: int = 168):
    """Get campaign performance metrics"""
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        query = text("""
            SELECT
                COALESCE(metadata->>'campaign', utm_campaign, 'direct') as campaign,
                COUNT(*) FILTER (WHERE event_type = 'ad_click') as clicks,
                COUNT(DISTINCT session_id) as sessions,
                COUNT(*) FILTER (WHERE event_type = 'purchase') as purchases,
                COALESCE(SUM(revenue) FILTER (WHERE event_type = 'purchase'), 0) as revenue
            FROM events
            WHERE timestamp >= :cutoff
            GROUP BY campaign
            ORDER BY clicks DESC
            LIMIT 10
        """)
        result = db.execute(query, {"cutoff": cutoff})
        campaigns = []
        for row in result:
            campaigns.append({
                "campaign": row[0],
                "clicks": row[1] or 0,
                "sessions": row[2] or 0,
                "purchases": row[3] or 0,
                "revenue": float(row[4] or 0)
            })
        return campaigns
    finally:
        db.close()

def get_revenue_metrics(hours: int = 168):
    """Get revenue analytics"""
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        query = text("""
            SELECT
                COUNT(*) FILTER (WHERE event_type = 'purchase') as total_purchases,
                COALESCE(SUM(revenue) FILTER (WHERE event_type = 'purchase'), 0) as total_revenue,
                COALESCE(AVG(revenue) FILTER (WHERE event_type = 'purchase'), 0) as avg_order_value,
                COALESCE(MAX(revenue) FILTER (WHERE event_type = 'purchase'), 0) as max_order_value
            FROM events
            WHERE timestamp >= :cutoff
        """)
        result = db.execute(query, {"cutoff": cutoff})
        row = result.fetchone()
        return {
            "total_purchases": row[0] or 0,
            "total_revenue": float(row[1] or 0),
            "avg_order_value": float(row[2] or 0),
            "max_order_value": float(row[3] or 0)
        }
    finally:
        db.close()

def get_event_timeline(hours: int = 168, interval: str = 'hour'):
    """Get event counts over time"""
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        # Choose interval based on time range
        if hours <= 24:
            trunc_str = "DATE_TRUNC('hour', timestamp)"
        elif hours <= 168:
            trunc_str = "DATE_TRUNC('day', timestamp)"
        else:
            trunc_str = "DATE_TRUNC('day', timestamp)"

        query = text(f"""
            SELECT
                {trunc_str} as time_bucket,
                COUNT(*) FILTER (WHERE event_type = 'ad_click') as ad_clicks,
                COUNT(*) FILTER (WHERE event_type = 'page_view') as page_views,
                COUNT(*) FILTER (WHERE event_type = 'product_view') as product_views,
                COUNT(*) FILTER (WHERE event_type = 'add_to_cart') as adds,
                COUNT(*) FILTER (WHERE event_type = 'purchase') as purchases,
                COALESCE(SUM(revenue), 0) as revenue
            FROM events
            WHERE timestamp >= :cutoff
            GROUP BY time_bucket
            ORDER BY time_bucket ASC
        """)
        result = db.execute(query, {"cutoff": cutoff})
        timeline = []
        for row in result:
            timeline.append({
                "timestamp": row[0].isoformat() if row[0] else None,
                "ad_clicks": row[1] or 0,
                "page_views": row[2] or 0,
                "product_views": row[3] or 0,
                "adds": row[4] or 0,
                "purchases": row[5] or 0,
                "revenue": float(row[6] or 0)
            })
        return timeline
    finally:
        db.close()

def get_recent_events(limit: int = 20):
    """Get most recent events"""
    db = SessionLocal()
    try:
        query = text("""
            SELECT
                event_type,
                user_id,
                session_id,
                utm_campaign,
                revenue,
                metadata->>'product_name' as product_name,
                metadata->>'user_email' as user_email,
                metadata->>'user_name' as user_name,
                timestamp
            FROM events
            ORDER BY timestamp DESC
            LIMIT :limit
        """)
        result = db.execute(query, {"limit": limit})
        events = []
        for row in result:
            events.append({
                "event_type": row[0],
                "user_id": row[1],
                "session_id": row[2],
                "campaign": row[3] or 'direct',
                "revenue": float(row[4] or 0),
                "product_name": row[5],
                "user_email": row[6],
                "user_name": row[7],
                "timestamp": row[8].isoformat() if row[8] else None
            })
        return events
    finally:
        db.close()
