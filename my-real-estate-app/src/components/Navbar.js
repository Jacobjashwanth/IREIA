import React from "react";
import "../styles/Navbar.css";

const Navbar = () => {
  const handlePropertiesClick = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          window.location.href = `/properties?lat=${latitude}&lng=${longitude}`;
        },
        (error) => {
          console.error(error);
          const userLocation = prompt("📍 We couldn't detect your location. Please enter your City or ZIP code:");

          if (userLocation && userLocation.trim() !== "") {
            window.location.href = `/properties?location=${encodeURIComponent(userLocation.trim())}`;
          } else {
            alert("❌ Location is required to search properties.");
          }
        }
      );
    } else {
      const userLocation = prompt("📍 Geolocation not supported. Please enter your City or ZIP code:");
      if (userLocation && userLocation.trim() !== "") {
        window.location.href = `/properties?location=${encodeURIComponent(userLocation.trim())}`;
      } else {
        alert("❌ Location is required to search properties.");
      }
    }
  };

  return (
    <div className="navbar-container">
      <nav className="navbar">
        <div><span className="logo-name">IREIA</span></div>
        <ul className="nav-links">
          <li><a href="/">Home</a></li>
          <li><button className="nav-link" onClick={handlePropertiesClick}>Properties</button></li>
          <li><a href="/loan">Loan</a></li>
          <li><a href="/about">About</a></li>
          <li><a href="/contact">Contact</a></li>
        </ul>
        <div className="nav-buttons">
          <button className="login-btn">Log in</button>
          <button className="join-btn">Join now</button>
        </div>
      </nav>
    </div>
  );
};

export default Navbar;