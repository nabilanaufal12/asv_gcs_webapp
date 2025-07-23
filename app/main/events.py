import paho.mqtt.client as mqtt
import json
import cv2
import base64
import random
import numpy as np
from flask import request
from flask_login import current_user
from app import socketio, db
from app.models import Waypoint
from datetime import datetime

# --- Konfigurasi ---
MQTT_BROKER_URL = "broker.hivemq.com"
MQTT_BROKER_PORT = 1883
MQTT_TELEMETRY_TOPIC = "asv/telemetry"
MQTT_COMMAND_TOPIC = "asv/commands"

# --- State Server ---
vehicle_mode = "Manual"
mission_status = "Idle"
video_stream_active = True
video_task = None
pid_graph_task = None

# --- Fungsi Helper untuk Logging ---
def log_activity(message, level='info'):
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = {"timestamp": timestamp, "message": message, "level": level}
    socketio.emit('new_log_entry', log_entry)

# --- Inisialisasi MQTT Client & Callbacks ---
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="gcs_webapp_server")
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Koneksi ke MQTT Broker berhasil.")
        client.subscribe(MQTT_TELEMETRY_TOPIC)
        log_activity("Terhubung ke MQTT Broker.", "success")
    else:
        print(f"Koneksi ke MQTT gagal, kode: {rc}")
        log_activity(f"Gagal terhubung ke MQTT Broker (kode: {rc}).", "error")
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        socketio.emit('update_telemetry', data)
    except Exception as e:
        print(f"Terjadi error saat memproses pesan telemetri: {e}")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
try:
    mqtt_client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT, 60)
    mqtt_client.loop_start()
except Exception as e:
    print(f"Tidak dapat terhubung ke MQTT Broker: {e}")
    log_activity("Gagal inisiasi koneksi ke MQTT Broker.", "error")

# --- Fungsi Background Tasks ---
def stream_video():
    """Menangkap video dari webcam, menggambar overlay, dan menyiarkannya."""
    global video_task
    print("Memulai video stream dengan overlay...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Tidak bisa membuka kamera.")
        log_activity("Gagal membuka kamera.", "error")
        video_task = None # Reset task jika gagal
        return
        
    frame_count = 0
    box_x, box_y, midpoint_x = 0, 0, 0
    box_w, box_h = 80, 80

    while video_stream_active:
        success, frame = cap.read()
        if not success: break
        
        h, w, _ = frame.shape
        # ... (Logika menggambar overlay tidak berubah) ...
        if frame_count % 30 == 0: 
            box_x = random.randint(0, w - box_w)
            box_y = random.randint(int(h/4), h - box_h - 60)
            midpoint_x = box_x + box_w // 2
        cv2.rectangle(frame, (box_x, box_y), (box_x + box_w, box_y + box_h), (0, 255, 0), 2)
        cv2.putText(frame, 'Green Buoy', (box_x, box_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        detection_info = {
            "label": "green_buoy",
            "confidence": round(random.uniform(0.85, 0.99), 2),
            "midpoint_x": midpoint_x,
            "midpoint_y": box_y + box_h // 2,
            "steering_angle": int(90 + (midpoint_x - w/2) * 0.1)
        }
        socketio.emit('update_detection_info', detection_info)
        if frame_count % 60 == 0:
            log_activity(f"Deteksi: {detection_info['label']} (Conf: {detection_info['confidence']})")
        scale_y = h - 20
        cv2.line(frame, (20, scale_y), (w - 20, scale_y), (255, 255, 255), 2)
        for i in range(0, 181, 45):
            angle = i
            x_pos = int(20 + (w - 40) * (angle / 180.0))
            cv2.line(frame, (x_pos, scale_y - 10), (x_pos, scale_y), (255, 255, 255), 2)
            cv2.putText(frame, str(angle), (x_pos - 10, scale_y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        midpoint_angle = (midpoint_x / w) * 180.0
        indicator_x = int(20 + (w - 40) * (midpoint_angle / 180.0))
        pts = np.array([[indicator_x, scale_y - 5], [indicator_x - 5, scale_y - 10], [indicator_x + 5, scale_y - 10]], np.int32)
        cv2.fillPoly(frame, [pts], (0, 255, 255))
        
        _, buffer = cv2.imencode('.jpg', frame)
        frame_str = base64.b64encode(buffer).decode('utf-8')
        socketio.emit('update_video_frame', frame_str)
        
        frame_count += 1
        socketio.sleep(0.05)
    
    cap.release()
    socketio.emit('video_stream_status', {'active': False})
    print("Video stream dihentikan.")
    video_task = None # DIUBAH: Reset variabel task saat loop selesai

def stream_pid_data():
    # ... (Kode PID tidak berubah) ...
    print("Memulai stream data grafik PID...")
    setpoint = 100
    actual = 90
    while True:
        actual += (setpoint - actual) * 0.3 + random.uniform(-5, 5)
        pid_data = {"setpoint": setpoint, "actual": round(actual, 2)}
        socketio.emit('update_pid_graph', pid_data)
        socketio.sleep(1)

# --- Event Handlers (Socket.IO) ---
@socketio.on('connect')
def handle_connect(auth=None): # DIUBAH: Menerima argumen opsional
    global video_task, pid_graph_task
    if not current_user.is_authenticated: return
    
    log_activity(f"Pengguna '{current_user.username}' terhubung.", "success")
    
    # Kirim data persisten dari database
    user_waypoints = [wp.to_dict() for wp in current_user.waypoints.order_by(Waypoint.order).all()]
    socketio.emit('update_waypoints', user_waypoints, room=request.sid)
    socketio.emit('update_pid_gains', current_user.get_pid_gains(), room=request.sid)
    socketio.emit('update_servo_limits', current_user.get_servo_limits(), room=request.sid)
    
    # Kirim data sementara dari state server
    socketio.emit('update_vehicle_mode', vehicle_mode, room=request.sid)
    socketio.emit('update_mission_status', mission_status, room=request.sid)
    socketio.emit('video_stream_status', {'active': video_stream_active}, room=request.sid)
    
    # DIUBAH: Logika memulai task disederhanakan
    if video_stream_active and video_task is None:
        video_task = socketio.start_background_task(target=stream_video)
    if pid_graph_task is None:
        pid_graph_task = socketio.start_background_task(target=stream_pid_data)

@socketio.on('disconnect')
def handle_disconnect():
    log_activity(f"Pengguna terputus.", "warning")

# ... (Event handler lain tidak berubah) ...
@socketio.on('add_waypoint')
def handle_add_waypoint(data):
    if not current_user.is_authenticated: return
    try:
        last_order = db.session.query(db.func.max(Waypoint.order)).filter_by(user_id=current_user.id).scalar() or -1
        new_wp = Waypoint(lat=float(data['lat']), lon=float(data['lon']), order=last_order + 1, author=current_user)
        db.session.add(new_wp)
        db.session.commit()
        user_waypoints = [wp.to_dict() for wp in current_user.waypoints.order_by(Waypoint.order).all()]
        socketio.emit('update_waypoints', user_waypoints)
        socketio.emit('show_notification', {'message': 'Waypoint berhasil ditambahkan!', 'type': 'success'}, room=request.sid)
    except (ValueError, KeyError):
        db.session.rollback()
        socketio.emit('show_notification', {'message': 'Gagal menambahkan waypoint.', 'type': 'error'}, room=request.sid)

@socketio.on('delete_waypoint')
def handle_delete_waypoint(index):
    if not current_user.is_authenticated: return
    try:
        wp_to_delete = current_user.waypoints.filter_by(order=index).first()
        if wp_to_delete:
            db.session.delete(wp_to_delete)
            remaining_wps = current_user.waypoints.filter(Waypoint.order > index).order_by(Waypoint.order).all()
            for wp in remaining_wps:
                wp.order -= 1
            db.session.commit()
        user_waypoints = [wp.to_dict() for wp in current_user.waypoints.order_by(Waypoint.order).all()]
        socketio.emit('update_waypoints', user_waypoints)
        socketio.emit('show_notification', {'message': 'Waypoint berhasil dihapus.', 'type': 'info'}, room=request.sid)
    except Exception:
        db.session.rollback()
        socketio.emit('show_notification', {'message': 'Gagal menghapus waypoint.', 'type': 'error'}, room=request.sid)

@socketio.on('set_vehicle_mode')
def handle_set_vehicle_mode():
    global vehicle_mode, mission_status
    vehicle_mode = "Auto" if vehicle_mode == "Manual" else "Manual"
    if vehicle_mode == "Manual":
        mission_status = "Idle"
        socketio.emit('update_mission_status', mission_status)
        mqtt_client.publish(MQTT_COMMAND_TOPIC, json.dumps({"command": "reset_mission"}))
    socketio.emit('update_vehicle_mode', vehicle_mode)
    mqtt_client.publish(MQTT_COMMAND_TOPIC, json.dumps({"command": "set_mode", "mode": vehicle_mode}))
    log_activity(f"Mode diubah ke {vehicle_mode}.")

@socketio.on('emergency_stop')
def handle_emergency_stop():
    global vehicle_mode, mission_status
    vehicle_mode = "Manual"
    mission_status = "Idle"
    socketio.emit('update_vehicle_mode', vehicle_mode)
    socketio.emit('update_mission_status', mission_status)
    mqtt_client.publish(MQTT_COMMAND_TOPIC, json.dumps({"command": "emergency_stop"}))
    socketio.emit('show_notification', {'message': 'EMERGENCY STOP DIAKTIFKAN!', 'type': 'error'}, room=request.sid)
    log_activity("EMERGENCY STOP DIAKTIFKAN!", "error")

@socketio.on('manual_control')
def handle_manual_control(data):
    command = {"command": "manual_move", "direction": data.get('direction')}
    mqtt_client.publish(MQTT_COMMAND_TOPIC, json.dumps(command))

@socketio.on('set_speed')
def handle_set_speed(data):
    command = {"command": "set_speed", "speed": data.get('speed')}
    mqtt_client.publish(MQTT_COMMAND_TOPIC, json.dumps(command))

@socketio.on('mission_command')
def handle_mission_command(data):
    global mission_status
    if not current_user.is_authenticated or vehicle_mode != "Auto": return
    command = data.get('command')
    if command == 'start_pause':
        if mission_status in ['Idle', 'Paused']:
            mission_status = 'Running'
            waypoints = [wp.to_dict() for wp in current_user.waypoints.order_by(Waypoint.order).all()]
            mqtt_client.publish(MQTT_COMMAND_TOPIC, json.dumps({"command": "start_mission", "waypoints": waypoints}))
            log_activity("Misi otonom dimulai.")
        elif mission_status == 'Running':
            mission_status = 'Paused'
            mqtt_client.publish(MQTT_COMMAND_TOPIC, json.dumps({"command": "pause_mission"}))
            log_activity("Misi otonom dijeda.", "warning")
    elif command == 'reset':
        mission_status = 'Idle'
        mqtt_client.publish(MQTT_COMMAND_TOPIC, json.dumps({"command": "reset_mission"}))
        log_activity("Misi otonom direset.")
    socketio.emit('update_mission_status', mission_status)

@socketio.on('set_auto_speed')
def handle_set_auto_speed(data):
    if not current_user.is_authenticated or vehicle_mode != "Auto": return
    command = {"command": "set_auto_speed", "speed": data.get('speed')}
    mqtt_client.publish(MQTT_COMMAND_TOPIC, json.dumps(command))

@socketio.on('set_pid_gains')
def handle_set_pid_gains(data):
    if not current_user.is_authenticated: return
    try:
        current_user.pid_kp = float(data['kp'])
        current_user.pid_ki = float(data['ki'])
        current_user.pid_kd = float(data['kd'])
        db.session.commit()
        gains = current_user.get_pid_gains()
        mqtt_client.publish(MQTT_COMMAND_TOPIC, json.dumps({"command": "set_pid", "gains": gains}))
        socketio.emit('update_pid_gains', gains)
        socketio.emit('show_notification', {'message': 'Pengaturan PID berhasil disimpan!', 'type': 'success'}, room=request.sid)
        log_activity(f"PID disimpan: Kp={gains['kp']}, Ki={gains['ki']}, Kd={gains['kd']}")
    except (ValueError, KeyError):
        db.session.rollback()
        socketio.emit('show_notification', {'message': 'Gagal menyimpan PID.', 'type': 'error'}, room=request.sid)

@socketio.on('set_servo_limits')
def handle_set_servo_limits(data):
    if not current_user.is_authenticated: return
    try:
        current_user.servo_min = int(data['min'])
        current_user.servo_max = int(data['max'])
        db.session.commit()
        limits = current_user.get_servo_limits()
        mqtt_client.publish(MQTT_COMMAND_TOPIC, json.dumps({"command": "set_servo_limits", "limits": limits}))
        socketio.emit('update_servo_limits', limits)
        socketio.emit('show_notification', {'message': 'Batas servo berhasil disimpan!', 'type': 'success'}, room=request.sid)
        log_activity(f"Batas servo disimpan: Min={limits['min']}, Max={limits['max']}")
    except (ValueError, KeyError):
        db.session.rollback()
        socketio.emit('show_notification', {'message': 'Gagal menyimpan batas servo.', 'type': 'error'}, room=request.sid)

@socketio.on('take_snapshot')
def handle_take_snapshot():
    if not current_user.is_authenticated: return
    mqtt_client.publish(MQTT_COMMAND_TOPIC, json.dumps({"command": "take_snapshot"}))
    socketio.emit('show_notification', {'message': 'Perintah snapshot terkirim!', 'type': 'info'}, room=request.sid)
    log_activity("Perintah snapshot terkirim.")

@socketio.on('toggle_video_stream')
def handle_toggle_video_stream():
    """Menghidupkan atau mematikan background task video stream."""
    global video_stream_active, video_task
    if not current_user.is_authenticated: return
    
    video_stream_active = not video_stream_active
    
    if video_stream_active:
        log_activity("Perintah memulai video stream.")
        # DIUBAH: Logika memulai task disederhanakan
        if video_task is None:
            video_task = socketio.start_background_task(target=stream_video)
            socketio.emit('video_stream_status', {'active': True})
    else:
        log_activity("Perintah menghentikan video stream.")
        # Loop di dalam stream_video akan berhenti, dan task akan direset ke None
