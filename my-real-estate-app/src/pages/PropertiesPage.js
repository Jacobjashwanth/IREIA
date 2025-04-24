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
  const propertiesPerPage = 6;

  useEffect(() => {
    const query = new URLSearchParams(window.location.search);
    const lat = query.get("lat");
    const lng = query.get("lng");

    if (!lat || !lng) {
      setError("Location access is required to fetch nearby properties.");
      return;
    }

    fetch('http://127.0.0.1:5000/search_property', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lat, lng })
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === "success") {
          const props = data.results || [];
          setProperties(props);
          setLocationName(data.location || "your area");

          if (window.google && window.google.maps) {
            initMapWithProperties(props);
          } else {
            window.initMap = () => initMapWithProperties(props);
          }
        } else {
          setError(data.message || "No properties found.");
        }
      })
      .catch(err => {
        console.error("Property fetch error:", err);
        setError("Unable to fetch nearby properties.");
      });
  }, []);

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

          {error ? (
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