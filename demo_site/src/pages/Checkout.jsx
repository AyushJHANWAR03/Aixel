import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { trackEvent } from '../utils/tracking';
import './Checkout.css';

const Checkout = () => {
  const { user, cart, clearCart, showNotification } = useApp();
  const navigate = useNavigate();
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    if (cart.length === 0) {
      navigate('/products');
      return;
    }

    trackEvent('page_view', { metadata: { page: 'checkout' } });
    showNotification('📋 Checkout Page View Tracked!');
  }, []);

  const subtotal = cart.reduce((sum, item) => sum + item.price, 0);
  const tax = subtotal * 0.1;
  const total = subtotal + tax;

  const handleSubmit = (e) => {
    e.preventDefault();
    setProcessing(true);

    trackEvent('payment_info_entered', {
      user_id: user?.userId,
      metadata: {
        total_amount: total,
        items_count: cart.length
      }
    });

    showNotification('💳 Processing Payment...');

    setTimeout(() => {
      trackEvent('purchase', {
        user_id: user?.userId,
        revenue: total,
        metadata: {
          items: cart.map(item => ({
            id: item.id,
            name: item.name,
            price: item.price
          })),
          tax: tax,
          subtotal: subtotal
        }
      });

      showNotification('🎉 Purchase Complete!');
      clearCart();

      setTimeout(() => {
        alert('🎉 Purchase Successful!\n\nThank you for your order! Your AI tools are ready to use.');
        navigate('/dashboard');
      }, 1000);
    }, 1500);
  };

  return (
    <div className="checkout-page">
      <div className="checkout-header">
        <div className="logo">🚀 Aixel Store</div>
      </div>

      <div className="checkout-container">
        <h1>Checkout</h1>

        <div className="demo-info">
          <strong>📝 Demo Mode:</strong> This is a simulated checkout. No real payment will be processed!
        </div>

        <div className="checkout-section">
          <h2>📦 Order Summary</h2>
          {cart.map((item, index) => (
            <div key={index} className="order-item">
              <span>{item.emoji} {item.name}</span>
              <span>${item.price}</span>
            </div>
          ))}
          <div className="order-total">
            <span>Total:</span>
            <span>${total.toFixed(2)}</span>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="checkout-section">
            <h2>💳 Payment Information</h2>
            <div className="form-group">
              <label>Card Number</label>
              <input type="text" placeholder="4242 4242 4242 4242" maxLength="19" required />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Expiry Date</label>
                <input type="text" placeholder="MM/YY" maxLength="5" required />
              </div>
              <div className="form-group">
                <label>CVV</label>
                <input type="text" placeholder="123" maxLength="3" required />
              </div>
            </div>
            <div className="form-group">
              <label>Cardholder Name</label>
              <input type="text" placeholder="John Doe" required />
            </div>
          </div>

          <div className="checkout-section">
            <h2>📍 Billing Address</h2>
            <div className="form-group">
              <label>Country</label>
              <select required>
                <option value="">Select country</option>
                <option value="US">United States</option>
                <option value="CA">Canada</option>
                <option value="UK">United Kingdom</option>
                <option value="AU">Australia</option>
              </select>
            </div>
            <div className="form-group">
              <label>ZIP / Postal Code</label>
              <input type="text" placeholder="12345" required />
            </div>
          </div>

          <button type="submit" className="btn-pay" disabled={processing}>
            {processing ? '⏳ Processing...' : '💰 Complete Purchase'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Checkout;
