import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './Navbar';
import Dashboard from './Dashboard';

function App() {
  return (
    <Router>
      <div>
        <h1>FinGraph UI</h1>
        <Navbar />
        <Routes>
          <Route path="/" element={<p>Welcome to your first React app!</p>} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/reports" element={<p>Reports page coming soon!</p>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
