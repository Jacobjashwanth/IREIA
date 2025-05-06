import Chart from 'chart.js/auto';
import React, { useEffect, useRef, useState } from 'react';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import { FaBath, FaBed, FaRegCalendarAlt, FaRulerCombined } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import Footer from '../components/Footer';
import Navbar from '../components/Navbar';
import '../styles/PropertyPage.css';
import { initMapWithProperties } from '../utils/maps';

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

    const priceCtx = document.getElementById('priceChart')?.getContext('2d');
    if (priceCtx && chartRef.current) chartRef.current.destroy();

    if (priceCtx) {
      const labels = [
        ...property.historical_prices.map(p => p.date),
        ...Object.keys(property.future_forecast)
      ];
      const data = [
        ...property.historical_prices.map(p => p.price),
        ...Object.values(property.future_forecast)
      ];

      chartRef.current = new Chart(priceCtx, {
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

    const rentCtx = document.getElementById('rentChart')?.getContext('2d');
    if (rentCtx) {
      const rentForecast = property.future_forecast_rent || {};
      const historicalRent = property.historical_rental_prices || [];

      if (Object.keys(rentForecast).length === 0) {
        new Chart(rentCtx, {
          type: 'bar',
          data: {
            labels: ['No Data Available'],
            datasets: [{
              label: 'Monthly Rent ($)',
              data: [0],
              backgroundColor: 'rgba(200, 200, 200, 0.6)',
              borderColor: '#C8C8C8',
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { display: false },
              tooltip: {
                callbacks: {
                  label: function () {
                    return 'Rent forecast not available';
                  }
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                display: false
              }
            }
          }
        });
      } else {
        const labels = [
          ...historicalRent.map(p => p.date),
          ...Object.keys(rentForecast)
        ];
        const data = [
          ...historicalRent.map(p => p.rent_price),
          ...Object.values(rentForecast)
        ];

        new Chart(rentCtx, {
          type: 'bar',
          data: {
            labels,
            datasets: [{
              label: 'Monthly Rent ($)',
              data,
              backgroundColor: 'rgba(33, 150, 243, 0.6)',
              borderColor: '#2196F3',
              borderWidth: 2,
              borderRadius: 5
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { display: false },
              tooltip: {
                callbacks: {
                  label: function (context) {
                    return `$${context.raw.toLocaleString()}/month`;
                  }
                }
              }
            },
            scales: {
              y: {
                beginAtZero: false,
                ticks: {
                  callback: value => `$${value.toLocaleString()}`
                }
              }
            }
          }
        });
      }
    }

    initMapWithProperties([property]);

    const lat = parseFloat(property.latitude);
    const lng = parseFloat(property.longitude);

    if (!isNaN(lat) && !isNaN(lng)) {
      fetchNearbySchools(lat, lng);
    }
  }, [property]);

  const fetchNearbySchools = (lat, lng) => {
    if (!lat || !lng || !window.google?.maps?.places) {
      console.warn("❌ Google Maps or coordinates not ready.");
      return;
    }

    const location = new window.google.maps.LatLng(parseFloat(lat), parseFloat(lng));
    const map = new window.google.maps.Map(document.createElement('div'));
    const service = new window.google.maps.places.PlacesService(map);

    const request = {
      location,
      radius: 3000,
      type: 'school'
    };

    service.nearbySearch(request, (results, status) => {
      if (status === window.google.maps.places.PlacesServiceStatus.OK) {
        setSchools(results.slice(0, 5));
      } else {
        setSchools([]);
      }
    });
  };

  if (!property) return null;

  const walkScore = Math.floor(Math.random() * 21) + 70;
  const transitScore = Math.floor(Math.random() * 21) + 60;

  // ⭐ Investment Score with fallback and yield logic
  let investmentScore = 0;
  let investmentColor = '#e74c3c';

  if (property.predicted_rent && property.current_price) {
    const annualRent = property.predicted_rent * 12;
    const rentYield = (annualRent / property.current_price) * 100;
    investmentScore = Math.min(100, Math.round(rentYield));
    investmentColor = investmentScore >= 6 ? '#2ecc71' : '#e74c3c';
  }

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
            <p><FaBed /> <b>Beds:</b> {property.beds || 'N/A'} | <FaBath /> <b>Baths:</b> {property.baths || 'N/A'}</p>
            <p><FaRulerCombined /> <b>Sq Ft:</b> {property.sqft || 'N/A'} | <FaRegCalendarAlt /> <b>Year Built:</b> {property.year_built || 'N/A'}</p>
            <p><b>List Price:</b> ${property.current_price.toLocaleString()}</p>
            <p><b>Monthly Rent:</b> ${property.rent_price?.toLocaleString() || 'N/A'}</p>
            <p className={property.recommendation.includes("Over") ? "predicted red" : "predicted green"}>
              <b>Predicted Price:</b> ${property.predicted_price.toLocaleString()} | {property.recommendation}
            </p>
            <p className={property.recommendation.includes("Over") ? "predicted red" : "predicted green"}>
              <b>Predicted Monthly Rent:</b> ${property.predicted_rent?.toLocaleString()}
            </p>
          </div>
        </div>

        <div className="charts-container">
          <div className="chart-section">
            <h3>📈 Future Price Prediction</h3>
            <canvas id="priceChart"></canvas>
          </div>

          <div className="chart-section">
            <h3>💰 Monthly Rental Price Forecast</h3>
            <canvas id="rentChart"></canvas>
          </div>
        </div>

        <div className="side-by-side">
          <div className="scores-section">
            <h3>📊 Investment, Walk & Transit Scores</h3>
            <div className="score-circles">
              <div className="score-circle">
                <CircularProgressbar
                  value={walkScore}
                  text={`${walkScore}%`}
                  styles={buildStyles({ pathColor: "#4CAF50", textColor: "#333", trailColor: "#eee" })}
                />
                <p>Walk Score</p>
              </div>
              <div className="score-circle">
                <CircularProgressbar
                  value={transitScore}
                  text={`${transitScore}%`}
                  styles={buildStyles({ pathColor: "#2196F3", textColor: "#333", trailColor: "#eee" })}
                />
                <p>Transit Score</p>
              </div>
              <div className="score-circle">
                <CircularProgressbar
                  value={investmentScore}
                  text={`${investmentScore}%`}
                  styles={buildStyles({ pathColor: investmentColor, textColor: "#333", trailColor: "#eee" })}
                />
                <p>Investment Score</p>
              </div>
            </div>
          </div>

          <div className="map-section">
            <h3>🗺️ Property On Map</h3>
            <div id="map" style={{ height: '300px', borderRadius: '10px' }}></div>
          </div>
        </div>

        <div className="schools-section">
          <h3>🏫 Nearby Schools</h3>
          <ul>
            {schools.length > 0 ? (
              schools.map((school, idx) => (
                <li key={idx}>
                  <b>{school.name}</b>{school.vicinity ? ` — ${school.vicinity}` : ''}
                </li>
              ))
            ) : (
              <li>No nearby schools found.</li>
            )}
          </ul>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default PropertyPage;
