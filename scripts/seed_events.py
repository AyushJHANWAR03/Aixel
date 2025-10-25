import requests
import random
import uuid
import time
import os
from datetime import datetime, timedelta

# Use production backend URL if deployed, otherwise localhost
BACKEND_URL = os.getenv('BACKEND_URL', 'https://aixel-pw3d.onrender.com')
API_BASE = f'{BACKEND_URL}/api/track'

# Realistic test users
USERS = [
    {"email": "ayushjhanwar123@gmail.com", "name": "Ayush", "userId": "user_ayush_001"},
    {"email": "sarah.johnson@gmail.com", "name": "Sarah Johnson", "userId": "user_sarah_002"},
    {"email": "mike.chen@yahoo.com", "name": "Mike Chen", "userId": "user_mike_003"},
    {"email": "priya.sharma@outlook.com", "name": "Priya Sharma", "userId": "user_priya_004"},
    {"email": "david.wilson@gmail.com", "name": "David Wilson", "userId": "user_david_005"},
    {"email": "emma.martinez@hotmail.com", "name": "Emma Martinez", "userId": "user_emma_006"},
    {"email": "raj.patel@gmail.com", "name": "Raj Patel", "userId": "user_raj_007"},
    {"email": "lisa.anderson@yahoo.com", "name": "Lisa Anderson", "userId": "user_lisa_008"},
    {"email": "kevin.lee@gmail.com", "name": "Kevin Lee", "userId": "user_kevin_009"},
    {"email": "sophia.garcia@outlook.com", "name": "Sophia Garcia", "userId": "user_sophia_010"},
]

# Campaign configurations
CAMPAIGNS = [
    {"name": "summer_sale", "weight": 25, "conversion_rate": 0.12},
    {"name": "journey_tracker_launch", "weight": 20, "conversion_rate": 0.15},
    {"name": "premium_upgrade", "weight": 18, "conversion_rate": 0.10},
    {"name": "black_friday", "weight": 15, "conversion_rate": 0.20},
    {"name": "new_year_promo", "weight": 12, "conversion_rate": 0.14},
    {"name": "direct", "weight": 10, "conversion_rate": 0.08},
]

# Products with realistic pricing
PRODUCTS = [
    {"id": 1, "name": "AI Analytics Pro", "price": 299},
    {"id": 2, "name": "Marketing Dashboard", "price": 199},
    {"id": 3, "name": "Customer Insights", "price": 399},
    {"id": 4, "name": "Journey Tracker", "price": 249},
]

# UTM sources for diversity
UTM_SOURCES = ['google', 'facebook', 'twitter', 'linkedin', 'instagram', 'email', 'direct']
DEVICES = ['desktop', 'mobile', 'tablet']

def weighted_random_campaign():
    """Select campaign based on weight"""
    campaigns = [c['name'] for c in CAMPAIGNS]
    weights = [c['weight'] for c in CAMPAIGNS]
    return random.choices(campaigns, weights=weights)[0]

def get_campaign_conversion_rate(campaign):
    """Get conversion rate for specific campaign"""
    for c in CAMPAIGNS:
        if c['name'] == campaign:
            return c['conversion_rate']
    return 0.08

def generate_session():
    """Simulate a complete user session through the funnel"""
    session_id = str(uuid.uuid4())
    user = random.choice(USERS)
    campaign = weighted_random_campaign()
    utm_source = random.choice(UTM_SOURCES)
    device = random.choice(DEVICES)

    # Mobile has lower conversion
    device_penalty = 0.7 if device == 'mobile' else 1.0
    base_conversion = get_campaign_conversion_rate(campaign) * device_penalty

    # Random time in the past week
    hours_ago = random.randint(0, 168)
    timestamp_base = datetime.utcnow() - timedelta(hours=hours_ago)

    events_sent = 0

    # Step 1: Ad Click (80% of sessions)
    if random.random() < 0.80:
        try:
            requests.post(API_BASE, json={
                "event_type": "ad_click",
                "session_id": session_id,
                "user_id": user['userId'],
                "timestamp": timestamp_base.isoformat(),
                "utm_source": utm_source,
                "utm_medium": "cpc",
                "utm_campaign": campaign,
                "device": device,
                "platform": "web",
                "metadata": {
                    "user_email": user['email'],
                    "user_name": user['name'],
                    "campaign": campaign
                }
            }, timeout=2)
            events_sent += 1
            time.sleep(0.01)
        except:
            pass

    # Step 2: Landing Page View (always happens)
    try:
        requests.post(API_BASE, json={
            "event_type": "page_view",
            "session_id": session_id,
            "user_id": user['userId'],
            "timestamp": (timestamp_base + timedelta(seconds=2)).isoformat(),
            "page_url": "/dashboard",
            "utm_source": utm_source,
            "utm_medium": "cpc",
            "utm_campaign": campaign,
            "device": device,
            "platform": "web",
            "metadata": {
                "user_email": user['email'],
                "user_name": user['name'],
                "landing": "true",
                "page": "dashboard"
            }
        }, timeout=2)
        events_sent += 1
        time.sleep(0.01)
    except:
        pass

    # Step 3: Browse to Products (70% continue)
    if random.random() < 0.70:
        try:
            requests.post(API_BASE, json={
                "event_type": "page_view",
                "session_id": session_id,
                "user_id": user['userId'],
                "timestamp": (timestamp_base + timedelta(seconds=15)).isoformat(),
                "page_url": "/products",
                "utm_source": utm_source,
                "utm_medium": "cpc",
                "utm_campaign": campaign,
                "device": device,
                "platform": "web",
                "metadata": {
                    "user_email": user['email'],
                    "user_name": user['name'],
                    "page": "products"
                }
            }, timeout=2)
            events_sent += 1
            time.sleep(0.01)
        except:
            pass

        # Step 4: Product View (60% of those who reach products)
        if random.random() < 0.60:
            product = random.choice(PRODUCTS)
            try:
                requests.post(API_BASE, json={
                    "event_type": "product_view",
                    "session_id": session_id,
                    "user_id": user['userId'],
                    "timestamp": (timestamp_base + timedelta(seconds=30)).isoformat(),
                    "utm_source": utm_source,
                    "utm_medium": "cpc",
                    "utm_campaign": campaign,
                    "device": device,
                    "platform": "web",
                    "metadata": {
                        "user_email": user['email'],
                        "user_name": user['name'],
                        "product_id": product['id'],
                        "product_name": product['name']
                    }
                }, timeout=2)
                events_sent += 1
                time.sleep(0.01)
            except:
                pass

            # Step 5: Add to Cart (40% of product viewers)
            if random.random() < 0.40:
                try:
                    requests.post(API_BASE, json={
                        "event_type": "add_to_cart",
                        "session_id": session_id,
                        "user_id": user['userId'],
                        "timestamp": (timestamp_base + timedelta(seconds=45)).isoformat(),
                        "utm_source": utm_source,
                        "utm_medium": "cpc",
                        "utm_campaign": campaign,
                        "device": device,
                        "platform": "web",
                        "metadata": {
                            "user_email": user['email'],
                            "user_name": user['name'],
                            "product_id": product['id'],
                            "product_name": product['name'],
                            "price": product['price']
                        }
                    }, timeout=2)
                    events_sent += 1
                    time.sleep(0.01)
                except:
                    pass

                # Step 6: Go to Cart Page
                try:
                    requests.post(API_BASE, json={
                        "event_type": "page_view",
                        "session_id": session_id,
                        "user_id": user['userId'],
                        "timestamp": (timestamp_base + timedelta(seconds=50)).isoformat(),
                        "page_url": "/cart",
                        "utm_source": utm_source,
                        "utm_medium": "cpc",
                        "utm_campaign": campaign,
                        "device": device,
                        "platform": "web",
                        "metadata": {
                            "user_email": user['email'],
                            "user_name": user['name'],
                            "page": "cart"
                        }
                    }, timeout=2)
                    events_sent += 1
                    time.sleep(0.01)
                except:
                    pass

                # Step 7: Checkout Start (70% of cart viewers)
                if random.random() < 0.70:
                    try:
                        requests.post(API_BASE, json={
                            "event_type": "checkout_start",
                            "session_id": session_id,
                            "user_id": user['userId'],
                            "timestamp": (timestamp_base + timedelta(seconds=60)).isoformat(),
                            "utm_source": utm_source,
                            "utm_medium": "cpc",
                            "utm_campaign": campaign,
                            "device": device,
                            "platform": "web",
                            "metadata": {
                                "user_email": user['email'],
                                "user_name": user['name'],
                                "cart_value": product['price']
                            }
                        }, timeout=2)
                        events_sent += 1
                        time.sleep(0.01)
                    except:
                        pass

                    # Step 8: Payment Info Entered
                    try:
                        requests.post(API_BASE, json={
                            "event_type": "payment_info_entered",
                            "session_id": session_id,
                            "user_id": user['userId'],
                            "timestamp": (timestamp_base + timedelta(seconds=75)).isoformat(),
                            "utm_source": utm_source,
                            "utm_medium": "cpc",
                            "utm_campaign": campaign,
                            "device": device,
                            "platform": "web",
                            "metadata": {
                                "user_email": user['email'],
                                "user_name": user['name']
                            }
                        }, timeout=2)
                        events_sent += 1
                        time.sleep(0.01)
                    except:
                        pass

                    # Step 9: Purchase (campaign-specific conversion rate)
                    if random.random() < base_conversion:
                        # Add 10% tax
                        total_revenue = product['price'] * 1.10
                        try:
                            requests.post(API_BASE, json={
                                "event_type": "purchase",
                                "session_id": session_id,
                                "user_id": user['userId'],
                                "timestamp": (timestamp_base + timedelta(seconds=90)).isoformat(),
                                "utm_source": utm_source,
                                "utm_medium": "cpc",
                                "utm_campaign": campaign,
                                "device": device,
                                "platform": "web",
                                "revenue": total_revenue,
                                "metadata": {
                                    "user_email": user['email'],
                                    "user_name": user['name'],
                                    "product_id": product['id'],
                                    "product_name": product['name'],
                                    "subtotal": product['price'],
                                    "tax": product['price'] * 0.10,
                                    "total": total_revenue
                                }
                            }, timeout=2)
                            events_sent += 1
                            time.sleep(0.01)
                        except:
                            pass

    return events_sent

def main():
    num_sessions = int(input("How many sessions to generate? (default: 500): ") or "500")

    print(f"\n🚀 Generating {num_sessions} realistic user sessions...")
    print(f"📧 Using {len(USERS)} test users")
    print(f"🎯 Across {len(CAMPAIGNS)} campaigns")
    print(f"🛍️ With {len(PRODUCTS)} products")
    print(f"\nThis will take approximately {num_sessions * 0.5:.0f} seconds...\n")

    total_events = 0
    successful_sessions = 0

    for i in range(num_sessions):
        try:
            events_count = generate_session()
            total_events += events_count
            successful_sessions += 1

            if (i + 1) % 50 == 0:
                print(f"✅ Generated {i + 1}/{num_sessions} sessions | {total_events} total events")
        except Exception as e:
            print(f"❌ Error in session {i}: {e}")
            continue

    print(f"\n{'='*60}")
    print(f"✅ SEEDING COMPLETE!")
    print(f"{'='*60}")
    print(f"📊 Sessions Generated: {successful_sessions}/{num_sessions}")
    print(f"📈 Total Events Created: {total_events:,}")
    print(f"📧 Users: {len(USERS)}")
    print(f"🎯 Campaigns: {len(CAMPAIGNS)}")
    print(f"💰 Products: {len(PRODUCTS)}")
    print(f"\n🎯 View your dashboard at: http://localhost:8501")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
