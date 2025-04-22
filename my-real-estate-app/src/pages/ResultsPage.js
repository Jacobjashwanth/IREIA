import React, { useEffect, useState, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { GoogleMap, LoadScript, Marker, InfoWindow } from '@react-google-maps/api';
import ComparisonChart from '../components/ComparisonChart';
import OwnershipCostChart from '../components/OwnershipCostChart';
import RentalPriceChart from '../components/RentalPriceChart';
import '../styles/ResultsPage.css';

const ResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  const [mapCenter, setMapCenter] = useState({ lat: 42.3601, lng: -71.0589 });
  const [markers, setMarkers] = useState([]);
  const [selectedMarker, setSelectedMarker] = useState(null);
  const [areaInfo, setAreaInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [mapError, setMapError] = useState(null);
  const [isMapLoaded, setIsMapLoaded] = useState(false);

  // Get search parameters from location state
  const searchParams = location.state?.searchParams || {};
  console.log('Search params received in ResultsPage:', searchParams);
  const { zipcode, predictedRent, predictedSalePrice, bedrooms, propertyType } = searchParams;
  console.log('Destructured values:', { zipcode, predictedRent, predictedSalePrice, bedrooms, propertyType });

  const handleMapLoad = useCallback((map) => {
    console.log('Map loaded successfully');
    setIsMapLoaded(true);
  }, []);

  const handleMapError = useCallback((error) => {
    console.error('Map loading error:', error);
    setMapError('Error loading map. Please try again later.');
  }, []);

  // Validate required parameters (ensure props for charts are available)
  useEffect(() => {
    if (!zipcode || predictedRent === undefined || predictedSalePrice === undefined) {
      console.log('Missing required parameters for rendering:', { zipcode, predictedRent, predictedSalePrice });
      // Set error or handle loading state appropriately if needed
      // setError('Missing required parameters for display');
      return;
    }
    // Ensure prices are numbers, default to 0 if not (for chart safety)
    const rent = Number(predictedRent) || 0;
    const salePrice = Number(predictedSalePrice) || 0;
    // If you need to update state based on this, do it here, but likely props are passed directly

  }, [zipcode, predictedRent, predictedSalePrice]);

  useEffect(() => {
    const fetchAreaInfo = async () => {
      if (!zipcode) return;

      try {
        setIsLoading(true);
        // 1. Initial Geocode by Zipcode
        const initialResponse = await fetch(`https://maps.googleapis.com/maps/api/geocode/json?address=${zipcode}&key=AIzaSyAC2_CrKzi9aSnFXsQdwixcuEVzPmdNbnk`);
        if (!initialResponse.ok) {
          throw new Error('Failed to fetch initial location data for zipcode');
        }
        const initialData = await initialResponse.json();

        if (!initialData.results || !initialData.results[0]) {
          throw new Error('No location found for the provided zipcode');
        }

        const initialResult = initialData.results[0];
        const location = initialResult.geometry.location;
        const initialFormattedAddress = initialResult.formatted_address;
        const initialAddressComponents = initialResult.address_components;

        // Set map center early
        setMapCenter({ lat: location.lat, lng: location.lng });

        // 2. Reverse Geocode using Lat/Lng
        let bestAreaName = '';
        let finalFullAddress = initialFormattedAddress;

        try {
          const reverseResponse = await fetch(`https://maps.googleapis.com/maps/api/geocode/json?latlng=${location.lat},${location.lng}&key=AIzaSyAC2_CrKzi9aSnFXsQdwixcuEVzPmdNbnk`);
          if (reverseResponse.ok) {
            const reverseData = await reverseResponse.json();
            if (reverseData.results && reverseData.results[0]) {
              // Use the first result from reverse geocode for potential better address
              finalFullAddress = reverseData.results[0].formatted_address; 
              
              // Try to find neighborhood/sublocality from reverse geocode results
              for (const result of reverseData.results) {
                 const neighborhood = result.address_components.find(comp => comp.types.includes('neighborhood'))?.long_name;
                 if (neighborhood) {
                    bestAreaName = neighborhood;
                    break; // Found neighborhood, stop searching
                 }
                 if (!bestAreaName) { // Only look for sublocality if neighborhood wasn't found yet
                    const sublocality = result.address_components.find(comp => comp.types.includes('sublocality'))?.long_name;
                    if (sublocality) {
                        bestAreaName = sublocality; 
                        // Don't break here, keep checking other results for a potential neighborhood
                    }
                 }
              }
            }
          } else {
             console.warn("Reverse geocoding request failed, falling back to initial data.");
          }
        } catch (reverseError) {
           console.error('Error during reverse geocoding:', reverseError);
           // Fallback handled below
        }


        // 3. Determine Final Area Name (Fallback Logic)
        if (!bestAreaName) {
          // Fallback to neighborhood/sublocality from *initial* zipcode result if reverse geocode didn't yield anything better
          bestAreaName = initialAddressComponents.find(comp => comp.types.includes('neighborhood'))?.long_name ||
                         initialAddressComponents.find(comp => comp.types.includes('sublocality'))?.long_name ||
                         initialFormattedAddress.split(',')[0]; // Final fallback to city/area from original address
        }

        // 4. Update State
        setAreaInfo({
          name: bestAreaName,
          zipcode: zipcode,
          fullAddress: finalFullAddress // Use address from reverse geocode if available
        });

        // Create marker for the location
        setMarkers([{
          position: { lat: location.lat, lng: location.lng },
          title: bestAreaName, // Use the best name found
          predictedSalePrice: predictedSalePrice,
          predictedRent: predictedRent,
          bedrooms: bedrooms,
          propertyType: propertyType,
          address: finalFullAddress // Use the potentially better address
        }]);

      } catch (error) {
        console.error('Error fetching area information:', error);
        setError(error.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAreaInfo();
  }, [zipcode, predictedSalePrice, predictedRent, bedrooms, propertyType]); // Added predictedRent dependency as it's used in Marker

  if (error) {
    return (
      <div className="error-container">
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={() => navigate('/')} className="back-button">
          Return to Home
        </button>
      </div>
    );
  }

  const mapContainerStyle = {
    width: '100%',
    height: '400px'
  };

  const mapOptions = {
    zoom: 15,
    mapTypeControl: true,
    streetViewControl: true,
    fullscreenControl: true,
    styles: [
      {
        featureType: 'poi',
        elementType: 'labels',
        stylers: [{ visibility: 'off' }]
      }
    ]
  };

  return (
    <div className="results-page">
      <div className="results-header">
        <button onClick={() => navigate('/')} className="back-button">
          Back to Search
        </button>
      </div>

      <div className="results-main-content">
        <div className="results-details-column">
          <h1>Property Predictions</h1>
          <h2>Area: {areaInfo?.name || zipcode}</h2>
          <div className="prediction-cards">
            <div className="prediction-card sale-card">
              <h3>Predicted Sale Price</h3>
              <p className="prediction-value">${predictedSalePrice?.toLocaleString()}</p>
              <div className="property-details">
                <p><strong>Bedrooms:</strong> {bedrooms}</p>
                <p><strong>Property Type:</strong> {propertyType}</p>
                <p><strong>Zipcode:</strong> {zipcode}</p>
                <p><strong>Address:</strong> {areaInfo?.fullAddress || `${zipcode}, USA`}</p>
              </div>
            </div>
            <div className="prediction-card rent-card">
              <h3>Predicted Monthly Rent</h3>
              <p className="prediction-value">${predictedRent?.toLocaleString()}</p>
              <div className="property-details">
                <p><strong>Bedrooms:</strong> {bedrooms}</p>
                <p><strong>Property Type:</strong> {propertyType}</p>
                <p><strong>Zipcode:</strong> {zipcode}</p>
                <p><strong>Address:</strong> {areaInfo?.fullAddress || `${zipcode}, USA`}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="results-map-column">
          <div className="map-wrapper">
            <LoadScript 
              googleMapsApiKey="AIzaSyAC2_CrKzi9aSnFXsQdwixcuEVzPmdNbnk"
              onLoad={handleMapLoad}
              onError={handleMapError}
            >
              <GoogleMap
                mapContainerStyle={{ width: '100%', height: '450px' }}
                center={mapCenter}
                zoom={mapOptions.zoom}
                options={mapOptions}
                onLoad={handleMapLoad}
                onError={handleMapError}
              >
                {markers.map((marker, index) => (
                  <Marker
                    key={index}
                    position={marker.position}
                    onClick={() => setSelectedMarker(marker)}
                    icon={{
                      url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`
                        <svg xmlns="http://www.w3.org/2000/svg" width="100" height="36">
                          <rect width="100" height="36" rx="8" ry="8" fill="#e74c3c" />
                          <text x="50" y="24" font-size="14" font-family="Arial" fill="white" font-weight="bold" text-anchor="middle">
                            Rent: $${marker.predictedRent?.toLocaleString()}
                          </text>
                        </svg>
                      `)}`,
                      scaledSize: new window.google.maps.Size(100, 36),
                      anchor: new window.google.maps.Point(50, 18)
                    }}
                  />
                ))}

                {selectedMarker && (
                  <InfoWindow
                    position={selectedMarker.position}
                    onCloseClick={() => setSelectedMarker(null)}
                  >
                    <div className="info-window">
                      <h3>{selectedMarker.title}</h3>
                      <p><strong>Address:</strong> {selectedMarker.address}</p>
                      <p><strong>Predicted Sale:</strong> ${selectedMarker.predictedSalePrice?.toLocaleString()}</p>
                      <p><strong>Predicted Rent:</strong> ${selectedMarker.predictedRent?.toLocaleString()}</p>
                      <p><strong>Bedrooms:</strong> {selectedMarker.bedrooms}</p>
                      <p><strong>Property Type:</strong> {selectedMarker.propertyType}</p>
                    </div>
                  </InfoWindow>
                )}
              </GoogleMap>
            </LoadScript>
          </div>

          {/* Charts - Moved inside the map column */}
          {/* Add a title for the chart section */}
          {!isLoading && Number(predictedRent) > 0 && Number(predictedSalePrice) > 0 && (
            <>
              <h2 className="charts-title">Additional Insights</h2>
              <div className="multi-chart-container">
                <ComparisonChart 
                  predictedRent={Number(predictedRent)}
                  predictedSalePrice={Number(predictedSalePrice)}
                />
                <OwnershipCostChart 
                  predictedSalePrice={Number(predictedSalePrice)} 
                />
                <RentalPriceChart 
                  predictedRent={Number(predictedRent)} 
                />
              </div>
            </>
          )}
        </div>
      </div>

    </div>
  );
};

export default ResultsPage; 