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
  
      const infoWindow = new window.google.maps.InfoWindow({
        content: `
          <div style="font-size: 13px; line-height: 1.4;">
            <strong>${prop.address}</strong><br>
            💰 <b>List:</b> $${Number(prop.current_price).toLocaleString()}<br>
            📈 <b>Predicted:</b> $${Number(prop.predicted_price).toLocaleString()}<br>
            <em>${prop.recommendation}</em>
          </div>
        `,
      });
  
      marker.addListener("mouseover", () => infoWindow.open(map, marker));
      marker.addListener("mouseout", () => infoWindow.close());
    });
  }