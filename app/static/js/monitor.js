document.addEventListener("DOMContentLoaded", function () {
  console.log("Monitor UI Initializing...");

  // Ambil elemen UI dari HTML
  const videoStream = document.getElementById("video-stream");
  const connectionDot = document.getElementById("connection-indicator-dot");
  const connectionText = document.getElementById("connection-indicator-text");
  const missionStatusDisplay = document.getElementById(
    "mission-status-display"
  );
  const speedDisplay = document.getElementById("speed-display");
  const headingDisplay = document.getElementById("heading-display");
  const batteryDisplay = document.getElementById("battery-display");

  // Inisialisasi koneksi Socket.IO
  const socket = io();

  // Mengelola status koneksi
  socket.on("connect", () => {
    console.log("Connected to server!");
    connectionDot.className = "h-4 w-4 rounded-full bg-green-500 mr-3";
    connectionText.textContent = "CONNECTED";
  });

  socket.on("disconnect", () => {
    console.log("Disconnected from server.");
    connectionDot.className = "h-4 w-4 rounded-full bg-red-500 mr-3";
    connectionText.textContent = "DISCONNECTED";
  });

  // Menerima dan menampilkan frame video
  socket.on("update_video_frame", function (frame) {
    videoStream.src = "data:image/jpeg;base64," + frame;
  });

  // Menerima dan menampilkan data telemetri
  socket.on("update_telemetry", function (data) {
    speedDisplay.innerHTML = `${data.speed} <span class="text-lg">knots</span>`;
    headingDisplay.innerHTML = `${data.heading} <span class="text-lg">°</span>`;
    batteryDisplay.innerHTML = `${data.battery} <span class="text-lg">%</span>`;
  });

  // Menerima dan menampilkan status misi
  socket.on("update_mission_status", function (newStatus) {
    missionStatusDisplay.textContent = `MISSION: ${newStatus.toUpperCase()}`;
  });

  console.log("Monitor UI Ready.");
});
