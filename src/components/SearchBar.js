import React, { useState } from 'react';
import '../styles/SearchBar.css';

const SearchBar = ({ onSearch }) => {
  const [searchParams, setSearchParams] = useState({
    zipcode: '',
    bedrooms: '2',
    bathrooms: '1',
    propertyType: 'SINGLE_FAMILY',
    livingArea: '1000'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchParams(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5001/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchParams),
      });

      if (!response.ok) {
        throw new Error('Failed to get prediction');
      }

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      onSearch({
        ...searchParams,
        predictedRent: data.predictedRent,
        predictedSalePrice: data.predictedSalePrice,
        coordinates: data.coordinates
      });
    } catch (error) {
      console.error('Error:', error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="search-container">
      <div className="search-box">
        <h2>Property Price Predictor</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label>Zipcode</label>
            <input
              type="text"
              name="zipcode"
              value={searchParams.zipcode}
              onChange={handleInputChange}
              placeholder="Enter zipcode"
              required
            />
          </div>

          <div className="input-group">
            <label>Bedrooms</label>
            <select
              name="bedrooms"
              value={searchParams.bedrooms}
              onChange={handleInputChange}
              required
            >
              {[1, 2, 3, 4, 5].map(num => (
                <option key={num} value={num}>{num}</option>
              ))}
            </select>
          </div>

          <div className="input-group">
            <label>Bathrooms</label>
            <select
              name="bathrooms"
              value={searchParams.bathrooms}
              onChange={handleInputChange}
              required
            >
              {[1, 1.5, 2, 2.5, 3, 3.5, 4].map(num => (
                <option key={num} value={num}>{num}</option>
              ))}
            </select>
          </div>

          <div className="input-group">
            <label>Living Area (sq ft)</label>
            <input
              type="number"
              name="livingArea"
              value={searchParams.livingArea}
              onChange={handleInputChange}
              placeholder="Square footage"
              min="500"
              max="10000"
              required
            />
          </div>

          <button 
            type="submit" 
            className="submit-button"
            disabled={isLoading}
          >
            {isLoading ? 'Calculating...' : 'Get Prediction'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SearchBar; 