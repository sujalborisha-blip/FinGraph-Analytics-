import React from "react";
import GraphView from "./GraphViz";

function Dashboard() {
  return (
    <div className="dashboard">

      <header className="dashboard-header">
        <div>
          <h1>FinGraph</h1>
          <p>Fraud Syndicate Analytics</p>
        </div>

        <div className="connection-status">
          ● Neo4j Connected
        </div>
      </header>

      <main className="dashboard-content">

        <section className="dashboard-title">
          <h2>Fraud Network</h2>
          <p>
            Interactive visualization of connected accounts and transactions.
          </p>
        </section>

        <section className="graph-card">
          <GraphView />
        </section>

      </main>

    </div>
  );
}

export default Dashboard;