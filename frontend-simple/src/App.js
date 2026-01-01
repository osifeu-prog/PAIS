import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [lotteryStatus, setLotteryStatus] = useState('Checking...');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check backend health
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setBackendStatus(data.status))
      .catch(() => setBackendStatus('❌ Offline'));

    // Check lottery health
    fetch('http://localhost:8000/api/v1/lottery/health')
      .then(res => res.json())
      .then(data => setLotteryStatus(data.status))
      .catch(() => setLotteryStatus('❌ Offline'));

    // Get lottery prediction
    fetch('http://localhost:8000/api/v1/lottery/prediction')
      .then(res => res.json())
      .then(data => {
        setPrediction(data.prediction);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  const simulateBet = () => {
    const numbers = [1, 15, 23, 34, 45];
    fetch('http://localhost:8000/api/v1/lottery/simulate-bet', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        numbers: numbers,
        bet_amount: 10
      })
    })
    .then(res => res.json())
    .then(data => {
      alert(`Simulation Result:\nWon: ${data.won ? 'Yes' : 'No'}\nPrize: ${data.prize}`);
    });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎯 Prediction Point System</h1>
        <p>Advanced prediction and trading platform with Lottery integration</p>
      </header>

      <main className="App-main">
        <div className="status-cards">
          <div className="status-card">
            <h2>Backend Status</h2>
            <p className={backendStatus === 'healthy' ? 'status-good' : 'status-bad'}>
              {backendStatus}
            </p>
          </div>
          
          <div className="status-card">
            <h2>Lottery API Status</h2>
            <p className={lotteryStatus === 'active' ? 'status-good' : 'status-bad'}>
              {lotteryStatus}
            </p>
          </div>
        </div>

        {loading ? (
          <div className="loading">Loading prediction...</div>
        ) : prediction ? (
          <div className="prediction-card">
            <h2>🎰 Today's Lottery Prediction</h2>
            <div className="numbers">
              {prediction.recommended_numbers.map((num, index) => (
                <span key={index} className="number">{num}</span>
              ))}
            </div>
            <p><strong>Strategy:</strong> {prediction.strategy}</p>
            <p><strong>Confidence:</strong> {prediction.confidence_score * 100}%</p>
            <button onClick={simulateBet} className="simulate-btn">
              Simulate Bet with [1, 15, 23, 34, 45]
            </button>
          </div>
        ) : (
          <div className="error">Could not load prediction</div>
        )}

        <div className="links">
          <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
            📚 API Documentation
          </a>
          <a href="http://localhost:8000/api/v1/lottery/analysis" target="_blank" rel="noopener noreferrer">
            📊 Lottery Analysis
          </a>
          <a href="http://localhost:8000/api/v1/lottery/last-draws" target="_blank" rel="noopener noreferrer">
            📈 Last Draws
          </a>
        </div>
      </main>

      <footer className="App-footer">
        <p>Prediction Point System v2.0.0 • Lottery Integration Enabled</p>
      </footer>
    </div>
  );
}

export default App;
