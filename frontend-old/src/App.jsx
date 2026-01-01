import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [users, setUsers] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [marketItems, setMarketItems] = useState([]);
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [registerData, setRegisterData] = useState({ username: '', email: '', password: '', confirmPassword: '' });
  const [predictionData, setPredictionData] = useState({ numbers: '', lottery_type: 'Chance', draw_date: '' });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // הגדרת headers עם token
  const getHeaders = () => {
    const headers = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  };

  // בדיקת חיבור API אוטומטית
  useEffect(() => {
    if (token) {
      fetchUserData();
    }
    fetchPublicData();
  }, [token]);

  const fetchUserData = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/auth/me`, {
        headers: getHeaders()
      });
      if (response.ok) {
        const data = await response.json();
        setUser(data);
        fetchPredictions();
      } else {
        localStorage.removeItem('token');
        setToken(null);
      }
    } catch (error) {
      console.error('Failed to fetch user data:', error);
    }
  };

  const fetchPublicData = async () => {
    try {
      const [usersRes, marketRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/users`),
        fetch(`${API_BASE}/api/v1/market`),
        fetch(`${API_BASE}/api/v1/stats`)
      ]);
      
      if (usersRes.ok) setUsers(await usersRes.json());
      if (marketRes.ok) setMarketItems(await marketRes.json());
      if (statsRes.ok) setStats((await statsRes.json()).stats);
    } catch (error) {
      console.error('Failed to fetch public data:', error);
    }
  };

  const fetchPredictions = async () => {
    if (!token) return;
    try {
      const response = await fetch(`${API_BASE}/api/v1/predictions`, {
        headers: getHeaders()
      });
      if (response.ok) {
        setPredictions(await response.json());
      }
    } catch (error) {
      console.error('Failed to fetch predictions:', error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    
    try {
      const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          username: loginData.username,
          password: loginData.password
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
        setMessage('Login successful!');
        setLoginData({ username: '', password: '' });
      } else {
        setMessage('Login failed. Check your credentials.');
      }
    } catch (error) {
      setMessage('Login error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (registerData.password !== registerData.confirmPassword) {
      setMessage('Passwords do not match');
      return;
    }
    
    setLoading(true);
    setMessage('');
    
    try {
      const response = await fetch(`${API_BASE}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: registerData.username,
          email: registerData.email,
          password: registerData.password
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
        setMessage('Registration successful! You are now logged in.');
        setRegisterData({ username: '', email: '', password: '', confirmPassword: '' });
      } else {
        const error = await response.json();
        setMessage('Registration failed: ' + (error.detail || 'Unknown error'));
      }
    } catch (error) {
      setMessage('Registration error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setMessage('Logged out successfully');
  };

  const handleCreatePrediction = async (e) => {
    e.preventDefault();
    if (!token) {
      setMessage('Please login to create predictions');
      return;
    }
    
    setLoading(true);
    setMessage('');
    
    try {
      const response = await fetch(`${API_BASE}/api/v1/predictions`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
          ...predictionData,
          draw_date: new Date(predictionData.draw_date).toISOString()
        })
      });
      
      if (response.ok) {
        const newPrediction = await response.json();
        setPredictions([newPrediction, ...predictions]);
        setMessage('Prediction created successfully!');
        setPredictionData({ numbers: '', lottery_type: 'Chance', draw_date: '' });
        fetchUserData(); // Refresh user points
      } else {
        const error = await response.json();
        setMessage('Prediction failed: ' + (error.detail || 'Unknown error'));
      }
    } catch (error) {
      setMessage('Prediction error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBuyItem = async (itemId) => {
    if (!token) {
      setMessage('Please login to buy items');
      return;
    }
    
    setLoading(true);
    setMessage('');
    
    try {
      const response = await fetch(`${API_BASE}/api/v1/market/${itemId}/buy`, {
        method: 'POST',
        headers: getHeaders()
      });
      
      if (response.ok) {
        const result = await response.json();
        setMessage(result.message);
        fetchPublicData(); // Refresh market items
        fetchUserData(); // Refresh user points
      } else {
        const error = await response.json();
        setMessage('Purchase failed: ' + (error.detail || 'Unknown error'));
      }
    } catch (error) {
      setMessage('Purchase error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const initializeDatabase = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/v1/init-db`, { method: 'POST' });
      if (response.ok) {
        setMessage('Database initialized with sample data');
        fetchPublicData();
      }
    } catch (error) {
      setMessage('Database initialization failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎯 Prediction Point System</h1>
        <p>Version 5.0.0 - Real Database & Features</p>
        {user && (
          <div className="user-info">
            <span>Welcome, {user.username}!</span>
            <span>Points: {user.points}</span>
            <button onClick={handleLogout}>Logout</button>
          </div>
        )}
      </header>

      <div className="container">
        {/* Navigation */}
        <div className="tabs">
          <button className={activeTab === 'dashboard' ? 'active' : ''} onClick={() => setActiveTab('dashboard')}>
            Dashboard
          </button>
          <button className={activeTab === 'predictions' ? 'active' : ''} onClick={() => setActiveTab('predictions')}>
            Predictions
          </button>
          <button className={activeTab === 'market' ? 'active' : ''} onClick={() => setActiveTab('market')}>
            Market
          </button>
          <button className={activeTab === 'users' ? 'active' : ''} onClick={() => setActiveTab('users')}>
            Users
          </button>
          <button className={activeTab === 'stats' ? 'active' : ''} onClick={() => setActiveTab('stats')}>
            Stats
          </button>
          {!user && (
            <>
              <button className={activeTab === 'login' ? 'active' : ''} onClick={() => setActiveTab('login')}>
                Login
              </button>
              <button className={activeTab === 'register' ? 'active' : ''} onClick={() => setActiveTab('register')}>
                Register
              </button>
            </>
          )}
        </div>

        {/* Messages */}
        {message && (
          <div className={`message ${message.includes('success') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}

        {/* Loading */}
        {loading && <div className="loading">Loading...</div>}

        {/* Tab Content */}
        <div className="tab-content">
          {activeTab === 'dashboard' && (
            <div className="dashboard">
              <h2>Dashboard</h2>
              <div className="cards">
                <div className="card">
                  <h3>System Status</h3>
                  <p>API: ✅ Connected</p>
                  <p>Database: {stats ? '✅ Active' : '⏳ Connecting...'}</p>
                  <button onClick={initializeDatabase}>Initialize Database</button>
                </div>
                <div className="card">
                  <h3>Your Info</h3>
                  {user ? (
                    <>
                      <p>Username: {user.username}</p>
                      <p>Points: {user.points}</p>
                      <p>Predictions: {predictions.length}</p>
                    </>
                  ) : (
                    <p>Please login to see your info</p>
                  )}
                </div>
                <div className="card">
                  <h3>System Stats</h3>
                  {stats ? (
                    <>
                      <p>Total Users: {stats.total_users}</p>
                      <p>Total Predictions: {stats.total_predictions}</p>
                      <p>Active Users: {stats.active_users}</p>
                    </>
                  ) : (
                    <p>Loading stats...</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'predictions' && (
            <div className="predictions">
              <h2>Predictions</h2>
              {user ? (
                <>
                  <form onSubmit={handleCreatePrediction} className="prediction-form">
                    <h3>Create New Prediction</h3>
                    <input
                      type="text"
                      placeholder="Numbers (e.g., 1,5,12,18,25,33)"
                      value={predictionData.numbers}
                      onChange={(e) => setPredictionData({...predictionData, numbers: e.target.value})}
                      required
                    />
                    <select
                      value={predictionData.lottery_type}
                      onChange={(e) => setPredictionData({...predictionData, lottery_type: e.target.value})}
                    >
                      <option value="Chance">Chance</option>
                      <option value="Lotto">Lotto</option>
                      <option value="777">777</option>
                    </select>
                    <input
                      type="datetime-local"
                      value={predictionData.draw_date}
                      onChange={(e) => setPredictionData({...predictionData, draw_date: e.target.value})}
                      required
                    />
                    <button type="submit" disabled={loading}>Create Prediction (Cost: 10 points)</button>
                  </form>

                  <h3>Your Predictions</h3>
                  <div className="predictions-list">
                    {predictions.map(pred => (
                      <div key={pred.id} className="prediction-card">
                        <p><strong>Numbers:</strong> {pred.numbers}</p>
                        <p><strong>Type:</strong> {pred.lottery_type}</p>
                        <p><strong>Draw Date:</strong> {new Date(pred.draw_date).toLocaleDateString()}</p>
                        <p><strong>Status:</strong> {pred.is_correct === null ? 'Pending' : pred.is_correct ? 'Won' : 'Lost'}</p>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <p>Please login to view and create predictions</p>
              )}
            </div>
          )}

          {activeTab === 'market' && (
            <div className="market">
              <h2>Marketplace</h2>
              <div className="market-items">
                {marketItems.map(item => (
                  <div key={item.id} className="market-item">
                    <h3>{item.name}</h3>
                    <p>{item.description}</p>
                    <p><strong>Price:</strong> {item.price} points</p>
                    <p><strong>Stock:</strong> {item.stock}</p>
                    <button 
                      onClick={() => handleBuyItem(item.id)}
                      disabled={!user || item.stock <= 0}
                    >
                      Buy Now
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'users' && (
            <div className="users">
              <h2>Users</h2>
              <div className="users-list">
                {users.map(u => (
                  <div key={u.id} className="user-card">
                    <h3>{u.username}</h3>
                    <p>Points: {u.points}</p>
                    <p>Joined: {new Date(u.created_at).toLocaleDateString()}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'stats' && (
            <div className="stats">
              <h2>Statistics</h2>
              {stats ? (
                <div className="stats-grid">
                  <div className="stat-card">
                    <h3>📊 System Overview</h3>
                    <p>Total Users: {stats.total_users}</p>
                    <p>Total Predictions: {stats.total_predictions}</p>
                    <p>Total Points: {stats.total_points_in_circulation}</p>
                  </div>
                  <div className="stat-card">
                    <h3>👥 User Activity</h3>
                    <p>Active Users: {stats.active_users}</p>
                    <p>Daily Predictions: {stats.daily_predictions}</p>
                    <p>Avg Points/User: {Math.round(stats.average_points_per_user)}</p>
                  </div>
                </div>
              ) : (
                <p>Loading statistics...</p>
              )}
            </div>
          )}

          {activeTab === 'login' && !user && (
            <div className="auth-form">
              <h2>Login</h2>
              <form onSubmit={handleLogin}>
                <input
                  type="text"
                  placeholder="Username"
                  value={loginData.username}
                  onChange={(e) => setLoginData({...loginData, username: e.target.value})}
                  required
                />
                <input
                  type="password"
                  placeholder="Password"
                  value={loginData.password}
                  onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                  required
                />
                <button type="submit" disabled={loading}>Login</button>
              </form>
            </div>
          )}

          {activeTab === 'register' && !user && (
            <div className="auth-form">
              <h2>Register</h2>
              <form onSubmit={handleRegister}>
                <input
                  type="text"
                  placeholder="Username"
                  value={registerData.username}
                  onChange={(e) => setRegisterData({...registerData, username: e.target.value})}
                  required
                />
                <input
                  type="email"
                  placeholder="Email"
                  value={registerData.email}
                  onChange={(e) => setRegisterData({...registerData, email: e.target.value})}
                  required
                />
                <input
                  type="password"
                  placeholder="Password"
                  value={registerData.password}
                  onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
                  required
                />
                <input
                  type="password"
                  placeholder="Confirm Password"
                  value={registerData.confirmPassword}
                  onChange={(e) => setRegisterData({...registerData, confirmPassword: e.target.value})}
                  required
                />
                <button type="submit" disabled={loading}>Register</button>
              </form>
            </div>
          )}
        </div>

        {/* Quick Links */}
        <div className="quick-links">
          <h3>Quick Links:</h3>
          <div className="links">
            <a href={`${API_BASE}`} target="_blank" rel="noopener noreferrer">
              API Root
            </a>
            <a href={`${API_BASE}/docs`} target="_blank" rel="noopener noreferrer">
              API Documentation
            </a>
            <button onClick={() => window.open('http://localhost:5432', '_blank')}>
              Database Admin
            </button>
          </div>
        </div>
      </div>

      <footer>
        <p>Prediction Point System &copy; 2024 - Phase 3: Database & Real Features</p>
        <p>API: {API_BASE} | Status: {user ? 'Logged In' : 'Not Logged In'}</p>
      </footer>
    </div>
  );
}

export default App;
