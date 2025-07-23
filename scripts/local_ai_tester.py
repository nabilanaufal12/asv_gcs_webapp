import cv2
import torch
import numpy as np
import pathlib
import json
import base64
import paho.mqtt.client as mqtt
import time
import sys
import os

# --- Konfigurasi MQTT ---
MQTT_BROKER_URL = "broker.hivemq.com"
MQTT_BROKER_PORT = 1883
MQTT_VIDEO_TOPIC = "asv/video_stream"
MQTT_DETECTION_TOPIC = "asv/detection_info"

# --- Inisialisasi MQTT Client ---
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="local_ai_tester")
def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("✅ Berhasil terhubung ke MQTT Broker.")
    else:
        print(f"❌ Gagal terhubung ke MQTT, kode: {rc}")
mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT)
mqtt_client.loop_start()

# --- Menambahkan Path Proyek untuk Impor YOLOv5 ---
# Ini penting agar Python bisa menemukan folder 'models' dan 'utils'
FILE = pathlib.Path(__file__).resolve()
ROOT = FILE.parents[1]  # Naik satu level dari /scripts ke /asv_gcs_webapp
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
os.chdir(ROOT) # Mengubah direktori kerja ke folder utama

# --- Impor YOLOv5 ---
from models.common import DetectMultiBackend
from utils.general import non_max_suppression, scale_boxes
from utils.torch_utils import select_device
from utils.plots import Annotator, colors

# --- Load Model AI ---
try:
    model_path = 'best.pt'
    device = select_device('')
    model = DetectMultiBackend(model_path, device=device, dnn=False)
    stride, names = model.stride, model.names
    model.warmup(imgsz=(1, 3, 640, 640))
    print("✅ Model AI YOLOv5 'best.pt' berhasil dimuat.")
except Exception as e:
    print(f"❌ Gagal memuat model 'best.pt'. Pastikan file ada di folder utama dan folder 'models' & 'utils' sudah disalin. Error: {e}")
    exit()

# --- Buka Webcam ---
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

    # --- Logika Deteksi AI (YOLOv5) ---
    img = cv2.resize(frame, (640, 640))
    img_tensor = torch.from_numpy(img).to(device)
    img_tensor = img_tensor.permute(2, 0, 1).float() / 255.0
    if img_tensor.ndimension() == 3:
        img_tensor = img_tensor.unsqueeze(0)

    with torch.no_grad():
        pred = model(img_tensor, augment=False, visualize=False)
        pred = non_max_suppression(pred, conf_thres=0.4, iou_thres=0.45)

    detection_info = None
    annotator = Annotator(frame, line_width=2, example=str(names))

    for det in pred:
        if len(det):
            det[:, :4] = scale_boxes(img_tensor.shape[2:], det[:, :4], frame.shape).round()

            for *xyxy, conf, cls in det:
                class_id = int(cls)
                class_name = names[class_id]
                confidence = float(conf)
                
                # Gambar kotak di frame menggunakan annotator
                label = f'{class_name} {confidence:.2f}'
                annotator.box_label(xyxy, label, color=colors(class_id, True))

                # Siapkan data deteksi untuk dikirim
                coords = torch.tensor(xyxy).tolist()
                x1, y1, x2, y2 = map(int, coords)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                detection_info = {
                    "label": class_name,
                    "confidence": confidence,
                    "midpoint_x": cx,
                    "midpoint_y": cy,
                    "steering_angle": int(90 + (cx - frame.shape[1]/2) * 0.1)
                }
                break # Hanya proses deteksi pertama

    annotated_frame = annotator.result()
    
    # --- Kirim Data ke GCS Web via MQTT ---
    _, buffer = cv2.imencode('.jpg', annotated_frame)
    frame_str = base64.b64encode(buffer).decode('utf-8')
    mqtt_client.publish(MQTT_VIDEO_TOPIC, frame_str)

    if detection_info:
        mqtt_client.publish(MQTT_DETECTION_TOPIC, json.dumps(detection_info))

    # Tampilkan jendela lokal
    cv2.imshow("Pengujian AI Lokal (Tekan 'q' untuk keluar)", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    time.sleep(0.05)

cap.release()
cv2.destroyAllWindows()
mqtt_client.loop_stop()
print("👋 Skrip dihentikan.")
