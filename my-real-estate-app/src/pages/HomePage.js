// src/pages/HomePage.js
import React, { useEffect, useState } from 'react';
import Footer from '../components/Footer';
import Navbar from '../components/Navbar';
import PropertyCard from '../components/PropertyCard';
import SearchBar from '../components/SearchBar';
import '../styles/HomePage.css';

const HomePage = () => {
  const [properties, setProperties] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const propertiesPerPage = 10;

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(async (position) => {
        const { latitude, longitude } = position.coords;
        const res = await fetch(`https://maps.googleapis.com/maps/api/geocode/json?latlng=${latitude},${longitude}&key=AIzaSyAC2_CrKzi9aSnFXsQdwixcuEVzPmdNbnk`);
        const data = await res.json();
        const components = data.results[0]?.address_components || [];
        const zip = components.find(c => c.types.includes("postal_code"))?.long_name;
        const city = components.find(c => c.types.includes("locality"))?.long_name;

        const location = zip || city || '02127'; // fallback if geolocation fails

        fetch('https://ireia.onrender.com/search_property', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ location }),
        })
          .then((response) => response.json())
          .then((data) => setProperties(data.results || []));
      });
    }
  }, []);

  const indexOfLast = currentPage * propertiesPerPage;
  const indexOfFirst = indexOfLast - propertiesPerPage;
  const currentProperties = properties.slice(indexOfFirst, indexOfLast);
  const totalPages = Math.ceil(properties.length / propertiesPerPage);

  const handlePageChange = (pageNum) => {
    if (pageNum >= 1 && pageNum <= totalPages) {
      setCurrentPage(pageNum);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div>
      <Navbar />
      <div className='hero-container'>
        <h1>Find Your Perfect Investment Properties</h1>
        <SearchBar /> {/* no setProperties here — user-triggered search redirects */}
      </div>

      <div className='property-container'>
        <div className="property-heading">
          <h2>Featured Properties</h2>
        </div>

        <section className="property-grid">
          {currentProperties.map((property, index) => (
            <PropertyCard key={index} property={property} />
          ))}
        </section>

        <div className="pagination">
          <button onClick={() => handlePageChange(currentPage - 1)} disabled={currentPage === 1}>&lt;</button>
          {[...Array(totalPages)].map((_, i) => (
            <button
              key={i}
              onClick={() => handlePageChange(i + 1)}
              className={currentPage === i + 1 ? 'active' : ''}
            >
              {i + 1}
            </button>
          ))}
          <button onClick={() => handlePageChange(currentPage + 1)} disabled={currentPage === totalPages}>&gt;</button>
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