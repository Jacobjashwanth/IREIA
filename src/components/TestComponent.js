import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TestComponent = () => {
  const [status, setStatus] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    testConnection();
  }, []);

  const testConnection = async () => {
    try {
      const response = await axios.get('http://localhost:5001/test');
      setStatus(response.data.message);
      console.log('Connection successful:', response.data);
    } catch (err) {
      setError(err.message);
      console.error('Connection error:', err);
    }
  };

  const handleTestSubmit = async () => {
    try {
      setError(null);
      const response = await axios.post('http://localhost:5001/api/predict', {
        bedrooms: 2,
        bathrooms: 1,
        sqft: 1000,
        zipcode: '02108',
        property_type: 'SINGLE_FAMILY'
      });

      console.log('Response:', response.data);
      alert('Success! Check console for response');
    } catch (err) {
      setError(err.message);
      console.error('Error:', err);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Connection Test</h2>
      <div style={{ marginBottom: '20px' }}>
        <button onClick={testConnection}>
          Test Connection
        </button>
      </div>
      {status && (
        <div style={{ 
          padding: '10px', 
          backgroundColor: '#e6ffe6', 
          borderRadius: '4px',
          marginBottom: '10px'
        }}>
          Server Status: {status}
        </div>
      )}
      {error && (
        <div style={{ 
          padding: '10px', 
          backgroundColor: '#ffe6e6', 
          borderRadius: '4px',
          marginBottom: '10px'
        }}>
          Error: {error}
        </div>
      )}
      <button onClick={handleTestSubmit}>
        Test POST Request
      </button>
    </div>
  );
};

export default TestComponent; 