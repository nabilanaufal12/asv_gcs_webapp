// Variabel privat untuk modul ini
let map;
let asvMarker;
let waypointLayer;

// Inisialisasi peta dan elemen-elemennya
export function initMap() {
  map = L.map("map").setView([-6.9175, 107.6191], 13);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution:
      '© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map);

  const asvIcon = L.icon({
    iconUrl: "https://placehold.co/40x40/3498db/ffffff?text=ASV",
    iconSize: [40, 40],
    iconAnchor: [20, 20],
  });
  asvMarker = L.marker([-6.9175, 107.6191], { icon: asvIcon }).addTo(map);
  asvMarker.bindPopup("<b>Posisi ASV</b>");
  waypointLayer = L.layerGroup().addTo(map);
  console.log("Map handler initialized.");
}

// Memperbarui posisi marker ASV di peta
export function updateAsvPosition(lat, lon) {
  if (!map || !asvMarker) return;
  const newPosition = [lat, lon];
  asvMarker.setLatLng(newPosition);
  map.panTo(newPosition);
  asvMarker.setPopupContent(
    `<b>Posisi ASV</b><br>Lat: ${lat.toFixed(6)}<br>Lon: ${lon.toFixed(6)}`
  );
}

// Menggambar ulang semua waypoint dan rute di peta
export function updateWaypointsOnMap(waypoints, waypointListElement) {
  if (!map || !waypointLayer) return;

  waypointLayer.clearLayers();
  waypointListElement.innerHTML = "";
  const latLngs = [];

  waypoints.forEach((wp, index) => {
    const pos = [wp.lat, wp.lon];
    latLngs.push(pos);
    L.marker(pos, {
      icon: L.icon({
        iconUrl: `https://placehold.co/30x30/2ecc71/ffffff?text=${index + 1}`,
        iconSize: [30, 30],
        iconAnchor: [15, 15],
      }),
    }).addTo(waypointLayer);

    const li = document.createElement("li");
    li.className =
      "flex justify-between items-center bg-slate-100 p-2 rounded-md text-sm";
    li.innerHTML = `<span>${index + 1}: ${wp.lat}, ${
      wp.lon
    }</span><button data-index="${index}" class="delete-wp-btn text-red-500 hover:text-red-700 font-bold text-lg">&times;</button>`;
    waypointListElement.appendChild(li);
  });

  if (latLngs.length > 1) {
    L.polyline(latLngs, { color: "red", weight: 3 }).addTo(waypointLayer);
  }
}
