import { createContext, useContext, useState, useEffect } from 'react';
import { generateUUID } from '../utils/tracking';

const AppContext = createContext();

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};

export const AppProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [cart, setCart] = useState([]);
  const [notification, setNotification] = useState({ show: false, message: '' });

  // Load user and cart from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('aixel_user');
    const savedCart = localStorage.getItem('aixel_cart');

    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }

    if (savedCart) {
      setCart(JSON.parse(savedCart));
    }
  }, []);

  // Save cart to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('aixel_cart', JSON.stringify(cart));
  }, [cart]);

  const login = (email, name) => {
    // Check if user already exists in our "database" (localStorage)
    const usersDB = JSON.parse(localStorage.getItem('aixel_users_db')) || {};

    let userId;
    if (usersDB[email]) {
      // Existing user - use their existing userId
      userId = usersDB[email].userId;
      console.log('🔄 Returning user:', email, 'with userId:', userId);
    } else {
      // New user - create new userId
      userId = 'user_' + Math.random().toString(36).substr(2, 9);
      usersDB[email] = {
        userId,
        email,
        name: name || email.split('@')[0],
        createdAt: new Date().toISOString()
      };
      // Save to database
      localStorage.setItem('aixel_users_db', JSON.stringify(usersDB));
      console.log('✨ New user created:', email, 'with userId:', userId);
    }

    const newUser = {
      email,
      name: name || email.split('@')[0],
      userId
    };
    setUser(newUser);
    localStorage.setItem('aixel_user', JSON.stringify(newUser));
    return newUser;
  };

  const logout = () => {
    setUser(null);
    setCart([]);
    localStorage.removeItem('aixel_user');
    localStorage.removeItem('aixel_cart');
  };

  const addToCart = (product) => {
    setCart(prev => [...prev, product]);
  };

  const removeFromCart = (index) => {
    setCart(prev => prev.filter((_, i) => i !== index));
  };

  const clearCart = () => {
    setCart([]);
    localStorage.removeItem('aixel_cart');
  };

  const showNotification = (message) => {
    setNotification({ show: true, message });
    setTimeout(() => {
      setNotification({ show: false, message: '' });
    }, 3000);
  };

  const value = {
    user,
    cart,
    notification,
    login,
    logout,
    addToCart,
    removeFromCart,
    clearCart,
    showNotification
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
