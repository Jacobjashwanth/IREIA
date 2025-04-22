// src/pages/HomePage.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Footer from '../components/Footer';
import Navbar from '../components/Navbar';
import PropertyCard from '../components/PropertyCard';
import SearchBar from '../components/SearchBar';
import Map from '../components/Map';
import '../styles/HomePage.css';

const HomePage = () => {
  const navigate = useNavigate();
  const [properties, setProperties] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const propertiesPerPage = 10;
  const [error, setError] = useState('');
  const [location, setLocation] = useState({ lat: 37.7749, lng: -122.4194 }); // Default to San Francisco
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const getLocation = () => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            setLocation({
              lat: position.coords.latitude,
              lng: position.coords.longitude
            });
            setIsLoading(false);
          },
          (error) => {
            console.error('Error getting location:', error);
            // Keep default location if geolocation fails
            setIsLoading(false);
          },
          {
            enableHighAccuracy: true,
            timeout: 5000,
            maximumAge: 0
          }
        );
      } else {
        console.error('Geolocation is not supported by this browser');
        setIsLoading(false);
      }
    };

    getLocation();
  }, []);

  const handleSearch = (searchResults) => {
    if (!searchResults.zipcode || !searchResults.bedrooms || !searchResults.propertyType) {
      setError('Please fill in all required fields');
      return;
    }
    setError('');
    
    // Navigate to results page with all search parameters
    navigate('/results', { 
      state: { 
        searchParams: {
          zipcode: searchResults.zipcode,
          bedrooms: searchResults.bedrooms,
          propertyType: searchResults.propertyType,
          predictedRent: searchResults.predictedRent,
          predictedSalePrice: searchResults.predictedSalePrice
        }
      }
    });
  };

  return (
    <div className="home-page">
      <Navbar />
      <div className="hero-section">
        <h1>Find Your Perfect Home</h1>
        <p>Search through thousands of properties to find your dream home</p>
      </div>

      <div className="search-section">
        <SearchBar onSearch={handleSearch} />
        {error && <div className="error-message">{error}</div>}
      </div>

      <div className="map-section">
        {isLoading ? (
          <div className="loading-spinner">Loading map...</div>
        ) : (
          <Map center={location} />
        )}
      </div>

      <div className="features-section">
        <div className="feature-card">
          <h3>Smart Search</h3>
          <p>Find properties that match your exact criteria</p>
        </div>
        <div className="feature-card">
          <h3>Real-time Updates</h3>
          <p>Get instant notifications for new listings</p>
        </div>
        <div className="feature-card">
          <h3>Expert Support</h3>
          <p>Our team is here to help you every step of the way</p>
        </div>
      </div>

      <div className='property-container'>
        <div className="property-heading">
          <h2>Featured Properties</h2>
        </div>

        <section className="property-grid">
          {properties.map((property, index) => (
            <PropertyCard key={index} property={property} />
          ))}
        </section>

        <div className="pagination">
          {[...Array(Math.ceil(properties.length / propertiesPerPage))].map((_, i) => (
            <button
              key={i}
              onClick={() => {
                setCurrentPage(i + 1);
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
              className={currentPage === i + 1 ? 'active' : ''}
            >
              {i + 1}
            </button>
          ))}
        </div>

        <div className="cta-section">
          <h2>Invest in real estate with confidence</h2>
          <button className="cta-btn">Invest Now</button>
        </div>

        <Footer />
      </div>
    </div>
  );
};

export default HomePage;