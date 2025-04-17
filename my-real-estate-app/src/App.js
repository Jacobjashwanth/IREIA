import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';

import HomePage from './pages/HomePage';
import PropertyPage from './pages/PropertyPage';
import SearchPage from './pages/SearchPage';
import PropertiesPage from './pages/PropertiesPage'; // New import for the properties page

// Update your routing logic
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/property" element={<PropertyPage />} />
        <Route path="/properties" element={<PropertiesPage />} />
        {/* Add more routes as necessary */}
      </Routes>
    </Router>
  );
}

export default App;