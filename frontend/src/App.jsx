//frontend/src/App.jsx
import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import ClusterDashboard from "./pages/ClusterDashboard";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow p-4 mb-6">
          <div className="container mx-auto flex justify-between">
            <h1 className="text-xl font-semibold text-blue-600">FAQ Analyzer</h1>
            <div className="space-x-4">
              <Link to="/" className="text-gray-600 hover:text-blue-500">Dashboard</Link>
            </div>
          </div>
        </nav>
        <Routes>
          <Route path="/" element={<ClusterDashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
