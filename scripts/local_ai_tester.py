import cv2
import torch
import numpy as np
import pathlib
import json
import base64
import paho.mqtt.client as mqtt
import time

# --- Konfigurasi MQTT ---
MQTT_BROKER_URL = "broker.hivemq.com"
MQTT_BROKER_PORT = 1883
MQTT_VIDEO_TOPIC = "asv/video_stream"
MQTT_DETECTION_TOPIC = "asv/detection_info"

# --- Inisialisasi MQTT Client ---
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="local_ai_tester")
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Berhasil terhubung ke MQTT Broker.")
    else:
        print(f"❌ Gagal terhubung ke MQTT, kode: {rc}")
mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT)
mqtt_client.loop_start()

# Fix Path untuk Windows
pathlib.PosixPath = pathlib.WindowsPath

# YOLOv5
from models.common import DetectMultiBackend
from utils.general import non_max_suppression, scale_boxes
from utils.torch_utils import select_device

# Load model
try:
    model_path = 'best.pt'
    device = select_device('')
    model = DetectMultiBackend(model_path, device=device, dnn=False)
    stride, names = model.stride, model.names
    model.warmup(imgsz=(1, 3, 640, 640))
    print("✅ Model AI 'best.pt' berhasil dimuat.")
except Exception as e:
    print(f"❌ Gagal memuat model 'best.pt'. Pastikan file ada di folder yang sama. Error: {e}")
    exit()


# Webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Gagal membuka webcam.")
    exit()

print("🚀 Skrip pengujian AI dimulai. Tekan 'q' di jendela video untuk berhenti.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Gagal baca webcam.")
        break

    # --- Logika Deteksi AI (dari deded1.py) ---
    img = cv2.resize(frame, (640, 640))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_tensor = torch.from_numpy(img_rgb).to(device)
    img_tensor = img_tensor.permute(2, 0, 1).float() / 255.0
    img_tensor = img_tensor.unsqueeze(0)

    with torch.no_grad():
        pred = model(img_tensor, augment=False, visualize=False)
        pred = non_max_suppression(pred, conf_thres=0.4, iou_thres=0.45)

    detection_info = None # Reset info deteksi setiap frame

    for det in pred:
        if len(det):
            det[:, :4] = scale_boxes(img_tensor.shape[2:], det[:, :4], frame.shape).round()

            for *xyxy, conf, cls in det:
                class_name = names[int(cls)]
                x1, y1, x2, y2 = map(int, xyxy)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                
                # Gambar kotak di frame
                color = (0, 255, 0) if "Green" in class_name else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{class_name} ({conf:.2f})", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                # Siapkan data deteksi untuk dikirim
                detection_info = {
                    "label": class_name,
                    "confidence": float(conf),
                    "midpoint_x": cx,
                    "midpoint_y": cy,
                    "steering_angle": int(90 + (cx - frame.shape[1]/2) * 0.1)
                }
                # Hanya kirim data deteksi pertama yang paling jelas
                break 
    
    # --- Kirim Data ke GCS Web via MQTT ---
    # 1. Kirim Frame Video
    _, buffer = cv2.imencode('.jpg', frame)
    frame_str = base64.b64encode(buffer).decode('utf-8')
    mqtt_client.publish(MQTT_VIDEO_TOPIC, frame_str)

    # 2. Kirim Info Deteksi (jika ada)
    if detection_info:
        mqtt_client.publish(MQTT_DETECTION_TOPIC, json.dumps(detection_info))

    # Tampilkan jendela lokal untuk debugging
    cv2.imshow("Pengujian AI Lokal (Tekan 'q' untuk keluar)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    time.sleep(0.05) # Batasi frame rate

cap.release()
cv2.destroyAllWindows()
mqtt_client.loop_stop()
print("👋 Skrip dihentikan.")
