"""
Database initialization script - runs seed data only if database is empty
This runs automatically on production startup
"""
import os
import sys
import requests
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from seed_events import generate_session

def create_schema():
    """Create database schema if it doesn't exist"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False

    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            print("📦 Creating database schema if not exists...")

            # Enable UUID extension
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))

            # Create events table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS events (
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
                )
            """))

            # Create indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events (timestamp)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_events_session ON events (session_id)"))

            conn.commit()
            print("✅ Schema created successfully")
            return True
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        return False

def check_database_empty():
    """Check if database has any events"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False

    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM events"))
            count = result.fetchone()[0]
            return count == 0
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def seed_production_data():
    """Seed production database with realistic data"""
    print("\n" + "="*60)
    print("🌱 PRODUCTION DATABASE INITIALIZATION")
    print("="*60)

    # Create schema first
    if not create_schema():
        print("❌ Failed to create schema. Aborting.")
        return

    # Check if already seeded
    if not check_database_empty():
        print("✅ Database already has data. Skipping seed.")
        print("="*60 + "\n")
        return

    print("📊 Database is empty. Starting seed process...")
    print("🚀 Generating 300 realistic user sessions...")
    print("⏱️  This will take approximately 150 seconds...\n")

    total_events = 0
    num_sessions = 300

    for i in range(num_sessions):
        try:
            events_count = generate_session()
            total_events += events_count

            if (i + 1) % 50 == 0:
                print(f"✅ Generated {i + 1}/{num_sessions} sessions | {total_events} events")
        except Exception as e:
            print(f"❌ Error in session {i}: {e}")
            continue

    print(f"\n{'='*60}")
    print(f"✅ PRODUCTION SEEDING COMPLETE!")
    print(f"{'='*60}")
    print(f"📊 Sessions Generated: {num_sessions}")
    print(f"📈 Total Events: {total_events:,}")
    print(f"📧 Users: 10")
    print(f"🎯 Campaigns: 6")
    print(f"💰 Products: 4")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    seed_production_data()
