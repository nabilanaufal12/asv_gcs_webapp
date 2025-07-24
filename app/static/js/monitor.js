// File: app/static/js/monitor.js

// Berjalan saat seluruh halaman HTML sudah dimuat
document.addEventListener("DOMContentLoaded", () => {
  // ===== INISIALISASI VARIABEL =====
  const mapContainer = document.getElementById("map");
  let map, vehicleIcon, vehicleMarker, vehicleTrace;
  let isMarkerAdded = false; // Tandai apakah marker sudah ditambahkan ke peta

  // ===== INISIALISASI PETA (DENGAN PENGECEKAN) =====
  // Periksa apakah container peta ada dan belum diinisialisasi oleh Leaflet
  if (mapContainer && !mapContainer._leaflet_id) {
    // 1. Buat Peta
    // Koordinat awal bisa diatur ke lokasi yang relevan, misal: Tanjung Pinang
    map = L.map("map").setView([0.9196, 104.4472], 13);

    // 2. Tambahkan Layer Peta (Tile Layer)
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(map);

    // 3. Buat Ikon Kustom untuk Wahana
    // PERBAIKAN: Menggunakan path folder 'images' yang benar
    vehicleIcon = L.icon({
      iconUrl: "/static/images/asv_icon.png",
      iconSize: [40, 40],
      iconAnchor: [20, 20], // Titik tengah ikon
    });

    // 4. Buat Marker untuk Wahana (tanpa menambahkannya ke peta dulu)
    vehicleMarker = L.marker([0, 0], {
      icon: vehicleIcon,
      rotationAngle: 0, // Properti dari plugin leaflet-rotatedmarker
    });

    // 5. Buat Garis untuk Jejak Lintasan
    vehicleTrace = L.polyline([], { color: "cyan", weight: 3 }).addTo(map);

    console.log("Map initialized successfully.");
  }

  // ===== KONEKSI WEBSOCKET =====
  const socket = io(); // Terhubung ke namespace default

  socket.on("connect", () => {
    const statusEl = document.getElementById("connection-status");
    statusEl.textContent = "CONNECTED";
    statusEl.className = "text-green-400"; // Mengganti class untuk warna
    console.log("Terhubung ke server GCS via WebSocket.");
  });

  socket.on("disconnect", () => {
    const statusEl = document.getElementById("connection-status");
    statusEl.textContent = "DISCONNECTED";
    statusEl.className = "text-red-500";
    console.log("Koneksi ke server terputus.");
  });

  // ===== EVENT HANDLER (MENERIMA DATA DARI SERVER) =====

  // 1. Menerima data telemetri utama dari wahana
  socket.on("update_telemetry", (data) => {
    // Update Tampilan Teks Telemetri
    document.getElementById("speed-display").innerHTML = `${
      data.speed?.toFixed(1) || 0.0
    } <span class="text-base">knots</span>`;
    document.getElementById("heading-display").innerHTML = `${
      Math.round(data.heading) || 0
    } <span class="text-base">°</span>`;
    document.getElementById("battery-display").innerHTML = `${
      data.battery?.toFixed(1) || 0
    } <span class="text-base">%</span>`;

    // Update Posisi Wahana di Peta
    // Pastikan data lat/lon ada dan peta sudah diinisialisasi
    if (data.lat && data.lon && map) {
      const newLatLng = new L.LatLng(data.lat, data.lon);

      // Perbarui posisi dan rotasi marker
      vehicleMarker.setLatLng(newLatLng);
      vehicleMarker.setRotationAngle(data.heading || 0);

      // Tambahkan titik baru ke jejak lintasan
      vehicleTrace.addLatLng(newLatLng);

      // Jika ini data posisi pertama yang diterima, tambahkan marker ke peta
      if (!isMarkerAdded) {
        vehicleMarker.addTo(map);
        map.setView(newLatLng, 17); // Pusatkan peta ke wahana dengan zoom lebih dekat
        isMarkerAdded = true;
      }
    }
  });

  // 2. Menerima frame video dari server
  socket.on("update_video_frame", (frame_str) => {
    const videoElement = document.getElementById("video-stream");
    videoElement.src = `data:image/jpeg;base64,${frame_str}`;
  });

  // 3. Menerima status video stream (misal: aktif/tidak aktif)
  socket.on("video_stream_status", (data) => {
    const btn = document.getElementById("toggle-video-btn");
    if (data.active) {
      btn.textContent = "STOP VIDEO";
      btn.classList.remove("bg-blue-500", "hover:bg-blue-600");
      btn.classList.add("bg-red-500", "hover:bg-red-600");
    } else {
      btn.textContent = "START VIDEO";
      btn.classList.remove("bg-red-500", "hover:bg-red-600");
      btn.classList.add("bg-blue-500", "hover:bg-blue-600");
      // Kosongkan gambar jika stream berhenti
      document.getElementById("video-stream").src = "";
    }
  });

  // 4. Menerima status misi
  socket.on("update_mission_status", (status) => {
    const statusDisplay = document.getElementById("mission-status-display");
    statusDisplay.textContent = `MISSION: ${status.toUpperCase()}`;
  });

  // ===== KONTROL DARI PENGGUNA (MENGIRIM EVENT KE SERVER) =====
  const videoBtn = document.getElementById("toggle-video-btn");
  if (videoBtn) {
    videoBtn.addEventListener("click", () => {
      console.log("Tombol video diklik, mengirim 'toggle_video_stream'");
      socket.emit("toggle_video_stream");
    });
  }
});
