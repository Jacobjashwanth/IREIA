import '../styles/MapPopup.css';

export function initMapWithProperties(properties) {
  if (!window.google || !window.google.maps || !Array.isArray(properties)) {
    console.warn("Google Maps is not ready or invalid properties.");
    return;
  }

  const first = properties.find(p => p.latitude && p.longitude);
  if (!first) return;

  const mapDiv = document.getElementById("map");
  if (!mapDiv) return;

  const map = new window.google.maps.Map(mapDiv, {
    center: { lat: first.latitude, lng: first.longitude },
    zoom: 13,
    mapTypeControl: true,
    streetViewControl: true,
    mapTypeId: 'roadmap',
  });

  let activeInfoWindow = null;
  let pinnedInfoWindow = null;

  properties.forEach((prop) => {
    if (!prop.latitude || !prop.longitude) return;

    const isOverpriced = prop.recommendation?.includes("Over");
    const color = isOverpriced ? "#ff4d4f" : "#52c41a";

    const boxIcon = {
      url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`
        <svg xmlns="http://www.w3.org/2000/svg" width="100" height="36">
          <rect width="100" height="36" rx="8" ry="8" fill="${color}" />
          <text x="50" y="24" font-size="14" font-family="Arial" fill="white" font-weight="bold" text-anchor="middle">
            $${Number(prop.current_price).toLocaleString()}
          </text>
        </svg>
      `)}`,
      scaledSize: new window.google.maps.Size(100, 36),
      anchor: new window.google.maps.Point(50, 18),
    };

    const marker = new window.google.maps.Marker({
      position: { lat: prop.latitude, lng: prop.longitude },
      map,
      title: prop.address,
      icon: boxIcon,
    });

    const popupContent = document.createElement('div');
    popupContent.className = "map-popup-container";
    popupContent.innerHTML = `
      <img src="${prop.image_url}" alt="Property" class="map-popup-image" />
      <div class="map-popup-address">${prop.address}</div>
      💰 <b>List:</b> $${Number(prop.current_price).toLocaleString()}<br>
      📈 <b>Predicted:</b> $${Number(prop.predicted_price).toLocaleString()}<br>
      <span class="map-popup-recommend" style="color: ${isOverpriced ? '#ff4d4f' : '#4CAF50'};">
        ${prop.recommendation}
      </span>
      <br>
      <button class="map-popup-button">View Details</button>
    `;

    const infoWindow = new window.google.maps.InfoWindow({
      content: popupContent,
    });

    // 👉 Hover behavior
    marker.addListener("mouseover", () => {
      if (!pinnedInfoWindow) {
        if (activeInfoWindow && activeInfoWindow !== infoWindow) {
          activeInfoWindow.close();
        }
        infoWindow.open(map, marker);
        activeInfoWindow = infoWindow;
      }
    });

    marker.addListener("mouseout", () => {
      if (!pinnedInfoWindow && activeInfoWindow === infoWindow) {
        infoWindow.close();
        activeInfoWindow = null;
      }
    });

    // 👉 Click behavior (pin popup)
    marker.addListener("click", () => {
      if (pinnedInfoWindow && pinnedInfoWindow !== infoWindow) {
        pinnedInfoWindow.close();
      }
      infoWindow.open(map, marker);
      pinnedInfoWindow = infoWindow;
      activeInfoWindow = infoWindow;
    });

    // ✅ Handle popup close to unpin
    window.google.maps.event.addListener(infoWindow, 'closeclick', () => {
      if (pinnedInfoWindow === infoWindow) {
        pinnedInfoWindow = null;
      }
      if (activeInfoWindow === infoWindow) {
        activeInfoWindow = null;
      }
    });

    // View Details
    window.google.maps.event.addListener(infoWindow, 'domready', () => {
      const viewButton = popupContent.querySelector('.map-popup-button');
      if (viewButton) {
        viewButton.onclick = () => {
          localStorage.setItem('selected_property', JSON.stringify(prop));
          window.location.href = '/property';
        };
      }
    });
  });

  return map;
}