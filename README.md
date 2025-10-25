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
# Navigate to project directory
cd Aixel

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY (optional)

# Start Postgres
docker compose up -d

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
