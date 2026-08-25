function Dashboard() {
  return (
    <div>
      <h2>Dashboard</h2>
      <p>This is your dashboard page content.</p>
      
      {/* Placeholder graph area */}
      <div 
        id="graph-area" 
        style={{
          border: "1px solid #ccc", 
          padding: "20px", 
          marginTop: "20px", 
          backgroundColor: "#fafafa",
          textAlign: "center"
        }}
      >
        Graph visualization will load here...
      </div>
    </div>
  );
}

export default Dashboard;
