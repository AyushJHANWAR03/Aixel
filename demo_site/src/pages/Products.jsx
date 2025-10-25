import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { trackEvent } from '../utils/tracking';
import './Products.css';

const Products = () => {
  const { user, cart, addToCart, showNotification } = useApp();
  const navigate = useNavigate();
  const location = useLocation();

  const isFromAd = new URLSearchParams(location.search).get('utm_source') !== null;

  useEffect(() => {
    trackEvent('page_view', {
      user_id: user?.userId,
      metadata: { landing: isFromAd, page: 'products' }
    });
    showNotification(isFromAd ? '🎯 Landing Page View Tracked!' : '📊 Page View Tracked!');
  }, []);

  const products = [
    {
      id: 1,
      name: 'AI Analytics Pro',
      price: 299,
      description: 'Advanced AI-powered analytics dashboard with real-time insights and predictive modeling.',
      image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop',
      emoji: '📊'
    },
    {
      id: 2,
      name: 'Marketing Dashboard',
      price: 199,
      description: 'Complete marketing analytics suite with campaign tracking and ROI optimization.',
      image: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=300&fit=crop',
      emoji: '📈'
    },
    {
      id: 3,
      name: 'Customer Insights',
      price: 399,
      description: 'Deep customer behavior analysis with AI-driven recommendations and segmentation.',
      image: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=400&h=300&fit=crop',
      emoji: '👥'
    },
    {
      id: 4,
      name: 'Journey Tracker',
      price: 249,
      description: 'Track complete customer journeys across all touchpoints with visual funnel analysis.',
      image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop',
      emoji: '🎯'
    }
  ];

  const handleProductClick = (product) => {
    trackEvent('product_view', {
      user_id: user?.userId,
      metadata: {
        product_id: product.id,
        product_name: product.name,
        price: product.price
      }
    });
    showNotification(`👀 Product View Tracked: ${product.name}`);
  };

  const handleAddToCart = (e, product) => {
    e.stopPropagation();

    trackEvent('add_to_cart', {
      user_id: user?.userId,
      metadata: {
        product_id: product.id,
        product_name: product.name,
        price: product.price
      }
    });

    addToCart(product);
    showNotification(`✅ Added to Cart: ${product.name}`);
  };

  return (
    <div className="products-page">
      <div className="products-header">
        <div className="products-header-content">
          <div className="logo" onClick={() => navigate('/dashboard')}>🚀 Aixel Store</div>
          <div className="header-right">
            <span>Hi, {user?.name || 'Guest'}!</span>
            <div className="cart-widget" onClick={() => navigate('/cart')}>
              🛒 Cart <span className="cart-count">{cart.length}</span>
            </div>
          </div>
        </div>
      </div>

      {isFromAd && (
        <div className="landing-banner">
          🎉 Special Offer Active! Get 40% OFF on all products - Limited Time!
        </div>
      )}

      <div className="products-container">
        <h1 className="page-title">AI-Powered Analytics Tools</h1>

        <div className="products-grid">
          {products.map(product => (
            <div
              key={product.id}
              className="product-card"
              onClick={() => handleProductClick(product)}
            >
              <div className="product-image-wrapper">
                <img src={product.image} alt={product.name} className="product-image" />
                <div className="product-emoji">{product.emoji}</div>
              </div>
              <div className="product-info">
                <div className="product-name">{product.name}</div>
                <div className="product-description">{product.description}</div>
                <div className="product-price">${product.price}</div>
                <button
                  className="btn-add-cart"
                  onClick={(e) => handleAddToCart(e, product)}
                >
                  Add to Cart
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Products;
