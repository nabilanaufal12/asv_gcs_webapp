import paho.mqtt.client as mqtt
import time
import json

# --- Konfigurasi ---
MQTT_BROKER_URL = "broker.hivemq.com"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "asv/telemetry"

# --- Data Simulasi ---
lat = -6.9175  # Lokasi awal di Bandung
lon = 107.6191
speed = 10.0
heading = 45.0
battery = 100.0

def on_connect(client, userdata, flags, rc):
    """Callback yang dipanggil saat berhasil terhubung ke broker."""
    if rc == 0:
        print(f"Berhasil terhubung ke MQTT Broker: {MQTT_BROKER_URL}")
    else:
        print(f"Gagal terhubung, return code {rc}\n")

# Inisialisasi MQTT Client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="asv_simulator")
client.on_connect = on_connect
client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT)
client.loop_start() # Memulai network loop di background thread

print("Simulator ASV dimulai. Tekan CTRL+C untuk berhenti.")

try:
    while True:
        # Simulasikan pergerakan kapal
        lat += 0.0001
        lon += 0.0001
        battery -= 0.1
        if battery < 0:
            battery = 100.0

        # Siapkan data dalam format dictionary
        telemetry_data = {
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "speed": speed,
            "heading": heading,
            "battery": round(battery, 2)
        }

        # Ubah dictionary menjadi string JSON
        payload = json.dumps(telemetry_data)

        # Publikasikan data ke topik MQTT
        result = client.publish(MQTT_TOPIC, payload)
        status = result[0]
        if status == 0:
            print(f"Mengirim data ke topik '{MQTT_TOPIC}': {payload}")
        else:
            print(f"Gagal mengirim pesan ke topik '{MQTT_TOPIC}'")

        # Tunggu 2 detik sebelum mengirim data berikutnya
        time.sleep(2)

except KeyboardInterrupt:
    print("Simulator dihentikan.")
    client.loop_stop()
    client.disconnect()

