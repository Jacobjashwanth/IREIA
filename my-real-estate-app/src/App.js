import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import PropertyPage from './pages/PropertyPage';
import SearchPage from './pages/SearchPage';
import PropertiesPage from './pages/PropertiesPage'; // New import for the properties page
import ResultsPage from './pages/ResultsPage';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import './App.css';

// Update your routing logic
function App() {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/property" element={<PropertyPage />} />
          <Route path="/properties" element={<PropertiesPage />} />
          <Route path="/results" element={<ResultsPage />} />
          {/* Add more routes as necessary */}
        </Routes>
        <Footer />
      </div>
    </Router>
  );
}

export default App;