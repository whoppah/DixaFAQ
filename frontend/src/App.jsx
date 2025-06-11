//frontend/src/App.jsx
import React from "react";
import { HashRouter as Router, Routes, Route, Link } from "react-router-dom";
import ClusterDashboard from "./pages/ClusterDashboard";
import LoginPage from "./pages/LoginPage"; 

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow p-4 mb-6">
          <div className="container mx-auto flex justify-between">
            <h1 className="text-xl font-semibold text-blue-600">FAQ insight</h1>
            <div className="space-x-4">
              <Link to="/" className="text-gray-600 hover:text-blue-500">Dashboard</Link>
            </div>
          </div>
        </nav>
        <Routes>
          <Route path="/" element={<ClusterDashboard />} />
          <Route path="/#/login" element={<LoginPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
