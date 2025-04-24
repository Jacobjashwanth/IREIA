// src/pages/SearchPage.jsx
import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import PropertyCard from '../components/PropertyCard';
import { initMapWithProperties } from '../utils/maps';
import '../styles/SearchPage.css';

const SearchPage = () => {
  const [properties, setProperties] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const propertiesPerPage = 6;

  const queryParams = new URLSearchParams(window.location.search);
  const locationParam = queryParams.get('location') || '';
  const addressParam = queryParams.get('address') || '';
  const typeParam = queryParams.get('type') || '';

  useEffect(() => {
    const payload = {};
    if (locationParam) payload.location = locationParam;
    if (addressParam) payload.address = addressParam;
    if (typeParam) payload.property_type = typeParam;
  
    fetch('http://127.0.0.1:5000/search_property', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((data) => {
        const fetchedProperties = data.results || [];
        setProperties(fetchedProperties);
  
        // ✅ Save to localStorage for PropertyPage to access
        localStorage.setItem("nearby_properties", JSON.stringify(fetchedProperties));
  
        // ✅ Init Google Map
        if (window.google && window.google.maps) {
          initMapWithProperties(fetchedProperties);
        } else {
          window.initMap = () => initMapWithProperties(fetchedProperties);
        }
      });
  }, [locationParam, addressParam, typeParam]);

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
            Properties in <span style={{ textTransform: 'capitalize' }}>{locationParam || addressParam}</span>
          </h2>
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
        </div>
        <div id="map" className="map-section" />
      </div>
      <Footer />
    </div>
  );
};

export default SearchPage;