import React, { useState } from 'react';
import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';

const Map = ({ center, zoom = 12 }) => {
  const [mapError, setMapError] = useState(null);
  const [isMapLoaded, setIsMapLoaded] = useState(false);

  const mapContainerStyle = {
    width: '100%',
    height: '400px'
  };

  const options = {
    disableDefaultUI: true,
    zoomControl: true,
    styles: [
      {
        featureType: 'poi',
        elementType: 'labels',
        stylers: [{ visibility: 'off' }]
      }
    ]
  };

  const handleLoad = () => {
    setIsMapLoaded(true);
  };

  const handleLoadError = () => {
    setMapError('Failed to load Google Maps. Please check your internet connection.');
  };

  if (mapError) {
    return (
      <div className="map-error">
        <p>{mapError}</p>
      </div>
    );
  }

  return (
    <LoadScript 
      googleMapsApiKey="AIzaSyAC2_CrKzi9aSnFXsQdwixcuEVzPmdNbnk"
      onLoad={handleLoad}
      onError={handleLoadError}
    >
      {isMapLoaded && (
        <GoogleMap
          mapContainerStyle={mapContainerStyle}
          center={center}
          zoom={zoom}
          options={options}
        >
          <Marker position={center} />
        </GoogleMap>
      )}
    </LoadScript>
  );
};

export default Map; 