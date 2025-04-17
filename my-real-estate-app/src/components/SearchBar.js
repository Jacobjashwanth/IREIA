import React, { useState } from 'react';
import '../styles/SearchBar.css';

const SearchBar = () => {
  const [address, setAddress] = useState('');
  const [location, setLocation] = useState('');
  const [propertyType, setPropertyType] = useState('');

  const handleSearch = () => {
    if (!address.trim() && !location.trim()) {
      alert("Please enter an address or location.");
      return;
    }

    const queryParams = new URLSearchParams();
    if (address) queryParams.append('address', address.trim());
    if (location) queryParams.append('location', location.trim());
    if (propertyType) queryParams.append('type', propertyType.trim());

    window.location.href = `/search?${queryParams.toString()}`;
  };

  return (
    <div className="search-box">
      <div className="search-inputs">
        <input
          type="text"
          placeholder="Enter address"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
        />
        <input
          type="text"
          placeholder="Location (ZIP, City, or County)"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
        />
        <select value={propertyType} onChange={(e) => setPropertyType(e.target.value)}>
          <option value="">Property type</option>
          <option value="Single Family">Single Family</option>
          <option value="Multi-Family">Multi-Family</option>
          <option value="Condo">Condo</option>
          <option value="Townhouse">Townhouse</option>
        </select>
      </div>
      <div className="search-actions">
        <button className="search-btn" onClick={handleSearch}>Search Properties</button>
        {/* <button className="advanced-btn">
          <span>&#9662;</span> Advanced Search
        </button> */}
      </div>
    </div>
  );
};

export default SearchBar;