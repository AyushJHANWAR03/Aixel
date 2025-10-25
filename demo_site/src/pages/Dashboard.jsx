import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { trackEvent } from '../utils/tracking';
import './Dashboard.css';

const Dashboard = () => {
  const { user, cart, showNotification } = useApp();
  const navigate = useNavigate();

  useEffect(() => {
    trackEvent('page_view', { metadata: { page: 'dashboard' } });
    showNotification('📊 Dashboard View Tracked!');
  }, []);

  const handleAdClick = (campaign) => {
    trackEvent('ad_click', {
      user_id: user?.userId,
      metadata: {
        campaign: campaign,
        source: 'dashboard'
      }
    });
    showNotification(`📢 Ad Click Tracked: ${campaign}`);
    navigate(`/products?utm_source=dashboard&utm_medium=banner&utm_campaign=${campaign}`);
  };

  const adCampaigns = [
    {
      id: 1,
      title: '🎯 Summer Sale - 40% OFF',
      description: 'Limited time offer on all AI Analytics tools',
      campaign: 'summer_sale',
      color: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)'
    },
    {
      id: 2,
      title: '🚀 New Launch: Journey Tracker',
      description: 'Track customer journeys across all touchpoints',
      campaign: 'journey_tracker_launch',
      color: 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
    },
    {
      id: 3,
      title: '💎 Premium Dashboard Upgrade',
      description: 'Get advanced insights with our premium tier',
      campaign: 'premium_upgrade',
      color: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)'
    }
  ];

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div className="dashboard-header-content">
          <div>
            <h1>Welcome back, {user?.name || 'User'}!</h1>
            <p>Your AI-powered analytics dashboard</p>
          </div>
          <div className="header-actions">
            <div className="cart-badge" onClick={() => navigate('/cart')}>
              🛒 Cart <span className="badge">{cart.length}</span>
            </div>
            <button className="btn-browse" onClick={() => navigate('/products')}>
              Browse Products
            </button>
          </div>
        </div>
      </div>

      <div className="dashboard-container">
        {/* Ad Campaigns Section */}
        <section className="ads-section">
          <h2>📢 Active Ad Campaigns</h2>
          <p className="section-subtitle">Click on any ad to simulate ad click tracking</p>

          <div className="ads-grid">
            {adCampaigns.map(ad => (
              <div
                key={ad.id}
                className="ad-card"
                style={{ background: ad.color }}
                onClick={() => handleAdClick(ad.campaign)}
              >
                <h3>{ad.title}</h3>
                <p>{ad.description}</p>
                <button className="ad-cta">Learn More →</button>
              </div>
            ))}
          </div>
        </section>

        {/* Quick Actions */}
        <section className="actions-section">
          <h2>⚡ Quick Actions</h2>
          <div className="actions-grid">
            <div className="action-card" onClick={() => navigate('/products')}>
              <div className="action-icon">🛍️</div>
              <h3>Browse Products</h3>
              <p>Explore our AI analytics tools</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
