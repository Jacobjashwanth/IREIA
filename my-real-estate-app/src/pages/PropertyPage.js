// src/pages/PropertyPage.jsx
import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Chart from 'chart.js/auto';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { initMapWithProperties } from '../utils/maps';
import { FaBed, FaBath, FaRulerCombined, FaRegCalendarAlt } from 'react-icons/fa';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import '../styles/PropertyPage.css';

const PropertyPage = () => {
  const navigate = useNavigate();
  const chartRef = useRef(null);
  const [property, setProperty] = useState(null);
  const [schools, setSchools] = useState([]);

  useEffect(() => {
    const prop = JSON.parse(localStorage.getItem('selected_property'));
    if (!prop) {
      navigate('/');
      return;
    }
    setProperty(prop);
  }, [navigate]);

  useEffect(() => {
    if (!property) return;

    // Chart drawing
    const ctx = document.getElementById('priceChart')?.getContext('2d');
    if (ctx && chartRef.current) chartRef.current.destroy();

    if (ctx) {
      const labels = [
        ...property.historical_prices.map(p => p.date),
        ...Object.keys(property.future_forecast)
      ];
      const data = [
        ...property.historical_prices.map(p => p.price),
        ...Object.values(property.future_forecast)
      ];

      chartRef.current = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Price ($)',
            data,
            borderColor: '#4CAF50',
            backgroundColor: 'rgba(76, 175, 80, 0.1)',
            fill: true,
            tension: 0.5,
            pointRadius: 4,
            borderWidth: 3
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            y: {
              ticks: {
                callback: value => `$${value.toLocaleString()}`
              }
            }
          }
        }
      });
    }

    initMapWithProperties([property]); // For now, only selected property

    fetchNearbySchools(property.latitude, property.longitude);
  }, [property]);

  const fetchNearbySchools = (lat, lng) => {
    const service = new window.google.maps.places.PlacesService(document.createElement('div'));
    const request = {
      location: new window.google.maps.LatLng(lat, lng),
      radius: 2000,
      type: ['school']
    };
    service.nearbySearch(request, (results, status) => {
      if (status === window.google.maps.places.PlacesServiceStatus.OK) {
        setSchools(results.slice(0, 5));
      }
    });
  };

  if (!property) return null;

  const walkScore = Math.floor(Math.random() * 21) + 70;
  const transitScore = Math.floor(Math.random() * 21) + 60;

  return (
    <>
      <Navbar />
      <div className="property-page">
        <div className="property-info-card">
          <h2>{property.address}</h2>
          <div className="carousel">
            {[property.image_url, ...(property.gallery || [])].map((img, idx) => (
              <img key={idx} src={img} alt={`Property view ${idx + 1}`} className="carousel-img" />
            ))}
          </div>

          <div className="info-grid">
            <p><b>List Price:</b> ${property.current_price.toLocaleString()}</p>
            <p><FaBed /> <b>Beds:</b> {property.beds || 'N/A'} | <FaBath /> <b>Baths:</b> {property.baths || 'N/A'}</p>
            <p><FaRulerCombined /> <b>Sq Ft:</b> {property.sqft || 'N/A'} | <FaRegCalendarAlt /> <b>Year Built:</b> {property.year_built || 'N/A'}</p>
            <p className={property.recommendation.includes("Over") ? "predicted red" : "predicted green"}>
              <b>Predicted Price:</b> ${property.predicted_price.toLocaleString()} | {property.recommendation}
            </p>
          </div>
        </div>

        <div className="chart-section">
          <h3>📈 Future Price Prediction</h3>
          <canvas id="priceChart"></canvas>
        </div>

        <div className="side-by-side">
          <div className="scores-section">
            <h3>🚶 Walk & Transit Scores</h3>
            <div className="score-circles">
              <div className="score-circle">
                <CircularProgressbar
                  value={walkScore}
                  text={`${walkScore}%`}
                  styles={buildStyles({
                    pathColor: "#4CAF50",
                    textColor: "#333",
                    trailColor: "#eee"
                  })}
                />
                <p>Walk Score</p>
              </div>
              <div className="score-circle">
                <CircularProgressbar
                  value={transitScore}
                  text={`${transitScore}%`}
                  styles={buildStyles({
                    pathColor: "#2196F3",
                    textColor: "#333",
                    trailColor: "#eee"
                  })}
                />
                <p>Transit Score</p>
              </div>
            </div>
          </div>

          <div className="map-section">
            <h3>🗺️ Nearby Properties</h3>
            <div id="map" style={{ height: '300px', borderRadius: '10px' }}></div>
          </div>
        </div>

        <div className="schools-section">
          <h3>🏫 Nearby Schools</h3>
          <ul>
            {schools.map((school, idx) => (
              <li key={idx}>
                <b>{school.name}</b> — {school.vicinity || 'Location not available'}
              </li>
            ))}
          </ul>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default PropertyPage;