import React from "react";
import { FaBath, FaBed, FaMapMarkerAlt, FaRulerCombined } from "react-icons/fa";
import "../styles/PropertyCard.css";
import { useNavigate } from "react-router-dom";

function PropertyCard({ property }) {
  const navigate = useNavigate();

  const isOverpriced = property?.recommendation?.toLowerCase().includes("overpriced");

  const handleClick = () => {
    // Save the selected property in localStorage
    // Add multiple images to the property object before saving
    const propertyWithImages = {
      ...property,
      images: property.photos?.map(photo => photo.href) || [property.image_url]
    };
    localStorage.setItem("selected_property", JSON.stringify(propertyWithImages)); // ✅ use the new one
    localStorage.setItem("selected_property", JSON.stringify(property));
    // Navigate to the individual property page
    navigate("/property");
  };

  return (
    <div className="property-card" onClick={handleClick}>
      <img src={property.image_url} alt={property.address} className="property-img" />
      <div className="property-content">
        <h3 className="property-title">{property.address}</h3>
        <div className="property-location">
          <FaMapMarkerAlt className="icon" />
          <span>{property.city}, {property.state}</span>
        </div>
        <div className="property-meta">
          <span><FaRulerCombined className="icon" /> {property.sqft || "N/A"} sqft.</span>
          <span><FaBed className="icon" /> {property.beds || "N/A"} Bed</span>
          <span><FaBath className="icon" /> {property.baths || "N/A"} Bath</span>
        </div>
        <div className="price-row">
          <span className="label">List Price:</span>
          <span className="value">${property.current_price?.toLocaleString()}</span>
        </div>
        <div className="price-row">
          <span className="label">Predicted Price:</span>
          <span className="predicted">${property.predicted_price?.toLocaleString()}</span>
        </div>
        <div className="property-footer">
          <span className={`recommend-badge ${isOverpriced ? "red" : "green"}`}>
            {property.recommendation}
          </span>
          <button className="invest-button">Invest now</button>
        </div>
      </div>
    </div>
  );
}

export default PropertyCard;