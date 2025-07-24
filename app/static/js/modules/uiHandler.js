import { elements } from "./uiElements.js";
import { emitCommand } from "./socketHandler.js";

// Ikon SVG untuk tombol toggle video, disimpan sebagai konstanta agar rapi
const playIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;
const pauseIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;

// --- Kumpulan Fungsi untuk Memperbarui Tampilan (UI) ---

export function updateTelemetryDisplay(data) {
  elements.coordsDisplay.textContent = `${data.lat.toFixed(
    6
  )}, ${data.lon.toFixed(6)}`;
  elements.speedDisplay.textContent = `${data.speed} knots`;
  elements.headingDisplay.textContent = `${data.heading} °`;
  elements.batteryDisplay.textContent = `${data.battery} %`;
}

export function updateDetectionInfo(data) {
  if (data && data.label) {
    elements.detectionLabel.textContent = data.label;
    elements.detectionConfidence.textContent = `${(
      data.confidence * 100
    ).toFixed(1)}%`;
    elements.detectionMidpoint.textContent = `(${data.midpoint_x}, ${data.midpoint_y})`;
    elements.detectionSteering.textContent = `${data.steering_angle} °`;
  } else {
    elements.detectionLabel.textContent = "--";
    elements.detectionConfidence.textContent = "0.00%";
    elements.detectionMidpoint.textContent = "(-, -)";
    elements.detectionSteering.textContent = "0 °";
  }
}

export function updateVehicleMode(newMode) {
  elements.vehicleModeDisplay.textContent = newMode;
  if (newMode === "Auto") {
    elements.modeSwitchBtn.textContent = "Beralih ke Mode Manual";
    // Menggunakan classList untuk menghindari penimpaan kelas
    elements.vehicleModeDisplay.classList.remove(
      "text-blue-800",
      "bg-blue-100"
    );
    elements.vehicleModeDisplay.classList.add("text-green-800", "bg-green-100");
    elements.manualControlPanel.classList.add("hidden");
    elements.navigationControlPanel.classList.remove("hidden");
  } else {
    elements.modeSwitchBtn.textContent = "Beralih ke Mode Auto";
    elements.vehicleModeDisplay.classList.remove(
      "text-green-800",
      "bg-green-100"
    );
    elements.vehicleModeDisplay.classList.add("text-blue-800", "bg-blue-100");
    elements.manualControlPanel.classList.remove("hidden");
    elements.navigationControlPanel.classList.add("hidden");
  }
}

export function updateMissionStatus(newStatus) {
  elements.missionStatusDisplay.textContent = newStatus;
  // Reset semua kelas warna terlebih dahulu
  elements.missionStatusDisplay.classList.remove(
    "bg-slate-200",
    "text-slate-800",
    "bg-green-100",
    "text-green-800",
    "bg-yellow-100",
    "text-yellow-800"
  );

  switch (newStatus) {
    case "Idle":
      elements.missionStartPauseBtn.textContent = "Mulai Misi";
      elements.missionStartPauseBtn.classList.remove(
        "bg-yellow-500",
        "hover:bg-yellow-600"
      );
      elements.missionStartPauseBtn.classList.add(
        "bg-green-600",
        "hover:bg-green-700"
      );
      elements.missionStatusDisplay.classList.add(
        "bg-slate-200",
        "text-slate-800"
      );
      break;
    case "Running":
      elements.missionStartPauseBtn.textContent = "Jeda Misi";
      elements.missionStartPauseBtn.classList.remove(
        "bg-green-600",
        "hover:bg-green-700"
      );
      elements.missionStartPauseBtn.classList.add(
        "bg-yellow-500",
        "hover:bg-yellow-600"
      );
      elements.missionStatusDisplay.classList.add(
        "bg-green-100",
        "text-green-800"
      );
      break;
    case "Paused":
      elements.missionStartPauseBtn.textContent = "Lanjutkan Misi";
      elements.missionStartPauseBtn.classList.remove(
        "bg-yellow-500",
        "hover:bg-yellow-600"
      );
      elements.missionStartPauseBtn.classList.add(
        "bg-green-600",
        "hover:bg-green-700"
      );
      elements.missionStatusDisplay.classList.add(
        "bg-yellow-100",
        "text-yellow-800"
      );
      break;
  }
}

export function updatePidGains(gains) {
  elements.kpInput.value = gains.kp;
  elements.kiInput.value = gains.ki;
  elements.kdInput.value = gains.kd;
}

export function updateServoLimits(limits) {
  elements.servoMinInput.value = limits.min;
  elements.servoMaxInput.value = limits.max;
}

export function updateVideoStreamStatus(status) {
  if (status.active) {
    elements.videoToggleBtn.innerHTML = pauseIcon;
    elements.videoStream.classList.remove("hidden");
    elements.videoPlaceholder.classList.add("hidden");
  } else {
    elements.videoToggleBtn.innerHTML = playIcon;
    elements.videoStream.classList.add("hidden");
    elements.videoPlaceholder.classList.remove("hidden");
    elements.videoStream.src = "";
  }
}

export function addLogEntry(log) {
  const li = document.createElement("li");
  let colorClass = "text-slate-500";
  if (log.level === "success") colorClass = "text-green-600";
  if (log.level === "warning") colorClass = "text-yellow-600";
  if (log.level === "error") colorClass = "text-red-600";
  li.className = colorClass;
  li.innerHTML = `<span class="text-slate-400">${log.timestamp}</span> &gt; ${log.message}`;
  elements.activityLogList.appendChild(li);
  elements.activityLogList.parentElement.scrollTop =
    elements.activityLogList.parentElement.scrollHeight;
}

export function showNotification(data) {
  let backgroundColor;
  switch (data.type) {
    case "success":
      backgroundColor = "linear-gradient(to right, #00b09b, #96c93d)";
      break;
    case "error":
      backgroundColor = "linear-gradient(to right, #ff5f6d, #ffc371)";
      break;
    default:
      backgroundColor = "linear-gradient(to right, #4facfe, #00f2fe)";
      break;
  }
  Toastify({
    text: data.message,
    duration: 3000,
    close: true,
    gravity: "top",
    position: "right",
    stopOnFocus: true,
    style: { background: backgroundColor },
  }).showToast();
}

// --- Fungsi Utama untuk Menginisialisasi Semua Event Listener ---
export function initEventListeners() {
  // Waypoint
  elements.waypointForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (elements.latInput.value && elements.lonInput.value) {
      emitCommand("add_waypoint", {
        lat: elements.latInput.value,
        lon: elements.lonInput.value,
      });
      elements.latInput.value = "";
      elements.lonInput.value = "";
    }
  });

  elements.waypointListElement.addEventListener("click", (e) => {
    if (e.target && e.target.classList.contains("delete-wp-btn")) {
      const index = parseInt(e.target.getAttribute("data-index"));
      emitCommand("delete_waypoint", index);
    }
  });

  // Kontrol Kendaraan & Navigasi
  elements.openMonitorBtn.addEventListener("click", () =>
    window.open("/monitor", "_blank")
  );
  elements.modeSwitchBtn.addEventListener("click", () =>
    emitCommand("set_vehicle_mode")
  );
  elements.emergencyStopBtn.addEventListener("click", () => {
    if (window.confirm("Apakah Anda yakin?")) emitCommand("emergency_stop");
  });
  elements.manualControlBtns.forEach((button) =>
    button.addEventListener("mousedown", function () {
      emitCommand("manual_control", { direction: this.id.split("-")[1] });
    })
  );
  window.addEventListener("mouseup", () =>
    emitCommand("manual_control", { direction: "stop" })
  );
  elements.speedSlider.addEventListener("input", function () {
    elements.speedValueDisplay.textContent = `${this.value}%`;
  });
  elements.speedSlider.addEventListener("change", function () {
    emitCommand("set_speed", { speed: this.value });
  });
  elements.missionStartPauseBtn.addEventListener("click", () =>
    emitCommand("mission_command", { command: "start_pause" })
  );
  elements.missionResetBtn.addEventListener("click", () =>
    emitCommand("mission_command", { command: "reset" })
  );
  elements.autoSpeedSlider.addEventListener("input", function () {
    elements.autoSpeedValueDisplay.textContent = `${this.value}%`;
  });
  elements.autoSpeedSlider.addEventListener("change", function () {
    emitCommand("set_auto_speed", { speed: this.value });
  });

  // Pengaturan
  elements.pidSaveBtn.addEventListener("click", () =>
    emitCommand("set_pid_gains", {
      kp: elements.kpInput.value,
      ki: elements.kiInput.value,
      kd: elements.kdInput.value,
    })
  );
  elements.servoSaveBtn.addEventListener("click", () =>
    emitCommand("set_servo_limits", {
      min: elements.servoMinInput.value,
      max: elements.servoMaxInput.value,
    })
  );

  // Kontrol Tampilan Pusat
  elements.snapshotBtn.addEventListener("click", () =>
    emitCommand("take_snapshot")
  );
  elements.videoToggleBtn.addEventListener("click", () =>
    emitCommand("toggle_video_stream")
  );

  function switchTab(activeTab, inactiveTab) {
    // Menggunakan classList untuk mengelola gaya tab
    activeTab.classList.remove("text-slate-500", "hover:bg-blue-50");
    activeTab.classList.add("text-white", "bg-blue-600");

    inactiveTab.classList.remove("text-white", "bg-blue-600");
    inactiveTab.classList.add("text-slate-500", "hover:bg-blue-50");

    if (activeTab.id === "tab-map") {
      elements.contentMap.classList.remove("hidden");
      elements.contentVideo.classList.add("hidden");
      elements.videoControls.classList.add("hidden");
      window.dispatchEvent(new Event("resize")); // Penting untuk render peta
    } else {
      elements.contentMap.classList.add("hidden");
      elements.contentVideo.classList.remove("hidden");
      elements.videoControls.classList.remove("hidden");
    }
  }

  elements.tabMap.addEventListener("click", () =>
    switchTab(elements.tabMap, elements.tabVideo)
  );
  elements.tabVideo.addEventListener("click", () =>
    switchTab(elements.tabVideo, elements.tabMap)
  );

  console.log("UI event listeners initialized.");
}
