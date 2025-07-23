import { updateAsvPosition, updateWaypointsOnMap } from "./mapHandler.js";
import { updatePidGraph } from "./chartHandler.js";
import * as ui from "./uiHandler.js";
import { elements } from "./uiElements.js";

let socket;

// Fungsi untuk mengirim perintah ke server
export function emitCommand(event, data) {
  if (socket) {
    socket.emit(event, data);
  } else {
    console.error("Socket not initialized.");
  }
}

// Inisialisasi koneksi Socket.IO dan semua event listeners
export function initSocket() {
  socket = io();

  socket.on("connect", () => {
    console.log("Terhubung ke server!");
    ui.addLogEntry({
      timestamp: new Date().toLocaleTimeString(),
      message: "Koneksi ke server berhasil.",
      level: "success",
    });
    elements.connectionDot.className = "h-3 w-3 rounded-full bg-green-500 mr-2";
    elements.connectionText.textContent = "Terhubung";
  });

  socket.on("disconnect", () => {
    console.log("Terputus dari server.");
    ui.addLogEntry({
      timestamp: new Date().toLocaleTimeString(),
      message: "Koneksi ke server terputus.",
      level: "error",
    });
    elements.connectionDot.className = "h-3 w-3 rounded-full bg-red-500 mr-2";
    elements.connectionText.textContent = "Terputus";
  });

  // Menghubungkan event dari server ke fungsi yang relevan
  socket.on("update_telemetry", (data) => {
    updateAsvPosition(data.lat, data.lon);
    ui.updateTelemetryDisplay(data);
  });

  socket.on("update_waypoints", (waypoints) => {
    updateWaypointsOnMap(waypoints, elements.waypointListElement);
  });

  socket.on("update_video_frame", (frame) => {
    elements.videoStream.src = "data:image/jpeg;base64," + frame;
  });

  socket.on("update_detection_info", ui.updateDetectionInfo);
  socket.on("update_vehicle_mode", ui.updateVehicleMode);
  socket.on("update_mission_status", ui.updateMissionStatus);
  socket.on("update_pid_gains", ui.updatePidGains);
  socket.on("update_servo_limits", ui.updateServoLimits);
  socket.on("video_stream_status", ui.updateVideoStreamStatus);
  socket.on("update_pid_graph", updatePidGraph);
  socket.on("new_log_entry", ui.addLogEntry);
  socket.on("show_notification", ui.showNotification);

  console.log("Socket handler initialized.");
}
