import { initMap } from "./modules/mapHandler.js";
import { initChart } from "./modules/chartHandler.js";
import { initEventListeners } from "./modules/uiHandler.js";
import { initSocket } from "./modules/socketHandler.js";

// Menunggu hingga seluruh halaman dimuat sebelum menjalankan skrip
document.addEventListener("DOMContentLoaded", () => {
  console.log("Application starting...");

  // 1. Inisialisasi komponen visual
  initMap();
  initChart();

  // 2. Inisialisasi event listeners untuk interaksi pengguna
  initEventListeners();

  // 3. Inisialisasi koneksi WebSocket untuk komunikasi real-time
  initSocket();

  console.log("Application initialized successfully.");
});
