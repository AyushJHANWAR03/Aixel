# Implementation Checklist: AI Customer Journey Tracker

Step-by-step guide to build the complete system from scratch.

---

## Step 1: Repository Skeleton & Dependencies

**Goal**: Create folder structure and dependency files

**Tasks**:
- [ ] Create directories: `backend/`, `dashboard/`, `demo_site/`, `scripts/`, `sql/`, `tests/`
- [ ] Create `requirements.txt` with dependencies:
  ```
  fastapi==0.104.1
  uvicorn==0.24.0
  sqlalchemy==2.0.23
  psycopg2-binary==2.9.9
  pydantic==2.5.0
  python-dotenv==1.0.0
  streamlit==1.28.2
  requests==2.31.0
  openai==1.3.5
  anthropic==0.7.0
  pandas==2.1.3
  plotly==5.18.0
  pytest==7.4.3
  ```
- [ ] Create `.env.example`:
  ```
  DATABASE_URL=postgresql://postgres:postgres@localhost:5432/aijourney
  OPENAI_API_KEY=sk-your-key-here
  API_BASE=http://localhost:8000
  ```
- [ ] Create `.gitignore` (Python, .env, __pycache__, .pytest_cache, etc.)

**Expected Output**: Clean folder structure ready for code

---

## Step 2: Database Schema & Docker Compose

**Goal**: Set up Postgres with schema

**Tasks**:
- [ ] Create `docker-compose.yml`:
  ```yaml
  version: '3.8'
  services:
    postgres:
      image: postgres:14
      environment:
        POSTGRES_USER: postgres
        POSTGRES_PASSWORD: postgres
        POSTGRES_DB: aijourney
      ports:
        - "5432:5432"
      volumes:
        - postgres_data:/var/lib/postgresql/data

    pgadmin:
      image: dpage/pgadmin4
      environment:
        PGADMIN_DEFAULT_EMAIL: admin@example.com
        PGADMIN_DEFAULT_PASSWORD: admin
      ports:
        - "5050:80"
      depends_on:
        - postgres

  volumes:
    postgres_data:
  ```

- [ ] Create `sql/schema.sql`:
  ```sql
  CREATE EXTENSION IF NOT EXISTS "pgcrypto";

  CREATE TABLE events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type text NOT NULL,
    timestamp timestamptz NOT NULL DEFAULT now(),
    session_id text,
    user_id text,
    page_url text,
    utm_source text,
    utm_medium text,
    utm_campaign text,
    platform text,
    device text,
    revenue numeric,
    metadata jsonb
  );

  CREATE INDEX idx_events_timestamp ON events (timestamp);
  CREATE INDEX idx_events_session ON events (session_id);
  ```

- [ ] Test: `docker-compose up -d` and verify Postgres is running
- [ ] Apply schema: `psql postgresql://postgres:postgres@localhost:5432/aijourney < sql/schema.sql`

**Expected Output**: Running Postgres with `events` table created

---

## Step 3: FastAPI Backend - Database Layer

**Goal**: Set up database connection and models

**Tasks**:
- [ ] Create `backend/__init__.py` (empty)
- [ ] Create `backend/db.py`:
  ```python
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker, declarative_base
  import os
  from dotenv import load_dotenv

  load_dotenv()

  DATABASE_URL = os.getenv("DATABASE_URL")
  engine = create_engine(DATABASE_URL)
  SessionLocal = sessionmaker(bind=engine)
  Base = declarative_base()

  def get_db():
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()
  ```

- [ ] Create `backend/models.py`:
  ```python
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
  ```

**Expected Output**: Database connection and Pydantic models ready

---

## Step 4: FastAPI Backend - CRUD Operations

**Goal**: Implement database operations

**Tasks**:
- [ ] Create `backend/crud.py`:
  ```python
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
                  :revenue, :metadata::jsonb
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
  ```

**Expected Output**: CRUD functions for event tracking and funnel queries

---

## Step 5: FastAPI Backend - API Endpoints

**Goal**: Create REST API

**Tasks**:
- [ ] Create `backend/main.py`:
  ```python
  from fastapi import FastAPI, HTTPException
  from fastapi.middleware.cors import CORSMiddleware
  from .models import EventCreate, FunnelMetrics, InsightsRequest, InsightsResponse
  from .crud import create_event, get_funnel_metrics
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

  @app.get("/health")
  def health_check():
      return {"status": "healthy"}
  ```

- [ ] Test: Run `uvicorn backend.main:app --reload` and check http://localhost:8000/docs

**Expected Output**: FastAPI server running with 4 endpoints

---

## Step 6: AI Integration - OpenAI Client

**Goal**: Implement LLM-based insights generation

**Tasks**:
- [ ] Create `backend/openai_client.py`:
  ```python
  import os
  import json
  from openai import OpenAI
  from dotenv import load_dotenv

  load_dotenv()

  client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

  INSIGHTS_PROMPT = """You are a marketing analyst. Given these aggregated funnel metrics (JSON), return 3 short observations and 3 action recommendations in JSON format.

  Keep each sentence concise and focused on conversions or campaign actions.

  Return ONLY valid JSON in this exact format:
  {
    "observations": ["observation 1", "observation 2", "observation 3"],
    "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"]
  }

  Metrics:
  {metrics}
  """

  def generate_insights(metrics: dict) -> dict:
      """Call OpenAI API to generate insights from metrics"""

      # Fallback mock if no API key
      if not os.getenv("OPENAI_API_KEY"):
          return {
              "observations": [
                  "Conversion rate from landing to purchase is 4.8%",
                  "Mobile users have 50% lower conversion than desktop",
                  "Google campaigns drive 60% of traffic but only 40% of purchases"
              ],
              "recommendations": [
                  "Optimize mobile checkout flow to reduce friction",
                  "Increase budget for high-converting Facebook campaigns",
                  "A/B test landing page CTAs to improve product view rate"
              ]
          }

      try:
          prompt = INSIGHTS_PROMPT.format(metrics=json.dumps(metrics, indent=2))

          response = client.chat.completions.create(
              model="gpt-4-turbo-preview",
              messages=[
                  {"role": "system", "content": "You are a marketing analytics expert."},
                  {"role": "user", "content": prompt}
              ],
              temperature=0.7,
              max_tokens=500
          )

          content = response.choices[0].message.content
          # Parse JSON from response
          insights = json.loads(content)

          return insights

      except Exception as e:
          print(f"Error generating insights: {e}")
          # Return fallback on error
          return {
              "observations": ["Error generating insights. Using fallback."],
              "recommendations": ["Please check API key and try again."]
          }
  ```

**Expected Output**: Working AI insights generator with fallback

---

## Step 7: Demo Site - Event Tracking

**Goal**: Create static HTML site that tracks user events

**Tasks**:
- [ ] Create `demo_site/index.html`:
  ```html
  <!DOCTYPE html>
  <html lang="en">
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Aixel Demo Store</title>
      <style>
          body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
          .header { background: #2563eb; color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
          .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
          .product { border: 1px solid #ddd; padding: 20px; border-radius: 8px; cursor: pointer; }
          .product:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
          .product img { width: 100%; height: 200px; object-fit: cover; border-radius: 4px; }
          .cta-button { background: #2563eb; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; }
          .cta-button:hover { background: #1d4ed8; }
          #cart { position: fixed; top: 20px; right: 20px; background: white; padding: 15px; border: 2px solid #2563eb; border-radius: 8px; }
      </style>
  </head>
  <body>
      <div class="header">
          <h1>Aixel Demo Store</h1>
          <p>Experience our AI-powered product recommendations</p>
      </div>

      <div id="cart">Cart: <span id="cart-count">0</span> items</div>

      <div class="product-grid" id="products"></div>

      <script src="tracking.js"></script>
  </body>
  </html>
  ```

- [ ] Create `demo_site/tracking.js`:
  ```javascript
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

  // Track event
  async function trackEvent(eventType, extraData = {}) {
      const event = {
          event_type: eventType,
          session_id: getSessionId(),
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
          await fetch(`${API_BASE}/api/track`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(event)
          });
          console.log('Tracked:', eventType);
      } catch (error) {
          console.error('Tracking error:', error);
      }
  }

  // Track landing page view
  trackEvent('page_view', { metadata: { landing: true } });

  // Simulate ad click if UTM params present
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('utm_source')) {
      trackEvent('ad_click');
  }

  // Render products
  const products = [
      { id: 1, name: 'AI Analytics Pro', price: 299, img: 'https://via.placeholder.com/200' },
      { id: 2, name: 'Marketing Dashboard', price: 199, img: 'https://via.placeholder.com/200' },
      { id: 3, name: 'Customer Insights', price: 399, img: 'https://via.placeholder.com/200' },
      { id: 4, name: 'Journey Tracker', price: 249, img: 'https://via.placeholder.com/200' },
  ];

  const productsContainer = document.getElementById('products');
  let cartCount = 0;

  products.forEach(product => {
      const productDiv = document.createElement('div');
      productDiv.className = 'product';
      productDiv.innerHTML = `
          <img src="${product.img}" alt="${product.name}">
          <h3>${product.name}</h3>
          <p>$${product.price}</p>
          <button class="cta-button" onclick="addToCart(${product.id}, '${product.name}', ${product.price})">
              Add to Cart
          </button>
      `;

      productDiv.addEventListener('click', (e) => {
          if (!e.target.classList.contains('cta-button')) {
              trackEvent('product_view', { metadata: { product_id: product.id, product_name: product.name } });
          }
      });

      productsContainer.appendChild(productDiv);
  });

  function addToCart(productId, productName, price) {
      trackEvent('add_to_cart', {
          metadata: { product_id: productId, product_name: productName, price: price }
      });

      cartCount++;
      document.getElementById('cart-count').textContent = cartCount;

      // Simulate checkout flow
      setTimeout(() => {
          if (confirm('Proceed to checkout?')) {
              trackEvent('checkout_start');
              setTimeout(() => {
                  trackEvent('purchase', { revenue: price });
                  alert('Purchase complete! Thank you.');
                  cartCount = 0;
                  document.getElementById('cart-count').textContent = cartCount;
              }, 1000);
          }
      }, 500);
  }
  ```

- [ ] Test: Open demo site at http://localhost:8080 and verify events are tracked

**Expected Output**: Interactive demo site that sends events to backend

---

## Step 8: Streamlit Dashboard

**Goal**: Create dashboard to visualize funnel and insights

**Tasks**:
- [ ] Create `dashboard/streamlit_app.py`:
  ```python
  import streamlit as st
  import requests
  import pandas as pd
  import plotly.graph_objects as go
  import os
  from dotenv import load_dotenv

  load_dotenv()

  API_BASE = os.getenv("API_BASE", "http://localhost:8000")

  st.set_page_config(page_title="AI Journey Tracker", layout="wide")

  st.title("🎯 AI Customer Journey Tracker")
  st.markdown("Real-time funnel analytics with AI-powered insights")

  # Sidebar filters
  st.sidebar.header("Filters")
  hours = st.sidebar.selectbox("Time Range", [24, 72, 168, 720], index=2)

  # Fetch funnel data
  @st.cache_data(ttl=60)
  def get_funnel_data(hours):
      response = requests.get(f"{API_BASE}/api/funnel?hours={hours}")
      return response.json()

  # Fetch insights
  def get_ai_insights(metrics):
      response = requests.post(f"{API_BASE}/api/generate_insights", json={"metrics": metrics})
      return response.json()

  # Main dashboard
  try:
      metrics = get_funnel_data(hours)

      # KPI cards
      col1, col2, col3, col4, col5 = st.columns(5)

      with col1:
          st.metric("Ad Clicks", f"{metrics['ad_clicks']:,}")
      with col2:
          st.metric("Landings", f"{metrics['landings']:,}")
      with col3:
          st.metric("Product Views", f"{metrics['product_views']:,}")
      with col4:
          st.metric("Adds to Cart", f"{metrics['adds']:,}")
      with col5:
          st.metric("Purchases", f"{metrics['purchases']:,}")

      # Calculate conversion rates
      landing_to_purchase = (metrics['purchases'] / metrics['landings'] * 100) if metrics['landings'] > 0 else 0
      cart_to_purchase = (metrics['purchases'] / metrics['adds'] * 100) if metrics['adds'] > 0 else 0

      st.markdown("---")

      col1, col2 = st.columns(2)

      with col1:
          st.subheader("📊 Conversion Funnel")

          # Funnel chart
          stages = ['Ad Clicks', 'Landings', 'Product Views', 'Add to Cart', 'Purchases']
          values = [
              metrics['ad_clicks'],
              metrics['landings'],
              metrics['product_views'],
              metrics['adds'],
              metrics['purchases']
          ]

          fig = go.Figure(go.Funnel(
              y=stages,
              x=values,
              textinfo="value+percent initial",
              marker={"color": ["#3b82f6", "#2563eb", "#1d4ed8", "#1e40af", "#1e3a8a"]}
          ))

          fig.update_layout(height=400)
          st.plotly_chart(fig, use_container_width=True)

          # Conversion metrics
          st.metric("Landing → Purchase", f"{landing_to_purchase:.1f}%")
          st.metric("Cart → Purchase", f"{cart_to_purchase:.1f}%")

      with col2:
          st.subheader("🤖 AI-Generated Insights")

          if st.button("Generate Fresh Insights", type="primary"):
              with st.spinner("Analyzing funnel data..."):
                  insights = get_ai_insights(metrics)
                  st.session_state['insights'] = insights

          if 'insights' in st.session_state:
              insights = st.session_state['insights']

              st.markdown("**📈 Observations:**")
              for obs in insights['observations']:
                  st.markdown(f"- {obs}")

              st.markdown("**💡 Recommendations:**")
              for rec in insights['recommendations']:
                  st.markdown(f"- {rec}")
          else:
              st.info("Click 'Generate Fresh Insights' to get AI-powered recommendations")

      # Data table
      st.markdown("---")
      st.subheader("📋 Funnel Metrics Summary")

      df = pd.DataFrame([metrics])
      st.dataframe(df, use_container_width=True)

  except Exception as e:
      st.error(f"Error loading data: {str(e)}")
      st.info("Make sure the FastAPI backend is running at http://localhost:8000")

  ```

- [ ] Test: Run `streamlit run dashboard/streamlit_app.py` and open http://localhost:8501

**Expected Output**: Interactive dashboard showing funnel metrics and AI insights

---

## Step 9: Seed Script for Testing

**Goal**: Generate synthetic events for demo

**Tasks**:
- [ ] Create `scripts/seed_events.py`:
  ```python
  import requests
  import random
  import uuid
  import time
  from datetime import datetime, timedelta

  API_BASE = 'http://localhost:8000/api/track'

  UTM_SOURCES = ['google', 'facebook', 'twitter', 'linkedin', 'direct']
  DEVICES = ['desktop', 'mobile', 'tablet']
  PRODUCTS = ['AI Analytics Pro', 'Marketing Dashboard', 'Customer Insights', 'Journey Tracker']

  def generate_session():
      """Simulate a single user session through the funnel"""
      session_id = str(uuid.uuid4())
      utm_source = random.choice(UTM_SOURCES)
      device = random.choice(DEVICES)
      timestamp_base = datetime.utcnow() - timedelta(hours=random.randint(0, 168))

      # Ad click (80% of sessions start with ad click)
      if random.random() < 0.8:
          requests.post(API_BASE, json={
              "event_type": "ad_click",
              "session_id": session_id,
              "timestamp": timestamp_base.isoformat(),
              "utm_source": utm_source,
              "device": device,
              "metadata": {}
          })
          time.sleep(0.001)

      # Landing page view (always happens)
      requests.post(API_BASE, json={
          "event_type": "page_view",
          "session_id": session_id,
          "timestamp": (timestamp_base + timedelta(seconds=2)).isoformat(),
          "page_url": "/landing",
          "utm_source": utm_source,
          "device": device,
          "metadata": {"landing": True}
      })
      time.sleep(0.001)

      # Product view (60% conversion)
      if random.random() < 0.6:
          product = random.choice(PRODUCTS)
          requests.post(API_BASE, json={
              "event_type": "product_view",
              "session_id": session_id,
              "timestamp": (timestamp_base + timedelta(seconds=15)).isoformat(),
              "utm_source": utm_source,
              "device": device,
              "metadata": {"product_name": product}
          })
          time.sleep(0.001)

          # Add to cart (40% of product viewers)
          if random.random() < 0.4:
              requests.post(API_BASE, json={
                  "event_type": "add_to_cart",
                  "session_id": session_id,
                  "timestamp": (timestamp_base + timedelta(seconds=30)).isoformat(),
                  "utm_source": utm_source,
                  "device": device,
                  "metadata": {"product_name": product}
              })
              time.sleep(0.001)

              # Purchase (50% of cart adds - lower for mobile)
              purchase_rate = 0.3 if device == 'mobile' else 0.5
              if random.random() < purchase_rate:
                  revenue = random.randint(199, 399)
                  requests.post(API_BASE, json={
                      "event_type": "purchase",
                      "session_id": session_id,
                      "timestamp": (timestamp_base + timedelta(seconds=45)).isoformat(),
                      "utm_source": utm_source,
                      "device": device,
                      "revenue": revenue,
                      "metadata": {"product_name": product}
                  })
                  time.sleep(0.001)

  def main():
      num_sessions = 1000
      print(f"Generating {num_sessions} synthetic sessions...")

      for i in range(num_sessions):
          try:
              generate_session()
              if (i + 1) % 100 == 0:
                  print(f"Generated {i + 1}/{num_sessions} sessions")
          except Exception as e:
              print(f"Error in session {i}: {e}")
              continue

      print(f"\n✅ Successfully generated {num_sessions} sessions!")
      print("View results at: http://localhost:8501")

  if __name__ == "__main__":
      main()
  ```

- [ ] Test: Run `python scripts/seed_events.py` and verify events in dashboard

**Expected Output**: 1000+ events inserted into database

---

## Step 10: Tests

**Goal**: Add basic tests for API endpoints

**Tasks**:
- [ ] Create `tests/__init__.py` (empty)
- [ ] Create `tests/test_api.py`:
  ```python
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
  ```

- [ ] Run tests: `pytest tests/ -v`

**Expected Output**: All tests passing

---

## Step 11: Documentation

**Goal**: Create comprehensive README

**Tasks**:
- [ ] Create `README.md`:
  ```markdown
  # AI Customer Journey Tracker & Insights Dashboard

  Real-time customer journey analytics with AI-powered insights for marketing optimization.

  ## Features

  - 📊 Real-time event tracking through marketing funnel
  - 🎯 Multi-stage conversion analysis (Ad Click → Purchase)
  - 🤖 AI-generated insights and recommendations
  - 📈 Interactive Streamlit dashboard
  - 🔄 Demo site for testing event flows
  - 🚀 FastAPI backend with Postgres

  ## Quick Start

  ### 1. Prerequisites

  - Python 3.11+
  - Docker & Docker Compose
  - OpenAI API key (optional - falls back to mock insights)

  ### 2. Setup

  ```bash
  # Clone repo
  git clone <repo-url>
  cd Aixel

  # Create .env file
  cp .env.example .env
  # Edit .env and add your OPENAI_API_KEY

  # Start Postgres
  docker-compose up -d

  # Install dependencies
  pip install -r requirements.txt

  # Apply database schema
  psql postgresql://postgres:postgres@localhost:5432/aijourney < sql/schema.sql
  ```

  ### 3. Run Services

  ```bash
  # Terminal 1: Start FastAPI backend
  uvicorn backend.main:app --reload

  # Terminal 2: Start Streamlit dashboard
  streamlit run dashboard/streamlit_app.py

  # Terminal 3: Serve demo site (optional)
  cd demo_site && python -m http.server 8080
  ```

  ### 4. Generate Test Data

  ```bash
  # Seed 1000 synthetic sessions
  python scripts/seed_events.py
  ```

  ### 5. View Dashboard

  Open http://localhost:8501 and click "Generate Fresh Insights"

  ## Architecture

  ```
  Demo Site (HTML/JS) ──────┐
                             ├──> FastAPI Backend ──> Postgres
  Streamlit Dashboard ──────┘          │
                                       └──> OpenAI API
  ```

  ## API Endpoints

  - `POST /api/track` - Ingest events
  - `GET /api/funnel?hours=168` - Get funnel metrics
  - `POST /api/generate_insights` - Generate AI insights
  - `GET /health` - Health check

  ## Environment Variables

  ```
  DATABASE_URL=postgresql://postgres:postgres@localhost:5432/aijourney
  OPENAI_API_KEY=sk-...
  API_BASE=http://localhost:8000
  ```

  ## Testing

  ```bash
  # Run API tests
  pytest tests/ -v

  # Manual testing
  curl http://localhost:8000/health
  ```

  ## Project Structure

  ```
  /backend/          - FastAPI application
  /dashboard/        - Streamlit dashboard
  /demo_site/        - Static HTML demo site
  /scripts/          - Seed data scripts
  /sql/              - Database schema
  /tests/            - API tests
  ```

  ## Demo Workflow

  1. Start all services (Postgres, FastAPI, Streamlit)
  2. Run seed script to generate 1000+ sessions
  3. Open dashboard to view funnel metrics
  4. Click "Generate AI Insights" for recommendations
  5. Interact with demo site to create live events

  ## Tech Stack

  - **Backend**: FastAPI, SQLAlchemy, Postgres
  - **Dashboard**: Streamlit, Plotly
  - **AI**: OpenAI GPT-4
  - **Infrastructure**: Docker Compose

  ## License

  MIT
  ```

**Expected Output**: Complete README with quick start guide

---

## Step 12: Final Polish & Validation

**Goal**: Ensure everything works end-to-end

**Tasks**:
- [ ] Verify all services start without errors
- [ ] Test full workflow: seed → dashboard → insights
- [ ] Check that demo site tracks events correctly
- [ ] Verify AI insights generate (with and without API key)
- [ ] Run test suite and ensure all pass
- [ ] Review code for TODOs and fix any remaining issues
- [ ] Test on fresh environment (optional)

**Expected Output**: Fully working demo ready to present

---

## Success Criteria

✅ Demo site sends events → backend stores them
✅ Dashboard displays funnel metrics that update after seeding
✅ AI insights button returns observations + recommendations
✅ README has clear run instructions
✅ All services can start with one command each
✅ Tests pass

---

## Next Steps After MVP

Consider adding:
- Real-time dashboard updates (WebSocket)
- Cohort analysis
- A/B test tracking
- Multi-touch attribution
- Campaign ROI calculator
- Export to CSV/PDF
- User authentication
- Rate limiting
- Caching layer (Redis)
