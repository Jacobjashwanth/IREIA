// src/components/Footer.js
import React from 'react';
import '../styles/Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        {/* Left */}
        <div className="footer-col">
          <p>
            Stay connected, explore opportunities,<br />
            and invest with confidence. Your real<br />
            estate success starts here
          </p>
          <div className="footer-socials">
            <i className="fab fa-facebook-f"></i>
            <i className="fab fa-twitter"></i>
            <i className="fab fa-instagram"></i>
            <i className="fab fa-linkedin-in"></i>
          </div>
        </div>

        {/* Middle */}
        <div className="footer-col">
          <ul>
            <li><strong>Home</strong></li>
            <li>Services</li>
            <li>Invest</li>
            <li>Properties</li>
          </ul>
        </div>

        {/* Right */}
        <div className="footer-col">
          <ul>
            <li><strong>About</strong></li>
            <li>Contact</li>
            <li>Privacy Policy</li>
            <li>Terms & Conditions</li>
          </ul>
        </div>
      </div>

      <div className="footer-bottom">
        <p>© All Rights Reserved 2025 | <span className="footer-brand">IREIA</span></p>
      </div>

      <div className="footer-watermark">IREIA</div>
    </footer>
  );
};

export default Footer;