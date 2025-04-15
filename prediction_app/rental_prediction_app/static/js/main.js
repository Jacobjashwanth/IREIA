
// // Global variables
// let map;
// let markers = [];
// let currentInfoWindow = null;

// // Chart data for rental trends
// const monthlyRentData = {
//     labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
//     datasets: [
//         {
//             label: 'Boston',
//             data: [2780, 2795, 2810, 2850, 2890, 2950, 3000, 3050, 3020, 2980, 2950, 2910],
//             borderColor: '#3498db',
//             backgroundColor: 'rgba(52, 152, 219, 0.1)',
//             borderWidth: 3,
//             tension: 0.4
//         },
//         {
//             label: 'Cambridge',
//             data: [2900, 2930, 2960, 3010, 3040, 3100, 3150, 3190, 3170, 3140, 3100, 3050],
//             borderColor: '#2ecc71',
//             backgroundColor: 'rgba(46, 204, 113, 0.1)',
//             borderWidth: 3,
//             tension: 0.4
//         },
//         {
//             label: 'Somerville',
//             data: [2600, 2620, 2650, 2680, 2720, 2760, 2800, 2840, 2820, 2790, 2750, 2720],
//             borderColor: '#e74c3c',
//             backgroundColor: 'rgba(231, 76, 60, 0.1)',
//             borderWidth: 3,
//             tension: 0.4
//         }
//     ]
// };

// // Initialize Google Map
// function initMap() {
//     // Create the map centered on Boston
//     map = new google.maps.Map(document.getElementById('map'), {
//         center: { lat: 42.3601, lng: -71.0589 },
//         zoom: 11,
//         styles: [
//             {
//                 "featureType": "administrative",
//                 "elementType": "labels.text.fill",
//                 "stylers": [{ "color": "#444444" }]
//             },
//             {
//                 "featureType": "landscape",
//                 "elementType": "all",
//                 "stylers": [{ "color": "#f2f2f2" }]
//             },
//             {
//                 "featureType": "poi",
//                 "elementType": "all",
//                 "stylers": [{ "visibility": "off" }]
//             },
//             {
//                 "featureType": "road",
//                 "elementType": "all",
//                 "stylers": [{ "saturation": -100 }, { "lightness": 45 }]
//             },
//             {
//                 "featureType": "road.highway",
//                 "elementType": "all",
//                 "stylers": [{ "visibility": "simplified" }]
//             },
//             {
//                 "featureType": "road.arterial",
//                 "elementType": "labels.icon",
//                 "stylers": [{ "visibility": "off" }]
//             },
//             {
//                 "featureType": "transit",
//                 "elementType": "all",
//                 "stylers": [{ "visibility": "off" }]
//             },
//             {
//                 "featureType": "water",
//                 "elementType": "all",
//                 "stylers": [{ "color": "#c4e5f9" }, { "visibility": "on" }]
//             }
//         ]
//     });
    
//     // Load initial rental listings
//     fetchRentalListings(42.3601, -71.0589);
    
//     // Set up click listener to get coordinates
//     map.addListener('click', function(event) {
//         document.getElementById('latitude').value = event.latLng.lat();
//         document.getElementById('longitude').value = event.latLng.lng();
        
//         // Reverse geocode to get address
//         const geocoder = new google.maps.Geocoder();
//         geocoder.geocode({ location: event.latLng }, function(results, status) {
//             if (status === 'OK' && results[0]) {
//                 document.getElementById('address').value = results[0].formatted_address;
//             }
//         });
//     });
    
//     // Set up geolocation if allowed
//     document.getElementById('use-location').addEventListener('change', function() {
//         if (this.checked) {
//             if (navigator.geolocation) {
//                 navigator.geolocation.getCurrentPosition(function(position) {
//                     const userLocation = {
//                         lat: position.coords.latitude,
//                         lng: position.coords.longitude
//                     };
                    
//                     // Set form values
//                     document.getElementById('latitude').value = userLocation.lat;
//                     document.getElementById('longitude').value = userLocation.lng;
                    
//                     // Center map on user location
//                     map.setCenter(userLocation);
//                     map.setZoom(15);
                    
//                     // Load rentals near this location
//                     fetchRentalListings(userLocation.lat, userLocation.lng);
                    
//                     // Add marker for user location
//                     new google.maps.Marker({
//                         position: userLocation,
//                         map: map,
//                         title: 'Your Location',
//                         icon: {
//                             path: google.maps.SymbolPath.CIRCLE,
//                             scale: 10,
//                             fillColor: '#4285F4',
//                             fillOpacity: 0.8,
//                             strokeColor: 'white',
//                             strokeWeight: 2
//                         }
//                     });
                    
//                     // Reverse geocode to get address
//                     const geocoder = new google.maps.Geocoder();
//                     geocoder.geocode({ location: userLocation }, function(results, status) {
//                         if (status === 'OK' && results[0]) {
//                             document.getElementById('address').value = results[0].formatted_address;
//                         }
//                     });
//                 });
//             }
//         }
//     });
    
//     // Set up address search
//     const addressInput = document.getElementById('address');
//     const searchResults = document.getElementById('search-results');
    
//     addressInput.addEventListener('input', function() {
//         if (this.value.length > 3) {
//             // Use Google Places Autocomplete service
//             const autocompleteService = new google.maps.places.AutocompleteService();
//             autocompleteService.getPlacePredictions({
//                 input: this.value,
//                 componentRestrictions: { country: 'us' },
//                 region: 'us'
//             }, function(predictions, status) {
//                 if (status === google.maps.places.PlacesServiceStatus.OK) {
//                     // Display results
//                     searchResults.innerHTML = '';
//                     searchResults.style.display = 'block';
                    
//                     predictions.forEach(function(prediction) {
//                         const resultItem = document.createElement('div');
//                         resultItem.className = 'search-result-item';
//                         resultItem.textContent = prediction.description;
//                         resultItem.addEventListener('click', function() {
//                             addressInput.value = prediction.description;
//                             searchResults.style.display = 'none';
                            
//                             // Geocode to get coordinates
//                             const geocoder = new google.maps.Geocoder();
//                             geocoder.geocode({ address: prediction.description }, function(results, status) {
//                                 if (status === 'OK' && results[0]) {
//                                     const location = results[0].geometry.location;
//                                     document.getElementById('latitude').value = location.lat();
//                                     document.getElementById('longitude').value = location.lng();
                                    
//                                     // Center map on selected location
//                                     map.setCenter(location);
//                                     map.setZoom(15);
                                    
//                                     // Load rentals near this location
//                                     fetchRentalListings(location.lat(), location.lng());
//                                 }
//                             });
//                         });
                        
//                         searchResults.appendChild(resultItem);
//                     });
//                 } else {
//                     searchResults.style.display = 'none';
//                 }
//             });
//         } else {
//             searchResults.style.display = 'none';
//         }
//     });
    
//     // Hide search results when clicking outside
//     document.addEventListener('click', function(event) {
//         if (!addressInput.contains(event.target) && !searchResults.contains(event.target)) {
//             searchResults.style.display = 'none';
//         }
//     });
// }

// // Fetch rental listings from the backend API
// function fetchRentalListings(latitude, longitude, radius = 10) {
//     fetch(`/api/rentals?latitude=${latitude}&longitude=${longitude}&radius=${radius}`)
//         .then(response => response.json())
//         .then(data => {
//             if (data.status === 'success') {
//                 addRentalMarkers(data.listings);
//                 fetchMarketStats(latitude, longitude);
//             } else {
//                 console.error('Error fetching rental listings:', data.error);
//             }
//         })
//         .catch(error => {
//             console.error('Error fetching rental listings:', error);
//         });
// }

// // Fetch market statistics for the area
// function fetchMarketStats(latitude, longitude) {
//     // Determine the closest city for stats
//     let city = 'Boston';  // Default
    
//     // Quick distance check for demo purposes
//     // In a production app, you would do a proper reverse geocode
//     const cambridgeLat = 42.3736;
//     const cambridgeLng = -71.1097;
//     const somervilleLat = 42.3876;
//     const somervilleLng = -71.0995;
    
//     const distToCambridge = Math.sqrt(
//         Math.pow(latitude - cambridgeLat, 2) + 
//         Math.pow(longitude - cambridgeLng, 2)
//     );
    
//     const distToSomerville = Math.sqrt(
//         Math.pow(latitude - somervilleLat, 2) + 
//         Math.pow(longitude - somervilleLng, 2)
//     );
    
//     if (distToCambridge < 0.02) {
//         city = 'Cambridge';
//     } else if (distToSomerville < 0.02) {
//         city = 'Somerville';
//     }
    
//     fetch(`/api/market-stats?city=${city}`)
//         .then(response => response.json())
//         .then(data => {
//             if (data.status === 'success') {
//                 updateMarketStats(data.stats);
//             } else {
//                 console.error('Error fetching market stats:', data.error);
//             }
//         })
//         .catch(error => {
//             console.error('Error fetching market stats:', error);
//         });
// }

// // Update the market statistics display
// function updateMarketStats(stats) {
//     document.getElementById('avg-rent').textContent = `$${stats.averageRent.toLocaleString()}`;
//     document.getElementById('price-per-sqft').textContent = `$${stats.pricePerSqFt.toFixed(2)}`;
//     document.getElementById('rent-yoy').textContent = `+${stats.rentYoYChange}%`;
//     document.getElementById('vacancy-rate').textContent = `${stats.vacancyRate}%`;
// }

// // Add markers for rental properties
// function addRentalMarkers(properties) {
//     // Clear existing markers
//     markers.forEach(marker => marker.setMap(null));
//     markers = [];
    
//     // Create new markers
//     properties.forEach(property => {
//         const position = { 
//             lat: property.latitude, 
//             lng: property.longitude 
//         };
        
//         // Skip if missing lat/lng
//         if (!position.lat || !position.lng) {
//             return;
//         }
        
//         // Determine marker color based on property type
//         let markerColor;
//         switch(property.propertyType) {
//             case 'CONDO':
//                 markerColor = '#3498db'; // Blue
//                 break;
//             case 'SINGLE_FAMILY':
//                 markerColor = '#2ecc71'; // Green
//                 break;
//             case 'MULTI_FAMILY':
//                 markerColor = '#e74c3c'; // Red
//                 break;
//             case 'TOWNHOUSE':
//                 markerColor = '#f39c12'; // Orange
//                 break;
//             default:
//                 markerColor = '#9b59b6'; // Purple
//         }
        
//         // Create marker
//         const marker = new google.maps.Marker({
//             position: position,
//             map: map,
//             title: property.address,
//             icon: {
//                 path: 'M12,2C8.13,2,5,5.13,5,9c0,5.25,7,13,7,13s7-7.75,7-13C19,5.13,15.87,2,12,2z M12,11.5c-1.38,0-2.5-1.12-2.5-2.5s1.12-2.5,2.5-2.5s2.5,1.12,2.5,2.5S13.38,11.5,12,11.5z',
//                 fillColor: markerColor,
//                 fillOpacity: 0.9,
//                 strokeWeight: 1,
//                 strokeColor: '#FFFFFF',
//                 scale: 1.5,
//                 anchor: new google.maps.Point(12, 22)
//             }
//         });
        
//         // Get display price
//         let displayPrice = property.price;
//         if (!displayPrice && property.rentZestimate) {
//             displayPrice = property.rentZestimate;
//         }
        
//         // Format address
//         const address = property.address || 'Address not available';
        
//         // Create info window content
//         const contentString = `
//             <div class="marker-popup">
//                 <h3>${address}</h3>
//                 <p class="price">$${displayPrice ? displayPrice.toLocaleString() : 'N/A'}/month</p>
//                 <p><strong>${property.bedrooms || 'N/A'}</strong> beds, <strong>${property.bathrooms || 'N/A'}</strong> baths</p>
//                 <p><strong>${property.livingArea ? property.livingArea.toLocaleString() : 'N/A'}</strong> sq ft</p>
//                 <p>Property Type: ${property.propertyType ? property.propertyType.replace(/_/g, ' ').toLowerCase() : 'Unknown'}</p>
//                 ${property.imgSrc ? `<img src="${property.imgSrc}" alt="${address}" style="width: 100%; max-height: 150px; object-fit: cover; margin-top: 10px; border-radius: 4px;">` : ''}
//             </div>
//         `;
        
//         const infoWindow = new google.maps.InfoWindow({
//             content: contentString,
//             maxWidth: 300
//         });
        
//         // Add click listener to show info window
//         marker.addListener('click', () => {
//             // Close the currently open info window
//             if (currentInfoWindow) {
//                 currentInfoWindow.close();
//             }
            
//             // Open the new info window
//             infoWindow.open(map, marker);
//             currentInfoWindow = infoWindow;
//         });
        
//         markers.push(marker);
//     });
// }

// // Initialize charts
// function initCharts() {
//     const ctx = document.getElementById('rental-chart').getContext('2d');
//     new Chart(ctx, {
//         type: 'line',
//         data: monthlyRentData,
//         options: {
//             responsive: true,
//             maintainAspectRatio: false,
//             plugins: {
//                 title: {
//                     display: true,
//                     text: 'Monthly Rental Trends (2024-2025)',
//                     font: {
//                         size: 16
//                     }
//                 },
//                 legend: {
//                     position: 'top'
//                 },
//                 tooltip: {
//                     mode: 'index',
//                     intersect: false
//                 }
//             },
//             scales: {
//                 y: {
//                     beginAtZero: false,
//                     title: {
//                         display: true,
//                         text: 'Average Rent ($)'
//                     }
//                 },
//                 x: {
//                     title: {
//                         display: true,
//                         text: 'Month'
//                     }
//                 }
//             }
//         }
//     });
// }

// // Make a rental price prediction API call
// function makePrediction(propertyData) {
//     // Show loading indicator
//     document.querySelector('.loading').style.display = 'block';
//     document.querySelector('.results').style.display = 'none';
    
//     // Make API call to backend
//     fetch('/api/predict', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(propertyData)
//     })
//     .then(response => response.json())
//     .then(data => {
//         // Hide loading indicator
//         document.querySelector('.loading').style.display = 'none';
        
//         if (data.error) {
//             alert(`Error: ${data.error}`);
//             return;
//         }
        
//         // Show the result
//         document.querySelector('.results').style.display = 'block';
//         document.getElementById('predicted-price').textContent = data.predictedRent.toLocaleString();
        
//         // Highlight the prediction result with animation
//         const predictionElement = document.getElementById('predicted-price').parentElement;
//         predictionElement.style.transform = 'scale(1.05)';
//         setTimeout(() => {
//             predictionElement.style.transition = 'transform 0.5s ease';
//             predictionElement.style.transform = 'scale(1)';
//         }, 50);
        
//         // Add a marker for the prediction
//         const markerPosition = {
//             lat: propertyData.latitude,
//             lng: propertyData.longitude
//         };
        
//         // Center map on the prediction location
//         map.setCenter(markerPosition);
//         map.setZoom(15);
        
//         // Remove previous prediction marker if exists
//         markers.forEach(marker => {
//             if (marker.title === 'Your Prediction') {
//                 marker.setMap(null);
//             }
//         });
        
//         // Add new prediction marker
//         const marker = new google.maps.Marker({
//             position: markerPosition,
//             map: map,
//             title: 'Your Prediction',
//             animation: google.maps.Animation.DROP,
//             icon: {
//                 path: google.maps.SymbolPath.CIRCLE,
//                 scale: 14,
//                 fillColor: '#e74c3c',
//                 fillOpacity: 0.8,
//                 strokeColor: 'white',
//                 strokeWeight: 2
//             }
//         });
        
//         // Create info window content
//         const contentString = `
//             <div class="marker-popup">
//                 <h3>Your Rental Prediction</h3>
//                 <p class="price">$${data.predictedRent.toLocaleString()}/month</p>
//                 <p><strong>${propertyData.bedrooms}</strong> beds, <strong>${propertyData.bathrooms}</strong> baths</p>
//                 <p><strong>${propertyData.livingArea}</strong> sq ft</p>
//                 <p>Property Type: ${propertyData.propertyType.replace(/_/g, ' ').toLowerCase()}</p>
//             </div>
//         `;
        
//         const infoWindow = new google.maps.InfoWindow({
//             content: contentString
//         });
        
//         // Add click listener to show info window
//         marker.addListener('click', () => {
//             if (currentInfoWindow) {
//                 currentInfoWindow.close();
//             }
//             infoWindow.open(map, marker);
//             currentInfoWindow = infoWindow;
//         });
        
//         // Open info window initially
//         infoWindow.open(map, marker);
//         currentInfoWindow = infoWindow;
        
//         markers.push(marker);
//     })
//     .catch(error => {
//         console.error('Error:', error);
//         document.querySelector('.loading').style.display = 'none';
//         alert('An error occurred while making the prediction. Please try again.');
//     });
// }

// // Handle form submission
// document.getElementById('prediction-form').addEventListener('submit', function(event) {
//     event.preventDefault();
    
//     // Get form values
//     const propertyData = {
//         latitude: parseFloat(document.getElementById('latitude').value),
//         longitude: parseFloat(document.getElementById('longitude').value),
//         propertyType: document.getElementById('property-type').value,
//         bedrooms: parseInt(document.getElementById('bedrooms').value),
//         bathrooms: parseFloat(document.getElementById('bathrooms').value),
//         livingArea: parseInt(document.getElementById('living-area').value),
//         lotArea: parseFloat(document.getElementById('lot-area').value) || 0.25
//     };
    
//     // Make prediction
//     makePrediction(propertyData);
// });

// // Initialize charts when page loads
// document.addEventListener('DOMContentLoaded', function() {
//     initCharts();
// });

// Global variables
let map;
let markers = [];
let currentInfoWindow = null;

// Chart data for rental trends
const monthlyRentData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
        {
            label: 'Boston',
            data: [2780, 2795, 2810, 2850, 2890, 2950, 3000, 3050, 3020, 2980, 2950, 2910],
            borderColor: '#3498db',
            backgroundColor: 'rgba(52, 152, 219, 0.1)',
            borderWidth: 3,
            tension: 0.4
        },
        {
            label: 'Cambridge',
            data: [2900, 2930, 2960, 3010, 3040, 3100, 3150, 3190, 3170, 3140, 3100, 3050],
            borderColor: '#2ecc71',
            backgroundColor: 'rgba(46, 204, 113, 0.1)',
            borderWidth: 3,
            tension: 0.4
        },
        {
            label: 'Somerville',
            data: [2600, 2620, 2650, 2680, 2720, 2760, 2800, 2840, 2820, 2790, 2750, 2720],
            borderColor: '#e74c3c',
            backgroundColor: 'rgba(231, 76, 60, 0.1)',
            borderWidth: 3,
            tension: 0.4
        }
    ]
};

// Initialize Google Map
function initMap() {
    // Create the map centered on Boston
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 42.3601, lng: -71.0589 },
        zoom: 11,
        styles: [
            {
                "featureType": "administrative",
                "elementType": "labels.text.fill",
                "stylers": [{ "color": "#444444" }]
            },
            {
                "featureType": "landscape",
                "elementType": "all",
                "stylers": [{ "color": "#f2f2f2" }]
            },
            {
                "featureType": "poi",
                "elementType": "all",
                "stylers": [{ "visibility": "off" }]
            },
            {
                "featureType": "road",
                "elementType": "all",
                "stylers": [{ "saturation": -100 }, { "lightness": 45 }]
            },
            {
                "featureType": "road.highway",
                "elementType": "all",
                "stylers": [{ "visibility": "simplified" }]
            },
            {
                "featureType": "road.arterial",
                "elementType": "labels.icon",
                "stylers": [{ "visibility": "off" }]
            },
            {
                "featureType": "transit",
                "elementType": "all",
                "stylers": [{ "visibility": "off" }]
            },
            {
                "featureType": "water",
                "elementType": "all",
                "stylers": [{ "color": "#c4e5f9" }, { "visibility": "on" }]
            }
        ]
    });
    
    // Load initial rental listings
    fetchRentalListings(42.3601, -71.0589);
    
    // Set up click listener to get coordinates
    map.addListener('click', function(event) {
        document.getElementById('latitude').value = event.latLng.lat();
        document.getElementById('longitude').value = event.latLng.lng();
        
        // Reverse geocode to get address and zipcode
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ location: event.latLng }, function(results, status) {
            if (status === 'OK' && results[0]) {
                document.getElementById('address').value = results[0].formatted_address;
                
                // Extract zipcode from address components
                const addressComponents = results[0].address_components;
                for (let component of addressComponents) {
                    if (component.types.includes('postal_code')) {
                        document.getElementById('zipcode').value = component.short_name;
                        break;
                    }
                }
            }
        });
    });
    
    // Set up geolocation if allowed
    document.getElementById('use-location').addEventListener('change', function() {
        if (this.checked) {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    const userLocation = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };
                    
                    // Set form values
                    document.getElementById('latitude').value = userLocation.lat;
                    document.getElementById('longitude').value = userLocation.lng;
                    
                    // Center map on user location
                    map.setCenter(userLocation);
                    map.setZoom(15);
                    
                    // Load rentals near this location
                    fetchRentalListings(userLocation.lat, userLocation.lng);
                    
                    // Add marker for user location
                    new google.maps.Marker({
                        position: userLocation,
                        map: map,
                        title: 'Your Location',
                        icon: {
                            path: google.maps.SymbolPath.CIRCLE,
                            scale: 10,
                            fillColor: '#4285F4',
                            fillOpacity: 0.8,
                            strokeColor: 'white',
                            strokeWeight: 2
                        }
                    });
                    
                    // Reverse geocode to get address and zipcode
                    const geocoder = new google.maps.Geocoder();
                    geocoder.geocode({ location: userLocation }, function(results, status) {
                        if (status === 'OK' && results[0]) {
                            document.getElementById('address').value = results[0].formatted_address;
                            
                            // Extract zipcode from address components
                            const addressComponents = results[0].address_components;
                            for (let component of addressComponents) {
                                if (component.types.includes('postal_code')) {
                                    document.getElementById('zipcode').value = component.short_name;
                                    break;
                                }
                            }
                        }
                    });
                });
            }
        }
    });
    
    // Set up address search
    const addressInput = document.getElementById('address');
    const searchResults = document.getElementById('search-results');
    
    addressInput.addEventListener('input', function() {
        if (this.value.length > 3) {
            // Use Google Places Autocomplete service
            const autocompleteService = new google.maps.places.AutocompleteService();
            autocompleteService.getPlacePredictions({
                input: this.value,
                componentRestrictions: { country: 'us' },
                region: 'us'
            }, function(predictions, status) {
                if (status === google.maps.places.PlacesServiceStatus.OK) {
                    // Display results
                    searchResults.innerHTML = '';
                    searchResults.style.display = 'block';
                    
                    predictions.forEach(function(prediction) {
                        const resultItem = document.createElement('div');
                        resultItem.className = 'search-result-item';
                        resultItem.textContent = prediction.description;
                        resultItem.addEventListener('click', function() {
                            // Update address field and handle zipcode, coordinates
                            handleAddressSelection(prediction.description);
                        });
                        
                        searchResults.appendChild(resultItem);
                    });
                } else {
                    searchResults.style.display = 'none';
                }
            });
        } else {
            searchResults.style.display = 'none';
        }
    });
    
    // Hide search results when clicking outside
    document.addEventListener('click', function(event) {
        if (!addressInput.contains(event.target) && !searchResults.contains(event.target)) {
            searchResults.style.display = 'none';
        }
    });
}

// Handle address selection from autocomplete
function handleAddressSelection(address) {
    document.getElementById('address').value = address;
    document.getElementById('search-results').style.display = 'none';
    
    // Geocode to get coordinates and zipcode
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ address: address }, function(results, status) {
        if (status === 'OK' && results[0]) {
            const location = results[0].geometry.location;
            document.getElementById('latitude').value = location.lat();
            document.getElementById('longitude').value = location.lng();
            
            // Extract zipcode from address components
            const addressComponents = results[0].address_components;
            for (let component of addressComponents) {
                if (component.types.includes('postal_code')) {
                    document.getElementById('zipcode').value = component.short_name;
                    break;
                }
            }
            
            // Center map on selected location
            map.setCenter(location);
            map.setZoom(15);
            
            // Load rentals near this location
            fetchRentalListings(location.lat(), location.lng());
        }
    });
}

// Fetch rental listings from the backend API
function fetchRentalListings(latitude, longitude, radius = 10) {
    fetch(`/api/rentals?latitude=${latitude}&longitude=${longitude}&radius=${radius}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                addRentalMarkers(data.listings);
                fetchMarketStats(latitude, longitude);
            } else {
                console.error('Error fetching rental listings:', data.error);
            }
        })
        .catch(error => {
            console.error('Error fetching rental listings:', error);
        });
}

// Fetch market statistics for the area
function fetchMarketStats(latitude, longitude) {
    // Determine the closest city for stats
    let city = 'Boston';  // Default
    
    // Quick distance check for demo purposes
    // In a production app, you would do a proper reverse geocode
    const cambridgeLat = 42.3736;
    const cambridgeLng = -71.1097;
    const somervilleLat = 42.3876;
    const somervilleLng = -71.0995;
    
    const distToCambridge = Math.sqrt(
        Math.pow(latitude - cambridgeLat, 2) + 
        Math.pow(longitude - cambridgeLng, 2)
    );
    
    const distToSomerville = Math.sqrt(
        Math.pow(latitude - somervilleLat, 2) + 
        Math.pow(longitude - somervilleLng, 2)
    );
    
    if (distToCambridge < 0.02) {
        city = 'Cambridge';
    } else if (distToSomerville < 0.02) {
        city = 'Somerville';
    }
    
    fetch(`/api/market-stats?city=${city}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateMarketStats(data.stats);
            } else {
                console.error('Error fetching market stats:', data.error);
            }
        })
        .catch(error => {
            console.error('Error fetching market stats:', error);
        });
}

// Update the market statistics display
function updateMarketStats(stats) {
    document.getElementById('avg-rent').textContent = `$${stats.averageRent.toLocaleString()}`;
    document.getElementById('price-per-sqft').textContent = `$${stats.pricePerSqFt.toFixed(2)}`;
    document.getElementById('rent-yoy').textContent = `+${stats.rentYoYChange}%`;
    document.getElementById('vacancy-rate').textContent = `${stats.vacancyRate}%`;
}

// Add markers for rental properties
function addRentalMarkers(properties) {
    // Clear existing markers
    markers.forEach(marker => marker.setMap(null));
    markers = [];
    
    // Create new markers
    properties.forEach(property => {
        const position = { 
            lat: property.latitude, 
            lng: property.longitude 
        };
        
        // Skip if missing lat/lng
        if (!position.lat || !position.lng) {
            return;
        }
        
        // Determine marker color based on property type
        let markerColor;
        switch(property.propertyType) {
            case 'CONDO':
                markerColor = '#3498db'; // Blue
                break;
            case 'SINGLE_FAMILY':
                markerColor = '#2ecc71'; // Green
                break;
            case 'MULTI_FAMILY':
                markerColor = '#e74c3c'; // Red
                break;
            case 'TOWNHOUSE':
                markerColor = '#f39c12'; // Orange
                break;
            default:
                markerColor = '#9b59b6'; // Purple
        }
        
        // Create marker
        const marker = new google.maps.Marker({
            position: position,
            map: map,
            title: property.address,
            icon: {
                path: 'M12,2C8.13,2,5,5.13,5,9c0,5.25,7,13,7,13s7-7.75,7-13C19,5.13,15.87,2,12,2z M12,11.5c-1.38,0-2.5-1.12-2.5-2.5s1.12-2.5,2.5-2.5s2.5,1.12,2.5,2.5S13.38,11.5,12,11.5z',
                fillColor: markerColor,
                fillOpacity: 0.9,
                strokeWeight: 1,
                strokeColor: '#FFFFFF',
                scale: 1.5,
                anchor: new google.maps.Point(12, 22)
            }
        });
        
        // Get display price
        let displayPrice = property.price;
        if (!displayPrice && property.rentZestimate) {
            displayPrice = property.rentZestimate;
        }
        
        // Format address
        const address = property.address || 'Address not available';
        
        // Create info window content
        const contentString = `
            <div class="marker-popup">
                <h3>${address}</h3>
                <p class="price">$${displayPrice ? displayPrice.toLocaleString() : 'N/A'}/month</p>
                <p><strong>${property.bedrooms || 'N/A'}</strong> beds, <strong>${property.bathrooms || 'N/A'}</strong> baths</p>
                <p><strong>${property.livingArea ? property.livingArea.toLocaleString() : 'N/A'}</strong> sq ft</p>
                <p>Property Type: ${property.propertyType ? property.propertyType.replace(/_/g, ' ').toLowerCase() : 'Unknown'}</p>
                ${property.imgSrc ? `<img src="${property.imgSrc}" alt="${address}" style="width: 100%; max-height: 150px; object-fit: cover; margin-top: 10px; border-radius: 4px;">` : ''}
            </div>
        `;
        
        const infoWindow = new google.maps.InfoWindow({
            content: contentString,
            maxWidth: 300
        });
        
        // Add click listener to show info window
        marker.addListener('click', () => {
            // Close the currently open info window
            if (currentInfoWindow) {
                currentInfoWindow.close();
            }
            
            // Open the new info window
            infoWindow.open(map, marker);
            currentInfoWindow = infoWindow;
        });
        
        markers.push(marker);
    });
}

// Initialize charts
function initCharts() {
    const ctx = document.getElementById('rental-chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: monthlyRentData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Monthly Rental Trends (2024-2025)',
                    font: {
                        size: 16
                    }
                },
                legend: {
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Average Rent ($)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Month'
                    }
                }
            }
        }
    });
}

// Make a rental price prediction API call
function makePrediction(propertyData) {
    // Show loading indicator
    document.querySelector('.loading').style.display = 'block';
    document.querySelector('.results').style.display = 'none';
    
    // Make API call to backend
    fetch('/api/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(propertyData)
    })
    .then(response => response.json())
    .then(data => {
        // Hide loading indicator
        document.querySelector('.loading').style.display = 'none';
        
        if (data.error) {
            alert(`Error: ${data.error}`);
            return;
        }
        
        // Show the result
        document.querySelector('.results').style.display = 'block';
        document.getElementById('predicted-price').textContent = data.predictedRent.toLocaleString();
        
        // Highlight the prediction result with animation
        const predictionElement = document.getElementById('predicted-price').parentElement;
        predictionElement.style.transform = 'scale(1.05)';
        setTimeout(() => {
            predictionElement.style.transition = 'transform 0.5s ease';
            predictionElement.style.transform = 'scale(1)';
        }, 50);
        
        // If we have latitude and longitude, add a marker for the prediction
        if (propertyData.latitude && propertyData.longitude) {
            // Add a marker for the prediction
            const markerPosition = {
                lat: propertyData.latitude,
                lng: propertyData.longitude
            };
            
            // Center map on the prediction location
            map.setCenter(markerPosition);
            map.setZoom(15);
            
            // Remove previous prediction marker if exists
            markers.forEach(marker => {
                if (marker.title === 'Your Prediction') {
                    marker.setMap(null);
                }
            });
            
            // Add new prediction marker
            const marker = new google.maps.Marker({
                position: markerPosition,
                map: map,
                title: 'Your Prediction',
                animation: google.maps.Animation.DROP,
                icon: {
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 14,
                    fillColor: '#e74c3c',
                    fillOpacity: 0.8,
                    strokeColor: 'white',
                    strokeWeight: 2
                }
            });
            
            // Create info window content
            const contentString = `
                <div class="marker-popup">
                    <h3>Your Rental Prediction</h3>
                    <p class="price">$${data.predictedRent.toLocaleString()}/month</p>
                    <p><strong>${propertyData.bedrooms}</strong> beds, <strong>${propertyData.bathrooms}</strong> baths</p>
                    ${propertyData.livingArea ? `<p><strong>${propertyData.livingArea}</strong> sq ft</p>` : ''}
                    ${propertyData.propertyType ? `<p>Property Type: ${propertyData.propertyType.replace(/_/g, ' ').toLowerCase()}</p>` : ''}
                    <p>Zipcode: ${propertyData.zipcode}</p>
                </div>
            `;
            
            const infoWindow = new google.maps.InfoWindow({
                content: contentString
            });
            
            // Add click listener to show info window
            marker.addListener('click', () => {
                if (currentInfoWindow) {
                    currentInfoWindow.close();
                }
                infoWindow.open(map, marker);
                currentInfoWindow = infoWindow;
            });
            
            // Open info window initially
            infoWindow.open(map, marker);
            currentInfoWindow = infoWindow;
            
            markers.push(marker);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.querySelector('.loading').style.display = 'none';
        alert('An error occurred while making the prediction. Please try again.');
    });
}

// Handle form submission
document.getElementById('prediction-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    // Get required form values
    const propertyData = {
        zipcode: document.getElementById('zipcode').value,
        bedrooms: parseInt(document.getElementById('bedrooms').value),
        bathrooms: parseFloat(document.getElementById('bathrooms').value)
    };
    
    // Add optional fields if they have values
    const latitude = document.getElementById('latitude').value;
    if (latitude) {
        propertyData.latitude = parseFloat(latitude);
    }
    
    const longitude = document.getElementById('longitude').value;
    if (longitude) {
        propertyData.longitude = parseFloat(longitude);
    }
    
    const propertyType = document.getElementById('property-type').value;
    if (propertyType) {
        propertyData.propertyType = propertyType;
    }
    
    const livingArea = document.getElementById('living-area').value;
    if (livingArea) {
        propertyData.livingArea = parseInt(livingArea);
    }
    
    const lotArea = document.getElementById('lot-area').value;
    if (lotArea) {
        propertyData.lotArea = parseFloat(lotArea);
    }
    
    // Make prediction
    makePrediction(propertyData);
});

// Initialize charts when page loads
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
});