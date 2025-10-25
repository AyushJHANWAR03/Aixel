import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { trackEvent } from '../utils/tracking';
import './Login.css';

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const { login, showNotification } = useApp();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    trackEvent('page_view', { metadata: { page: 'login' } });
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();

    const user = login(email, name);

    // Track login or signup
    trackEvent(isLogin ? 'user_login' : 'user_signup', {
      user_id: user.userId,
      metadata: { email, method: 'email' }
    });

    showNotification(isLogin ? '✅ Login Tracked!' : '✅ Signup Tracked!');

    // Check for redirect parameter or go to dashboard
    const params = new URLSearchParams(location.search);
    const redirect = params.get('redirect') || '/dashboard';

    setTimeout(() => {
      navigate(redirect + location.search);
    }, 800);
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <h1>Welcome to Aixel</h1>
        <p className="subtitle">Access your AI-powered analytics</p>

        <div className="demo-info">
          <strong>📝 Demo Mode:</strong> Use any email/password combination. No real authentication required!
        </div>

        <div className="tabs">
          <div
            className={`tab ${isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(true)}
          >
            Login
          </div>
          <div
            className={`tab ${!isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(false)}
          >
            Sign Up
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="John Doe"
                required
              />
            </div>
          )}

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={isLogin ? "Enter your password" : "Create a password"}
              required
            />
          </div>

          <button type="submit" className="btn-submit">
            {isLogin ? '🔐 Login' : '✨ Create Account'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
