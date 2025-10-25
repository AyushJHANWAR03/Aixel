import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { trackEvent } from '../utils/tracking';
import './Cart.css';

const Cart = () => {
  const { user, cart, removeFromCart, showNotification } = useApp();
  const navigate = useNavigate();

  useEffect(() => {
    trackEvent('page_view', { metadata: { page: 'cart' } });
    showNotification('🛒 Cart Page View Tracked!');
  }, []);

  const subtotal = cart.reduce((sum, item) => sum + item.price, 0);
  const tax = subtotal * 0.1;
  const total = subtotal + tax;

  const handleCheckout = () => {
    trackEvent('checkout_start', {
      user_id: user?.userId,
      metadata: {
        items_count: cart.length,
        total_amount: total
      }
    });
    showNotification('🚀 Checkout Started!');
    setTimeout(() => navigate('/checkout'), 800);
  };

  if (cart.length === 0) {
    return (
      <div className="cart-page">
        <div className="cart-header">
          <div className="logo" onClick={() => navigate('/dashboard')}>🚀 Aixel Store</div>
        </div>
        <div className="cart-container">
          <div className="cart-empty">
            <div style={{ fontSize: '4em' }}>🛒</div>
            <h2>Your cart is empty</h2>
            <p>Add some awesome AI tools to get started!</p>
            <button className="btn-primary" onClick={() => navigate('/products')}>
              Browse Products
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="cart-page">
      <div className="cart-header">
        <div className="logo" onClick={() => navigate('/dashboard')}>🚀 Aixel Store</div>
      </div>

      <div className="cart-container">
        <h1>Your Shopping Cart</h1>

        <div className="cart-items">
          {cart.map((item, index) => (
            <div key={index} className="cart-item">
              <img src={item.image} alt={item.name} className="item-image" />
              <div className="item-details">
                <div className="item-name">{item.emoji} {item.name}</div>
                <div className="item-price">${item.price}</div>
              </div>
              <button className="btn-remove" onClick={() => removeFromCart(index)}>
                Remove
              </button>
            </div>
          ))}
        </div>

        <div className="cart-summary">
          <div className="summary-row">
            <span>Subtotal:</span>
            <span>${subtotal.toFixed(2)}</span>
          </div>
          <div className="summary-row">
            <span>Tax (10%):</span>
            <span>${tax.toFixed(2)}</span>
          </div>
          <div className="summary-total">
            <span>Total:</span>
            <span>${total.toFixed(2)}</span>
          </div>

          <button className="btn-checkout" onClick={handleCheckout}>
            💳 Proceed to Checkout
          </button>
          <button className="btn-continue" onClick={() => navigate('/products')}>
            ← Continue Shopping
          </button>
        </div>
      </div>
    </div>
  );
};

export default Cart;
