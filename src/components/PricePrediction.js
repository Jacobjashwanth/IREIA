import React, { useState } from 'react';
import './PricePrediction.css';

const PricePrediction = () => {
  const [formData, setFormData] = useState({
    bedrooms: '2',
    bathrooms: '1',
    sqft: '1000',
    zipcode: '02108',
    propertyType: 'SINGLE_FAMILY'
  });
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPredictions(null); // Reset predictions

    try {
      console.log('Sending request with data:', formData);
      
      const response = await fetch('http://localhost:5001/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Received data:', data);

      // Check if we have the required prediction fields
      if (data.predictedSalePrice !== undefined && data.predictedRent !== undefined) {
        console.log('Setting predictions:', {
          predictedSalePrice: data.predictedSalePrice,
          predictedRent: data.predictedRent
        });
        setPredictions({
          predictedSalePrice: data.predictedSalePrice,
          predictedRent: data.predictedRent
        });
      } else {
        console.error('Missing prediction data in response:', data);
        console.error('Response keys:', Object.keys(data));
        setError('Invalid response format from server');
      }
    } catch (error) {
      console.error('Error:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prediction-container">
      <h2>Property Price Prediction</h2>
      
      <form onSubmit={handleSubmit} className="prediction-form">
        <div className="form-group">
          <label>Bedrooms</label>
          <select
            name="bedrooms"
            value={formData.bedrooms}
            onChange={handleInputChange}
            required
          >
            {[1, 2, 3, 4, 5].map(num => (
              <option key={num} value={num}>{num}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Bathrooms</label>
          <select
            name="bathrooms"
            value={formData.bathrooms}
            onChange={handleInputChange}
            required
          >
            {[1, 1.5, 2, 2.5, 3, 3.5, 4].map(num => (
              <option key={num} value={num}>{num}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Square Footage</label>
          <input
            type="number"
            name="sqft"
            value={formData.sqft}
            onChange={handleInputChange}
            min="500"
            max="10000"
            required
          />
        </div>

        <div className="form-group">
          <label>Zipcode</label>
          <input
            type="text"
            name="zipcode"
            value={formData.zipcode}
            onChange={handleInputChange}
            pattern="[0-9]{5}"
            maxLength="5"
            required
          />
        </div>

        <div className="form-group">
          <label>Property Type</label>
          <select
            name="propertyType"
            value={formData.propertyType}
            onChange={handleInputChange}
            required
          >
            <option value="SINGLE_FAMILY">Single Family</option>
            <option value="MULTI_FAMILY">Multi Family</option>
            <option value="CONDO">Condo</option>
            <option value="TOWNHOUSE">Townhouse</option>
          </select>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Calculating...' : 'Get Predictions'}
        </button>
      </form>

      {loading && (
        <div className="loading-message">
          Calculating predictions...
        </div>
      )}

      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}

      {predictions && (
        <div className="predictions-result">
          <div className="prediction-card">
            <h3>Area: {formData.zipcode}</h3>
            <div className="property-details">
              <h3>Predicted Sale Price</h3>
              <p className="price">${predictions.predictedSalePrice.toLocaleString()}</p>
              <p><strong>Bedrooms:</strong> {formData.bedrooms}</p>
              <p><strong>Property Type:</strong> {formData.propertyType}</p>
              <p><strong>Zipcode:</strong> {formData.zipcode}</p>
              <p><strong>Address:</strong> {formData.zipcode}, USA</p>
            </div>
          </div>
          <div className="prediction-card">
            <h3>Area: {formData.zipcode}</h3>
            <div className="property-details">
              <h3>Predicted Monthly Rent</h3>
              <p className="price">${predictions.predictedRent.toLocaleString()}</p>
              <p><strong>Bedrooms:</strong> {formData.bedrooms}</p>
              <p><strong>Property Type:</strong> {formData.propertyType}</p>
              <p><strong>Zipcode:</strong> {formData.zipcode}</p>
              <p><strong>Address:</strong> {formData.zipcode}, USA</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PricePrediction; 