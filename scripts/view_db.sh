#!/bin/bash

# Quick script to view database entries

DB_URL="postgresql://postgres:postgres@localhost:5433/aijourney"

echo "=========================================="
echo "📊 AIXEL DATABASE VIEWER"
echo "=========================================="
echo ""

# Total events
echo "📈 Total Events:"
/Library/PostgreSQL/16/bin/psql $DB_URL -c "SELECT COUNT(*) as total FROM events;"
echo ""

# Events by type
echo "📊 Events by Type (Last 24 hours):"
/Library/PostgreSQL/16/bin/psql $DB_URL -c "
SELECT
    event_type,
    COUNT(*) as count,
    COUNT(DISTINCT session_id) as unique_sessions,
    COUNT(DISTINCT user_id) as unique_users
FROM events
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY event_type
ORDER BY count DESC;
"
echo ""

# Recent events
echo "🕐 Last 10 Events:"
/Library/PostgreSQL/16/bin/psql $DB_URL -c "
SELECT
    event_type,
    user_id,
    session_id,
    revenue,
    metadata->>'campaign' as campaign,
    metadata->>'product_name' as product,
    TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') as time
FROM events
ORDER BY timestamp DESC
LIMIT 10;
"
echo ""

# Revenue summary
echo "💰 Revenue Summary:"
/Library/PostgreSQL/16/bin/psql $DB_URL -c "
SELECT
    COUNT(*) as total_purchases,
    COALESCE(SUM(revenue), 0) as total_revenue,
    COALESCE(AVG(revenue), 0) as avg_order_value
FROM events
WHERE event_type = 'purchase';
"
echo ""

echo "=========================================="
echo "Access pgAdmin UI at: http://localhost:5050"
echo "Email: admin@example.com | Password: admin"
echo "=========================================="
