import { elements } from "./uiElements.js";

let pidChart;

// Inisialisasi grafik PID
export function initChart() {
  pidChart = new Chart(elements.pidChartCanvas, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Setpoint",
          borderColor: "rgb(59, 130, 246)",
          backgroundColor: "rgba(59, 130, 246, 0.1)",
          data: [],
          tension: 0.2,
          pointRadius: 0,
        },
        {
          label: "Actual Value",
          borderColor: "rgb(239, 68, 68)",
          backgroundColor: "rgba(239, 68, 68, 0.1)",
          data: [],
          tension: 0.2,
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { ticks: { color: "#475569" }, grid: { color: "#e2e8f0" } },
        y: { ticks: { color: "#475569" }, grid: { color: "#e2e8f0" } },
      },
      plugins: {
        legend: { labels: { color: "#334155" } },
      },
    },
  });
  console.log("Chart handler initialized.");
}

// Memperbarui data pada grafik PID
export function updatePidGraph(data) {
  if (!pidChart) return;
  const chartData = pidChart.data;
  chartData.labels.push(new Date().toLocaleTimeString());
  chartData.datasets[0].data.push(data.setpoint);
  chartData.datasets[1].data.push(data.actual);

  const maxDataPoints = 30;
  if (chartData.labels.length > maxDataPoints) {
    chartData.labels.shift();
    chartData.datasets.forEach((dataset) => {
      dataset.data.shift();
    });
  }
  pidChart.update();
}
