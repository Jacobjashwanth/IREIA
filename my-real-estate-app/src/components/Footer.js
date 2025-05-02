// src/components/Footer.js
import React, { useEffect, useRef, useState } from 'react';
import { FaFacebookF, FaInstagram, FaLinkedinIn, FaTwitter } from 'react-icons/fa';
import '../styles/Footer.css';

const Footer = () => {
  const watermarkRef = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const target = watermarkRef.current;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    if (target) observer.observe(target);
    return () => {
      if (target) observer.unobserve(target);
    };
  }, []);

  // Optional: Parallax scroll effect
  useEffect(() => {
    const handleScroll = () => {
      const offset = window.scrollY - document.body.scrollHeight + window.innerHeight + 200;
      if (watermarkRef.current) {
        watermarkRef.current.style.setProperty('--scroll-offset', `${Math.min(offset * 0.15, 60)}px`);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

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
            <a href="https://facebook.com" target="_blank" rel="noopener noreferrer"><FaFacebookF /></a>
            <a href="https://twitter.com" target="_blank" rel="noopener noreferrer"><FaTwitter /></a>
            <a href="https://instagram.com" target="_blank" rel="noopener noreferrer"><FaInstagram /></a>
            <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer"><FaLinkedinIn /></a>
          </div>
        </div>

        {/* Middle */}
        <div className="footer-col">
          <ul>
            <li><strong><a href="/">Home</a></strong></li>
            <li><a href="/services">Services</a></li>
            <li><a href="/invest">Invest</a></li>
            <li><a href="/properties">Properties</a></li>
          </ul>
        </div>

        {/* Right */}
        <div className="footer-col">
          <ul>
            <li><strong><a href="/about">About</a></strong></li>
            <li><a href="/contact">Contact</a></li>
            <li><a href="/privacy">Privacy Policy</a></li>
            <li><a href="/terms">Terms & Conditions</a></li>
          </ul>
        </div>
      </div>

      <div className="footer-bottom">
        <p>© All Rights Reserved 2025 | <span className="footer-brand">IREIA</span></p>
      </div>

      <div
        ref={watermarkRef}
        className={`footer-watermark ${visible ? 'animate-watermark parallax' : ''}`}
      >
        IREIA
      </div>
    </footer>
  );
};

export default Footer;