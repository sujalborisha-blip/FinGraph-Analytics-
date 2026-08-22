import React, { useState, useEffect } from 'react';
import './Dashboard.css';

const Dashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [systemStatus, setSystemStatus] = useState('SECURE');

  // Simulated live data feed from Neo4j / Flink
  useEffect(() => {
    const mockFraudData = {
      tx_id: "edeacd85-2621-47b0-bdf6",
      type: "FRAUD_LAYERING",
      amount: 9900.0,
      timestamp: new Date().toLocaleTimeString()
    };

    const timer = setTimeout(() => {
      setAlerts([mockFraudData]);
      setSystemStatus('CRITICAL - SYNDICATE DETECTED');
    }, 5000); // Trigger a fake fraud alert after 5 seconds

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className={`dashboard-container ${systemStatus === 'SECURE' ? 'theme-dark' : 'theme-alert'}`}>
      <header className="dashboard-header">
        <h1>FinGraph AML Dashboard</h1>
        <div className={`status-badge ${systemStatus.toLowerCase().split(' ')[0]}`}>
          Status: {systemStatus}
        </div>
      </header>

      <main className="dashboard-grid">
        <section className="graph-visualization">
          <h2>Live Graph Database (Neo4j)</h2>
          <div className="graph-placeholder">
            {/* Future integration: react-force-graph to visualize Neo4j nodes */}
            <p className="placeholder-text">Graph Network Visualization Loading...</p>
            {systemStatus !== 'SECURE' && (
              <div className="fraud-node-highlight">
                🚨 Anomalous Node Cluster Identified
              </div>
            )}
          </div>
        </section>

        <section className="alert-feed">
          <h2>Real-Time Security Alerts</h2>
          {alerts.length === 0 ? (
            <p className="no-alerts">No suspicious activity detected in the stream.</p>
          ) : (
            <ul className="alert-list">
              {alerts.map((alert, index) => (
                <li key={index} className="alert-item">
                  <strong>[ALERT]</strong> Pattern: {alert.type} <br/>
                  Amount: ${alert.amount} <br/>
                  Time: {alert.timestamp} <br/>
                  <div className="action-buttons">
                    <button className="btn-freeze" onClick={() => alert("Account Frozen")}>Freeze Account</button>
                    <button className="btn-dismiss" onClick={() => setAlerts([])}>Dismiss</button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  );
};

export default Dashboard;
