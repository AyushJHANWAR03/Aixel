const API_BASE = 'http://localhost:8000';

// Session management
function getSessionId() {
    let sessionId = localStorage.getItem('session_id');
    if (!sessionId) {
        sessionId = generateUUID();
        localStorage.setItem('session_id', sessionId);
    }
    return sessionId;
}

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Visual tracking indicator
function showTrackingIndicator(message = '📊 Event Tracked!') {
    const indicator = document.getElementById('tracking-indicator');
    if (!indicator) return;

    indicator.textContent = message;
    indicator.classList.add('show');

    setTimeout(() => {
        indicator.classList.remove('show');
    }, 3000);
}

// Track event to backend
async function trackEvent(eventType, extraData = {}) {
    const user = JSON.parse(localStorage.getItem('aixel_user'));

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
        ...extraData
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
}

// Debug: Log session info on page load
console.log('🔍 Session ID:', getSessionId());
console.log('👤 User:', JSON.parse(localStorage.getItem('aixel_user')));
console.log('🛒 Cart:', JSON.parse(localStorage.getItem('aixel_cart'))?.length || 0, 'items');
