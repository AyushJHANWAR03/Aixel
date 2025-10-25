const API_BASE = 'http://localhost:8000';

// Deduplication cache - prevent same event from being tracked twice within 2 seconds
const eventCache = new Map();
const DEDUPE_WINDOW_MS = 2000;

// Generate UUID
export const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

// Get or create session ID
export const getSessionId = () => {
  let sessionId = localStorage.getItem('session_id');
  if (!sessionId) {
    sessionId = generateUUID();
    localStorage.setItem('session_id', sessionId);
  }
  return sessionId;
};

// Track event to backend
export const trackEvent = async (eventType, extraData = {}) => {
  const user = JSON.parse(localStorage.getItem('aixel_user'));

  // Create cache key for deduplication
  const cacheKey = `${eventType}_${window.location.pathname}_${user?.userId || 'anon'}_${JSON.stringify(extraData.metadata || {})}`;
  const now = Date.now();

  // Check if this exact event was tracked recently (within DEDUPE_WINDOW_MS)
  const lastTracked = eventCache.get(cacheKey);
  if (lastTracked && (now - lastTracked) < DEDUPE_WINDOW_MS) {
    console.log('🔄 Skipping duplicate event:', eventType);
    return null;
  }

  // Update cache with current timestamp
  eventCache.set(cacheKey, now);

  // Clean up old cache entries (older than DEDUPE_WINDOW_MS)
  for (const [key, timestamp] of eventCache.entries()) {
    if (now - timestamp > DEDUPE_WINDOW_MS) {
      eventCache.delete(key);
    }
  }

  // Merge metadata properly
  const baseMetadata = {
    user_email: user?.email || null,
    user_name: user?.name || null
  };

  const mergedMetadata = {
    ...baseMetadata,
    ...(extraData.metadata || {})
  };

  const event = {
    event_type: eventType,
    session_id: getSessionId(),
    user_id: user?.userId || null,
    timestamp: new Date().toISOString(),
    page_url: window.location.pathname,
    utm_source: new URLSearchParams(window.location.search).get('utm_source') || 'direct',
    utm_medium: new URLSearchParams(window.location.search).get('utm_medium') || 'none',
    utm_campaign: new URLSearchParams(window.location.search).get('utm_campaign') || 'none',
    platform: 'web',
    device: /Mobile|Android|iPhone/i.test(navigator.userAgent) ? 'mobile' : 'desktop',
    revenue: extraData.revenue || 0,
    metadata: mergedMetadata
  };

  try {
    const response = await fetch(`${API_BASE}/api/track`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event)
    });

    const result = await response.json();
    console.log('✅ Tracked:', eventType, result);
    console.log('📊 Event Details:', event);
    return result;
  } catch (error) {
    console.error('❌ Tracking error:', error);
    return null;
  }
};
