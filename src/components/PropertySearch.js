import React, { useState } from 'react';
import './PropertySearch.css';

const PropertySearch = () => {
  const [location, setLocation] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      console.log('Sending request to server...');
      const response = await fetch('http://localhost:5001/search_property', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ location }),
      });

      console.log('Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Received data:', data);
      
      if (data.status === 'success') {
        setResults(data.results);
      } else {
        setError(data.message || 'Failed to fetch properties');
      }
    } catch (error) {
      console.error('Error:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="property-search-container">
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="Enter location (city or ZIP)"
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="results-grid">
          {results.map((property, index) => (
            <div key={index} className="property-card">
              <img src={property.image_url} alt={property.address} />
              <div className="property-info">
                <h3>{property.address}</h3>
                <p>{property.city}, {property.state} {property.zipcode}</p>
                <p>{property.beds} beds • {property.baths} baths • {property.sqft} sqft</p>
                <div className="price-info">
                  <p>Sale Price: ${property.predicted_sale_price.toLocaleString()}</p>
                  <p>Monthly Rent: ${property.predicted_rental_price.toLocaleString()}</p>
                </div>
                <div className="recommendation">
                  {property.recommendation}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PropertySearch; 