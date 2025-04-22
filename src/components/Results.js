import React from 'react';
import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';
import '../styles/Results.css';

const Results = ({ results }) => {
  const mapContainerStyle = {
    width: '100%',
    height: '400px'
  };

  const center = results?.coordinates || {
    lat: 42.3601,
    lng: -71.0589
  };

  return (
    <div className="results-container">
      <div className="predictions-container">
        <div className="prediction-card">
          <h3>Estimated Sale Price</h3>
          <p className="price">${results?.predictedSalePrice?.toLocaleString()}</p>
        </div>
        <div className="prediction-card">
          <h3>Estimated Monthly Rent</h3>
          <p className="price">${results?.predictedRent?.toLocaleString()}</p>
        </div>
      </div>

      <div className="map-container">
        <LoadScript googleMapsApiKey="YOUR_GOOGLE_MAPS_API_KEY">
          <GoogleMap
            mapContainerStyle={mapContainerStyle}
            zoom={13}
            center={center}
          >
            <Marker position={center} />
          </GoogleMap>
        </LoadScript>
      </div>
    </div>
  );
};

export default Results; 