# AI Customer Journey Tracker & Insights Dashboard

Real-time customer journey analytics with AI-powered insights for marketing optimization.

> **Built for Aixel AI** - This project was created as a demonstration of full-stack capabilities and contribution to the Aixel AI team as a Backend SDE 1 candidate. It showcases end-to-end implementation of event tracking, analytics pipelines, and AI-powered insights generation.

## 🌐 Live Production Demo

- **Customer Portal**: https://aixel-frontend.onrender.com
- **Admin Dashboard**: https://aixel-dashboard.onrender.com
- **Backend API**: https://aixel-pw3d.onrender.com
- **API Documentation**: https://aixel-pw3d.onrender.com/docs

## ✨ Features

- 📊 **Real-time Event Tracking**: Complete user journey tracking from ad click to purchase
- 🎯 **Multi-stage Funnel Analysis**: Ad Click → Landing → Product View → Cart → Purchase
- 🤖 **AI-Powered Insights**: OpenAI GPT-4 integration for intelligent recommendations
- 📈 **Stunning Dashboard**: Interactive Streamlit dashboard with real-time charts and metrics
- 🛍️ **React Customer Portal**: Modern e-commerce interface with user authentication
- 🚀 **Production-Ready Backend**: FastAPI with PostgreSQL, automatic schema creation & data seeding
- 🔄 **Auto-Seeding**: Database automatically populated with 300 realistic sessions on first startup
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices
- 🎨 **UTM Campaign Tracking**: Full attribution across Google, Facebook, LinkedIn, and more

## 🚀 Quick Start

### Option 1: Use Production Demo (Easiest)

Just visit the live links above! The production deployment is fully functional with seeded data.

### Option 2: Run Locally

#### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- OpenAI API key (optional - falls back to mock insights)

#### Setup Backend & Database

```bash
# Clone repository
git clone https://github.com/AyushJHANWAR03/Aixel.git
cd Aixel

# Start PostgreSQL
docker compose up -d

# Install Python dependencies
pip install -r requirements.txt

# Backend automatically creates schema and seeds data on first run!
uvicorn backend.main:app --reload
```

Backend will be available at `http://localhost:8000`

#### Setup Dashboard

```bash
# In a new terminal
streamlit run dashboard/streamlit_app.py
```

Dashboard will open at `http://localhost:8501`

#### Setup React Frontend

```bash
# In a new terminal
cd demo_site

# Install dependencies
npm install

# Create environment file
echo "VITE_API_BASE=http://localhost:8000" > .env

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

#### Manual Data Seeding (Optional)

The backend auto-seeds on startup, but you can generate more data:

```bash
python scripts/seed_events.py
# Enter number of sessions when prompted (default: 500)
```

## 🏗️ Architecture

```
┌─────────────────────┐
│  React Frontend     │ ← Users browse products, add to cart, purchase
│  (Vite + React)     │
└──────────┬──────────┘
           │ POST /api/track (events)
           ▼
┌─────────────────────┐
│   FastAPI Backend   │ ← Event ingestion, analytics queries
│   (Python 3.11)     │
└──────────┬──────────┘
           │
           ├──> PostgreSQL (Event storage)
           └──> OpenAI API (Insights generation)
           ▲
           │ GET /api/funnel, /api/user_analytics, etc.
┌──────────┴──────────┐
│ Streamlit Dashboard │ ← Admin views metrics & AI insights
│  (Python + Plotly)  │
└─────────────────────┘
```

## 📡 API Endpoints

### Event Tracking
- `POST /api/track` - Ingest user events (clicks, views, purchases, etc.)

### Analytics
- `GET /api/funnel?hours=168` - Get funnel metrics (ad clicks → purchases)
- `GET /api/user_analytics?hours=168` - User statistics and session data
- `GET /api/campaign_performance?hours=168` - Campaign ROI and conversion rates
- `GET /api/revenue_metrics?hours=168` - Revenue totals and order values
- `GET /api/event_timeline?hours=168` - Time-series event data
- `GET /api/recent_events?limit=20` - Live event feed

### AI Insights
- `POST /api/generate_insights` - Generate AI-powered recommendations

### Health
- `GET /health` - Service health check

## ⚙️ Environment Variables

### Backend (`/.env`)
```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
OPENAI_API_KEY=sk-...  # Optional - uses fallback mock if not set
```

### Dashboard (`/.env`)
```bash
API_BASE=https://aixel-pw3d.onrender.com  # Backend API URL
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### Frontend (`/demo_site/.env`)
```bash
VITE_API_BASE=https://aixel-pw3d.onrender.com  # Backend API URL
```

## 🚢 Production Deployment

This project is deployed on **Render.com** with three services:

### Backend (Web Service)
- **Type**: Docker
- **Dockerfile**: `Dockerfile.backend`
- **Auto-Deploy**: Enabled on git push
- **Features**: Auto schema creation, auto-seeding on first run

### Dashboard (Web Service)
- **Type**: Docker
- **Dockerfile**: `Dockerfile.dashboard`
- **Auto-Deploy**: Enabled on git push

### Frontend (Static Site)
- **Type**: Static Site
- **Build**: `npm install && npm run build`
- **Publish**: `demo_site/dist`
- **Root Directory**: `demo_site`

All services connect to a single managed PostgreSQL instance.

## 🧪 Testing

```bash
# Run API tests
pytest tests/ -v

# Test backend health
curl https://aixel-pw3d.onrender.com/health

# Test funnel endpoint
curl https://aixel-pw3d.onrender.com/api/funnel?hours=168
```

## 📂 Project Structure

```
/backend/          - FastAPI application
  ├── main.py      - API endpoints & CORS config
  ├── crud.py      - Database queries (funnel, analytics, etc.)
  ├── models.py    - Pydantic models
  ├── db.py        - Database connection
  └── openai_client.py - AI insights generation

/dashboard/        - Streamlit admin dashboard
  └── streamlit_app.py - Dashboard UI with Plotly charts

/demo_site/        - React customer-facing frontend
  ├── src/
  │   ├── pages/   - Product catalog, cart, checkout
  │   ├── components/ - Auth, navigation
  │   └── utils/   - Event tracking SDK
  └── package.json

/scripts/          - Database & seeding scripts
  ├── init_db.py   - Auto schema creation & seeding
  └── seed_events.py - Generate realistic sessions

/sql/              - SQL schema (for reference)
/tests/            - API integration tests
```

## 🎯 User Journey Flow

1. **User lands on frontend** → Tracks `page_view` event
2. **User views product** → Tracks `product_view` event
3. **User adds to cart** → Tracks `add_to_cart` event
4. **User purchases** → Tracks `purchase` event with revenue
5. **Admin opens dashboard** → Views funnel metrics in real-time
6. **Admin clicks "Generate AI Insights"** → OpenAI analyzes conversion rates and provides recommendations

## 💻 Tech Stack

### Backend
- **FastAPI** - High-performance async API framework
- **SQLAlchemy** - ORM and database toolkit
- **PostgreSQL** - Primary data store
- **psycopg2** - PostgreSQL adapter
- **Pydantic** - Data validation

### Frontend
- **React 19** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing

### Dashboard
- **Streamlit** - Interactive data apps
- **Plotly** - Charts and visualizations
- **Pandas** - Data manipulation

### AI
- **OpenAI GPT-4** - Insights generation
- **Anthropic Claude** - Alternative AI provider (configured)

### Infrastructure
- **Docker** - Containerization
- **Render.com** - Cloud hosting
- **GitHub** - Version control & CI/CD

## 🏆 Key Technical Achievements

- ✅ **Full-stack deployment** on production with 3 interconnected services
- ✅ **Automatic database initialization** - Schema creation and data seeding on startup
- ✅ **Real-time event tracking** with sub-second latency
- ✅ **AI-powered insights** with OpenAI GPT-4 integration
- ✅ **Responsive design** working across devices
- ✅ **Production-grade error handling** and fallbacks
- ✅ **CORS configuration** for cross-origin requests
- ✅ **Environment-based configuration** for local/production

## 📝 About This Project

This project was built to demonstrate backend development capabilities for the **Aixel AI** team as part of the Backend SDE 1 application process. It showcases:

- RESTful API design and implementation
- Database schema design and optimization
- Event-driven architecture for analytics
- AI/ML integration for intelligent insights
- Full deployment pipeline from development to production
- Clean code organization and documentation

**Built by**: Ayush Jhanwar
**GitHub**: https://github.com/AyushJHANWAR03/Aixel
**Contact**: ayushjhanwar123@gmail.com

## 📄 License

MIT
