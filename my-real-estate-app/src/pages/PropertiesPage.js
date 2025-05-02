// src/pages/PropertiesPage.jsx
import React, { useEffect, useState } from 'react';
import Footer from '../components/Footer';
import Navbar from '../components/Navbar';
import PropertyCard from '../components/PropertyCard';
import '../styles/SearchPage.css';
import { initMapWithProperties } from '../utils/maps';

const PropertiesPage = () => {
  const [properties, setProperties] = useState([]);
  const [locationName, setLocationName] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [error, setError] = useState('');
  const [needsManualLocation, setNeedsManualLocation] = useState(false);
  const [manualLocationInput, setManualLocationInput] = useState('');
  const propertiesPerPage = 6;

  useEffect(() => {
    const query = new URLSearchParams(window.location.search);
    const lat = query.get("lat");
    const lng = query.get("lng");
    const locationParam = query.get("location");

    if (locationParam) {
      fetchPropertiesFromLocation(locationParam);
    } else if (lat && lng) {
      reverseGeocode(lat, lng);
    } else {
      setNeedsManualLocation(true);
    }
  }, []);

  const reverseGeocode = async (lat, lng) => {
    try {
      const res = await fetch(`https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=AIzaSyAC2_CrKzi9aSnFXsQdwixcuEVzPmdNbnk`);
      const data = await res.json();

      if (data.status === 'OK' && data.results.length > 0) {
        const addressComponents = data.results[0].address_components;
        const city = addressComponents.find(c => c.types.includes('locality'));
        const zip = addressComponents.find(c => c.types.includes('postal_code'));

        const location = city?.long_name || zip?.long_name;
        if (location) {
          fetchPropertiesFromLocation(location);
          return;
        }
      }
      setNeedsManualLocation(true);
    } catch (err) {
      console.error('Reverse geocoding failed:', err);
      setNeedsManualLocation(true);
    }
  };

  const fetchPropertiesFromLocation = async (location) => {
    try {
      setLocationName(location);

      const response = await fetch('http://127.0.0.1:5000/search_property', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location })
      });

      const data = await response.json();

      if (data.status === 'success') {
        const props = data.results || [];
        setProperties(props);

        if (window.google && window.google.maps) {
          initMapWithProperties(props);
        } else {
          window.initMap = () => initMapWithProperties(props);
        }
      } else {
        setError(data.message || 'No properties found.');
      }
    } catch (err) {
      console.error('Property fetch error:', err);
      setError('Unable to fetch properties.');
    }
  };

  const handleManualSubmit = () => {
    if (!manualLocationInput.trim()) {
      alert("Please enter a valid location.");
      return;
    }
    fetchPropertiesFromLocation(manualLocationInput.trim());
    setNeedsManualLocation(false);
  };

  const indexOfLast = currentPage * propertiesPerPage;
  const indexOfFirst = indexOfLast - propertiesPerPage;
  const currentProperties = properties.slice(indexOfFirst, indexOfLast);
  const totalPages = Math.ceil(properties.length / propertiesPerPage);

  return (
    <div>
      <Navbar />
      <div className="search-page">
        <div className="results-list">
          <h2 className="section-title">
            Properties near <span style={{ textTransform: 'capitalize' }}>{locationName}</span>
          </h2>

          {needsManualLocation ? (
            <div className="manual-location-box">
              <h3>📍 Enter Your Location</h3>
              <input
                type="text"
                value={manualLocationInput}
                onChange={(e) => setManualLocationInput(e.target.value)}
                placeholder="Enter City, ZIP or County"
              />
              <button onClick={handleManualSubmit}>Search</button>
            </div>
          ) : error ? (
            <p className="error-message">{error}</p>
          ) : (
            <>
              <div className="property-list">
                {currentProperties.map((property, index) => (
                  <PropertyCard key={index} property={property} />
                ))}
              </div>
              <div className="pagination">
                {Array.from({ length: totalPages }, (_, i) => (
                  <button
                    key={i}
                    className={currentPage === i + 1 ? 'active' : ''}
                    onClick={() => setCurrentPage(i + 1)}
                  >
                    {i + 1}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        <div id="map" className="map-section" />
      </div>
      <Footer />
    </div>
  );
};

export default PropertiesPage;