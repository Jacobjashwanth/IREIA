import React, { useState } from 'react';
import '../styles/SearchBar.css';
import { useNavigate } from 'react-router-dom';

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
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchParams(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!searchParams.zipcode.trim()) {
      alert("Please enter a zipcode.");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5001/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          zipcode: searchParams.zipcode.trim(),
          bedrooms: parseInt(searchParams.bedrooms) || 2,
          bathrooms: parseInt(searchParams.bathrooms) || 1,
          propertyType: searchParams.propertyType || 'SINGLE_FAMILY',
          livingArea: parseInt(searchParams.livingArea) || 1000
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get prediction');
      }

      const data = await response.json();
      console.log('Raw API response:', data);
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      // Navigate to results page with the prediction data
      const searchParamsData = {
        zipcode: searchParams.zipcode.trim(),
        bedrooms: parseInt(searchParams.bedrooms) || 2,
        bathrooms: parseInt(searchParams.bathrooms) || 1,
        propertyType: searchParams.propertyType || 'SINGLE_FAMILY',
        livingArea: parseInt(searchParams.livingArea) || 1000,
        predictedRent: data.predictedRent,
        predictedSalePrice: data.predictedSalePrice,
        areaInfo: {
          name: searchParams.zipcode,
          fullAddress: `${searchParams.zipcode}, USA`
        }
      };
      
      console.log('Data being passed to results page:', searchParamsData);
      
      navigate('/results', {
        state: {
          searchParams: searchParamsData
        }
      });
    } catch (error) {
      console.error('Error:', error);
      alert(error.message || 'Error making prediction. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="search-container">
      <div className="search-box">
        <h2>Property Price Predictor</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit} className="search-inputs">
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
            <input
              type="number"
              name="bedrooms"
              value={searchParams.bedrooms}
              onChange={handleInputChange}
              min="1"
              required
            />
          </div>

          <div className="input-group">
            <label>Bathrooms</label>
            <input
              type="number"
              name="bathrooms"
              value={searchParams.bathrooms}
              onChange={handleInputChange}
              min="1"
              step="0.5"
              required
            />
          </div>

          <div className="input-group">
            <label>Living Area (sqft)</label>
            <input
              type="number"
              name="livingArea"
              value={searchParams.livingArea}
              onChange={handleInputChange}
              min="100"
              required
            />
          </div>

          <div className="input-group">
            <label>Property Type</label>
            <select
              name="propertyType"
              value={searchParams.propertyType}
              onChange={handleInputChange}
              required
            >
              <option value="SINGLE_FAMILY">Single Family</option>
              <option value="MULTI_FAMILY">Multi Family</option>
              <option value="CONDO">Condo</option>
              <option value="TOWNHOUSE">Townhouse</option>
            </select>
          </div>

          <button type="submit" className="search-btn" disabled={isLoading}>
            {isLoading ? 'Calculating...' : 'Get Predictions'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SearchBar;