import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
from dotenv import load_dotenv
import time

load_dotenv()

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(
    page_title="AI Journey Tracker - Admin",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🎯"
)

# STUNNING CUSTOM CSS
st.markdown("""
<style>
    /* Main background with animated gradient */
    .main {
        background: linear-gradient(-45deg, #0f172a, #1e1b4b, #1e3a8a, #0f172a);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Header styling */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
        animation: glow 2s ease-in-out infinite alternate;
    }

    @keyframes glow {
        from { filter: drop-shadow(0 0 5px #667eea); }
        to { filter: drop-shadow(0 0 20px #764ba2); }
    }

    .sub-header {
        font-size: 1.2rem;
        color: #a5b4fc;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 300;
    }

    /* Metric cards with glass morphism */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        transition: all 0.3s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(102, 126, 234, 0.5);
        border-color: rgba(102, 126, 234, 0.5);
    }

    div[data-testid="stMetric"] label {
        color: #e0e7ff !important;
        font-weight: 600;
        font-size: 0.9rem;
    }

    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem;
        font-weight: 700;
    }

    /* AI Insights section - STUNNING */
    .insight-container {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 25px;
        border: 2px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.4), inset 0 0 20px rgba(102, 126, 234, 0.1);
        margin: 15px 0;
        animation: pulse-glow 3s ease-in-out infinite;
    }

    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.4), inset 0 0 20px rgba(102, 126, 234, 0.1); }
        50% { box-shadow: 0 12px 40px 0 rgba(102, 126, 234, 0.6), inset 0 0 30px rgba(118, 75, 162, 0.2); }
    }

    .insight-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 15px 20px;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin: 12px 0;
        color: #e0e7ff;
        font-size: 1.05rem;
        line-height: 1.6;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    .insight-box:hover {
        transform: translateX(10px);
        background: rgba(102, 126, 234, 0.15);
        border-left-color: #f093fb;
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
    }

    .insight-header {
        color: #fbbf24;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 15px 0 10px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Event cards */
    .event-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.15);
        transition: all 0.3s ease;
        color: #e0e7ff;
    }

    .event-card:hover {
        background: rgba(102, 126, 234, 0.2);
        transform: translateX(5px);
        border-color: rgba(102, 126, 234, 0.5);
    }

    /* Section headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #e0e7ff;
        margin: 25px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
        display: flex;
        align-items: center;
        gap: 12px;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1.05rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #0f172a 100%);
        border-right: 1px solid rgba(102, 126, 234, 0.2);
    }

    section[data-testid="stSidebar"] h2 {
        color: #e0e7ff;
    }

    section[data-testid="stSidebar"] label {
        color: #cbd5e1;
    }

    /* DataFrame styling */
    .dataframe {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #e0e7ff !important;
        border-radius: 10px;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .animated {
        animation: slideIn 0.6s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.markdown("## ⚙️ Dashboard Controls")

# Time range filter
time_range_options = {
    "Last 24 Hours ⏰": 24,
    "Last 3 Days 📅": 72,
    "Last Week 📊": 168,
    "Last Month 📈": 720
}
selected_range = st.sidebar.selectbox(
    "Time Range",
    options=list(time_range_options.keys()),
    index=2
)
hours = time_range_options[selected_range]

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=False)
if auto_refresh:
    time.sleep(30)
    st.rerun()

# Manual refresh button
if st.sidebar.button("⚡ Refresh Dashboard", type="primary", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 Quick Access")
st.sidebar.markdown("- 📚 [API Documentation](http://localhost:8000/docs)")
st.sidebar.markdown("- 🛍️ [Customer Portal](http://localhost:8080)")
st.sidebar.markdown("- 🗄️ [Database Admin](http://localhost:5050)")

# Main dashboard header
st.markdown('<div class="main-header">🎯 AI CUSTOMER JOURNEY TRACKER</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Real-time Analytics & AI-Powered Insights • {selected_range}</div>', unsafe_allow_html=True)

# Fetch all data
@st.cache_data(ttl=60)
def fetch_all_data(hours):
    try:
        funnel = requests.get(f"{API_BASE}/api/funnel?hours={hours}").json()
        users = requests.get(f"{API_BASE}/api/user_analytics?hours={hours}").json()
        campaigns = requests.get(f"{API_BASE}/api/campaign_performance?hours={hours}").json()
        revenue = requests.get(f"{API_BASE}/api/revenue_metrics?hours={hours}").json()
        timeline = requests.get(f"{API_BASE}/api/event_timeline?hours={hours}").json()
        recent = requests.get(f"{API_BASE}/api/recent_events?limit=15").json()
        return funnel, users, campaigns, revenue, timeline, recent
    except Exception as e:
        st.error(f"⚠️ Error fetching data: {str(e)}")
        return None, None, None, None, None, None

# Fetch AI insights
def get_ai_insights(metrics):
    try:
        response = requests.post(f"{API_BASE}/api/generate_insights", json={"metrics": metrics}, timeout=30)
        return response.json()
    except Exception as e:
        st.error(f"⚠️ AI Insights Error: {str(e)}")
        return None

with st.spinner("🔮 Loading dashboard data..."):
    funnel_data, user_data, campaign_data, revenue_data, timeline_data, recent_events = fetch_all_data(hours)

if not funnel_data:
    st.error("❌ Failed to load data. Make sure FastAPI is running at http://localhost:8000")
    st.stop()

# ======================
# KEY METRICS ROW
# ======================
st.markdown('<div class="section-header">📊 KEY PERFORMANCE INDICATORS</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        "Total Events",
        f"{user_data['total_events']:,}",
        delta=None,
        help="Total tracked events"
    )

with col2:
    st.metric(
        "Active Users",
        f"{user_data['total_users']:,}",
        delta=f"+{user_data['new_users']}" if user_data['new_users'] > 0 else None,
        help="Unique active users"
    )

with col3:
    st.metric(
        "Sessions",
        f"{user_data['total_sessions']:,}",
        delta=None,
        help="Total user sessions"
    )

with col4:
    st.metric(
        "Purchases",
        f"{revenue_data['total_purchases']:,}",
        delta=None,
        help="Completed purchases"
    )

with col5:
    st.metric(
        "Revenue",
        f"${revenue_data['total_revenue']:,.0f}",
        delta=None,
        help="Total revenue generated"
    )

with col6:
    avg_order = revenue_data['avg_order_value']
    st.metric(
        "AOV",
        f"${avg_order:.0f}",
        delta=None,
        help="Average Order Value"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ======================
# AI INSIGHTS - STUNNING SECTION
# ======================
st.markdown('<div class="section-header">🤖 AI-POWERED INSIGHTS</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown('<div class="insight-container">', unsafe_allow_html=True)

    col_btn, col_info = st.columns([2, 3])
    with col_btn:
        if st.button("✨ Generate AI Insights", type="primary", use_container_width=True):
            with st.spinner("🧠 AI is analyzing your customer journey data..."):
                combined_metrics = {
                    **funnel_data,
                    **user_data,
                    **revenue_data,
                    "conversion_rate": (funnel_data['purchases'] / funnel_data['landings'] * 100) if funnel_data['landings'] > 0 else 0
                }
                insights = get_ai_insights(combined_metrics)
                if insights and 'observations' in insights and 'recommendations' in insights:
                    st.session_state['insights'] = insights
                    st.session_state['insights_time'] = datetime.now()
                    st.success("✅ AI Insights Generated!")
                    st.rerun()

    with col_info:
        if 'insights_time' in st.session_state:
            insight_time = st.session_state.get('insights_time')
            if insight_time:
                st.caption(f"🕐 Last updated: {insight_time.strftime('%H:%M:%S')}")

    if 'insights' in st.session_state:
        insights = st.session_state.get('insights')

        if insights and isinstance(insights, dict) and 'observations' in insights:
            st.markdown('<div class="insight-header">📈 Key Observations</div>', unsafe_allow_html=True)
            for obs in insights.get('observations', []):
                st.markdown(f'<div class="insight-box">• {obs}</div>', unsafe_allow_html=True)

            st.markdown('<div class="insight-header">💡 Recommended Actions</div>', unsafe_allow_html=True)
            for rec in insights.get('recommendations', []):
                st.markdown(f'<div class="insight-box">→ {rec}</div>', unsafe_allow_html=True)
        else:
            st.info("🎯 Click 'Generate AI Insights' to get intelligent recommendations powered by OpenAI")
    else:
        st.info("🎯 Click 'Generate AI Insights' to get intelligent recommendations powered by OpenAI")

    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    # Conversion funnel
    st.markdown("#### 🔄 Conversion Funnel")

    stages = ['Ad Clicks', 'Landings', 'Views', 'Cart', 'Purchase']
    values = [
        funnel_data['ad_clicks'],
        funnel_data['landings'],
        funnel_data['product_views'],
        funnel_data['adds'],
        funnel_data['purchases']
    ]

    fig_funnel = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textinfo="value+percent initial",
        marker={
            "color": ["#667eea", "#764ba2", "#f093fb", "#f59e0b", "#10b981"],
            "line": {"width": 3, "color": "rgba(255,255,255,0.3)"}
        },
        textfont={"size": 13, "color": "white", "family": "Arial Black"}
    ))

    fig_funnel.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

    # Conversion rates
    col_a, col_b, col_c = st.columns(3)

    landing_to_purchase = (funnel_data['purchases'] / funnel_data['landings'] * 100) if funnel_data['landings'] > 0 else 0
    cart_to_purchase = (funnel_data['purchases'] / funnel_data['adds'] * 100) if funnel_data['adds'] > 0 else 0
    click_to_landing = (funnel_data['landings'] / funnel_data['ad_clicks'] * 100) if funnel_data['ad_clicks'] > 0 else 0

    with col_a:
        st.metric("Ad→Landing", f"{click_to_landing:.1f}%")
    with col_b:
        st.metric("Landing→Buy", f"{landing_to_purchase:.1f}%")
    with col_c:
        st.metric("Cart→Buy", f"{cart_to_purchase:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# ======================
# TIMELINE CHART
# ======================
st.markdown('<div class="section-header">📈 EVENTS TIMELINE</div>', unsafe_allow_html=True)

if timeline_data and len(timeline_data) > 0:
    timeline_df = pd.DataFrame(timeline_data)
    timeline_df['timestamp'] = pd.to_datetime(timeline_df['timestamp'])

    fig_timeline = go.Figure()

    metrics_to_plot = [
        ('purchases', 'Purchases', '#10b981', 'circle'),
        ('adds', 'Cart Adds', '#f59e0b', 'diamond'),
        ('product_views', 'Product Views', '#8b5cf6', 'square'),
        ('page_views', 'Page Views', '#667eea', 'triangle-up'),
        ('ad_clicks', 'Ad Clicks', '#ec4899', 'star')
    ]

    for metric, name, color, symbol in metrics_to_plot:
        fig_timeline.add_trace(go.Scatter(
            x=timeline_df['timestamp'],
            y=timeline_df[metric],
            mode='lines+markers',
            name=name,
            line=dict(color=color, width=3),
            marker=dict(size=8, symbol=symbol, line=dict(width=2, color='white'))
        ))

    fig_timeline.update_layout(
        height=450,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title="Time",
            gridcolor='rgba(255,255,255,0.1)',
            color='white'
        ),
        yaxis=dict(
            title="Event Count",
            gridcolor='rgba(255,255,255,0.1)',
            color='white'
        ),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(0,0,0,0.3)',
            font=dict(color='white')
        ),
        font=dict(color='white')
    )

    st.plotly_chart(fig_timeline, use_container_width=True)
else:
    st.info("📊 No timeline data available")

st.markdown("<br>", unsafe_allow_html=True)

# ======================
# USER ANALYTICS & CAMPAIGN PERFORMANCE
# ======================
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">👥 USER ANALYTICS</div>', unsafe_allow_html=True)

    user_metrics = pd.DataFrame({
        'Metric': ['Total Users', 'New Users', 'Returning', 'Sessions'],
        'Value': [
            user_data['total_users'],
            user_data['new_users'],
            user_data['returning_users'],
            user_data['total_sessions']
        ]
    })

    fig_users = px.bar(
        user_metrics,
        x='Metric',
        y='Value',
        text='Value',
        color='Metric',
        color_discrete_sequence=['#667eea', '#10b981', '#f59e0b', '#8b5cf6']
    )
    fig_users.update_traces(
        texttemplate='%{text:,}',
        textposition='outside',
        textfont=dict(size=14, color='white', family='Arial Black')
    )
    fig_users.update_layout(
        height=350,
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title="", gridcolor='rgba(255,255,255,0.1)', color='white'),
        yaxis=dict(title="Count", gridcolor='rgba(255,255,255,0.1)', color='white'),
        font=dict(color='white')
    )
    st.plotly_chart(fig_users, use_container_width=True)

    sessions_per_user = user_data['total_sessions'] / user_data['total_users'] if user_data['total_users'] > 0 else 0
    events_per_session = user_data['total_events'] / user_data['total_sessions'] if user_data['total_sessions'] > 0 else 0

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Sessions/User", f"{sessions_per_user:.2f}")
    with col_b:
        st.metric("Events/Session", f"{events_per_session:.1f}")

with col2:
    st.markdown('<div class="section-header">🎯 CAMPAIGN PERFORMANCE</div>', unsafe_allow_html=True)

    if campaign_data and len(campaign_data) > 0:
        campaign_df = pd.DataFrame(campaign_data)

        fig_campaigns = px.bar(
            campaign_df.head(6),
            x='campaign',
            y='revenue',
            text='revenue',
            color='clicks',
            color_continuous_scale='Plasma'
        )
        fig_campaigns.update_traces(
            texttemplate='$%{text:.0f}',
            textposition='outside',
            textfont=dict(size=13, color='white', family='Arial Black')
        )
        fig_campaigns.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title="", gridcolor='rgba(255,255,255,0.1)', color='white'),
            yaxis=dict(title="Revenue ($)", gridcolor='rgba(255,255,255,0.1)', color='white'),
            font=dict(color='white')
        )
        st.plotly_chart(fig_campaigns, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            total_clicks = sum([c['clicks'] for c in campaign_data])
            st.metric("Total Clicks", f"{total_clicks:,}")
        with col_b:
            total_campaign_revenue = sum([c['revenue'] for c in campaign_data])
            st.metric("Campaign Revenue", f"${total_campaign_revenue:.0f}")
    else:
        st.info("📊 No campaign data available")

st.markdown("<br>", unsafe_allow_html=True)

# ======================
# RECENT EVENTS FEED
# ======================
st.markdown('<div class="section-header">🔔 LIVE EVENTS FEED</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    if recent_events and len(recent_events) > 0:
        for event in recent_events:
            event_type = event['event_type']
            timestamp = datetime.fromisoformat(event['timestamp']) if event['timestamp'] else None
            time_str = timestamp.strftime('%H:%M:%S') if timestamp else 'N/A'

            emoji_map = {
                'ad_click': '📢',
                'page_view': '👁️',
                'product_view': '🛍️',
                'add_to_cart': '🛒',
                'purchase': '💰',
                'user_login': '🔑',
                'user_signup': '✨',
                'checkout_start': '💳'
            }

            emoji = emoji_map.get(event_type, '📌')
            user_email = event.get('user_email') or event.get('user_name') or 'Anonymous'

            desc = f"{emoji} **{event_type.replace('_', ' ').title()}**"
            if event.get('product_name'):
                desc += f" - {event['product_name']}"
            if event.get('revenue', 0) > 0:
                desc += f" **(${event['revenue']:.2f})**"
            desc += f" | 👤 {user_email} | 🎯 {event.get('campaign', 'direct')} | 🕐 {time_str}"

            st.markdown(f'<div class="event-card">{desc}</div>', unsafe_allow_html=True)
    else:
        st.info("📊 No recent events")

with col2:
    st.markdown("#### 💰 Revenue Stats")

    revenue_breakdown = pd.DataFrame({
        'Metric': ['Total Revenue', 'Avg Order', 'Max Order', 'Purchases'],
        'Value': [
            f"${revenue_data['total_revenue']:.2f}",
            f"${revenue_data['avg_order_value']:.2f}",
            f"${revenue_data['max_order_value']:.2f}",
            f"{revenue_data['total_purchases']}"
        ]
    })

    st.dataframe(revenue_breakdown, use_container_width=True, hide_index=True)

    revenue_per_session = revenue_data['total_revenue'] / user_data['total_sessions'] if user_data['total_sessions'] > 0 else 0
    st.metric("Revenue/Session", f"${revenue_per_session:.2f}")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<div style="text-align: center; color: #a5b4fc; padding: 2rem; font-size: 0.9rem;">',
    unsafe_allow_html=True
)
st.markdown("✨ **AI Customer Journey Tracker** | Powered by FastAPI • PostgreSQL • Streamlit • OpenAI ✨")
st.markdown("</div>", unsafe_allow_html=True)
