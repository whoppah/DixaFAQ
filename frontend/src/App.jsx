//frontend/src/App.jsx
import React, { useEffect, useState } from "react";
import { HashRouter as Router, Routes, Route, Link, Navigate, useLocation } from "react-router-dom";
import ClusterDashboard from "./pages/ClusterDashboard";
import LoginPage from "./pages/LoginPage";
import axios from "axios";

axios.defaults.withCredentials = true;
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || "";

function PrivateRoute({ children }) {
  const [user, setUser] = useState(null);
  const [checked, setChecked] = useState(false);
  const location = useLocation();

  useEffect(() => {
    axios.get("/api/current-user-info/")
      .then(res => setUser(res.data))
      .catch(() => setUser(null))
      .finally(() => setChecked(true));
  }, []);

  if (!checked) return null;  
  return user ? children : <Navigate to="/login" state={{ from: location }} />;
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow p-4 mb-6">
          <div className="container mx-auto flex justify-between">
            <h1 className="text-xl font-semibold text-blue-600">FAQ Analyzer</h1>
          </div>
        </nav>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={
            <PrivateRoute>
              <ClusterDashboard />
            </PrivateRoute>
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
