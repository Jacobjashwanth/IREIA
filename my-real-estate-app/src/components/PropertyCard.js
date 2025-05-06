import React from "react";
import { FaBath, FaBed, FaMapMarkerAlt, FaRulerCombined } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import "../styles/PropertyCard.css";

// 🔧 High-resolution image transformer
const getHighResImage = (url) => {
  return url
    ?.replace(/-m(\d+)s\.jpg/, '-m$1x.jpg')
    ?.replace(/-t\.jpg/, '-o.jpg')
    ?.replace(/s\.jpg$/, 'od.jpg')
    ?.replace(/-m(\d+)\.jpg/, '-m$1x.jpg')
    ?.replace(/-l\.jpg/, '-o.jpg')
    ?.replace(/-p\.jpg/, '-o.jpg');
};

function PropertyCard({ property }) {
  const navigate = useNavigate();

  const isOverpriced = property?.recommendation?.toLowerCase().includes("overpriced");

  const handleClick = () => {
    const propertyWithImages = {
      ...property,
      images: property.photos?.map(photo => photo.href) || [property.image_url]
    };
    localStorage.setItem("selected_property", JSON.stringify(propertyWithImages));
    navigate("/property");
  };

  return (
    <div className="property-card" onClick={handleClick}>
      <img
        src={getHighResImage(property.image_url) || '/fallback.png'}
        alt={property.address}
        className="property-img"
        onError={(e) => { e.target.src = '/fallback.png'; }}
      />

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
          <span className={`predicted ${isOverpriced ? "red" : "green"}`}>
            ${property.predicted_price?.toLocaleString()}
          </span>
        </div>

        <div className="price-row">
          <span className="label">Monthly Rent:</span>
          <span className="value">${property.rent_price?.toLocaleString()}</span>
        </div>

        <div className="price-row">
          <span className="label">Predicted Rent:</span>
          <span className={`predicted ${isOverpriced ? "red" : "green"}`}>
            ${property.predicted_rent?.toLocaleString()}
          </span>
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