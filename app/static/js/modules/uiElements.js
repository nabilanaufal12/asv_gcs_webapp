// File ini mengekspor sebuah objek yang berisi semua referensi ke elemen DOM
// agar mudah diakses dari modul lain tanpa perlu mengulang getElementById.

export const elements = {
  // Status & Info
  coordsDisplay: document.getElementById("coords-display"),
  speedDisplay: document.getElementById("speed-display"),
  headingDisplay: document.getElementById("heading-display"),
  batteryDisplay: document.getElementById("battery-display"),
  connectionDot: document.getElementById("connection-indicator-dot"),
  connectionText: document.getElementById("connection-indicator-text"),

  // Deteksi Objek
  detectionLabel: document.getElementById("detection-label"),
  detectionConfidence: document.getElementById("detection-confidence"),
  detectionMidpoint: document.getElementById("detection-midpoint"),
  detectionSteering: document.getElementById("detection-steering"),

  // Waypoints
  waypointForm: document.getElementById("waypoint-form"),
  latInput: document.getElementById("lat-input"),
  lonInput: document.getElementById("lon-input"),
  waypointListElement: document.getElementById("waypoint-list"),

  // Kontrol Kendaraan
  modeSwitchBtn: document.getElementById("mode-switch-btn"),
  emergencyStopBtn: document.getElementById("emergency-stop-btn"),
  vehicleModeDisplay: document.getElementById("vehicle-mode-display"),

  // Kontrol Manual & Navigasi
  manualControlPanel: document.getElementById("manual-control-panel"),
  navigationControlPanel: document.getElementById("navigation-control-panel"),
  manualControlBtns: document.querySelectorAll(".manual-control-btn"),
  speedSlider: document.getElementById("speed-slider"),
  speedValueDisplay: document.getElementById("speed-value-display"),

  // Misi
  missionStartPauseBtn: document.getElementById("mission-start-pause-btn"),
  missionResetBtn: document.getElementById("mission-reset-btn"),
  missionStatusDisplay: document.getElementById("mission-status-display"),
  autoSpeedSlider: document.getElementById("auto-speed-slider"),
  autoSpeedValueDisplay: document.getElementById("auto-speed-value-display"),

  // PID
  kpInput: document.getElementById("kp-input"),
  kiInput: document.getElementById("ki-input"),
  kdInput: document.getElementById("kd-input"),
  pidSaveBtn: document.getElementById("pid-save-btn"),
  pidChartCanvas: document.getElementById("pid-chart"),

  // Servo
  servoMinInput: document.getElementById("servo-min-input"),
  servoMaxInput: document.getElementById("servo-max-input"),
  servoSaveBtn: document.getElementById("servo-save-btn"),

  // Tampilan Pusat (Peta/Video)
  tabMap: document.getElementById("tab-map"),
  tabVideo: document.getElementById("tab-video"),
  contentMap: document.getElementById("content-map"),
  contentVideo: document.getElementById("content-video"),
  videoStream: document.getElementById("video-stream"),
  videoControls: document.getElementById("video-controls"),
  videoToggleBtn: document.getElementById("video-toggle-btn"),
  videoPlaceholder: document.getElementById("video-placeholder"),
  snapshotBtn: document.getElementById("snapshot-btn"),

  // Log
  activityLogList: document.getElementById("activity-log-list"),
};
