import os
import time
import requests
import cv2
import string
import secrets
from datetime import datetime, timezone, timedelta
import threading
import numpy as np
import base64

# Arduino App Lab components
from arduino.app_utils import App
try:
    from arduino.app_utils import Bridge
except ImportError:
    Bridge = None

from arduino.app_bricks.web_ui import WebUI

# Edge Impulse Linux Runner
from edge_impulse_linux.image import ImageImpulseRunner

# ==========================================
# ⚙️ USER CONFIGURATION (ส่วนตั้งค่าสำหรับผู้ใช้งาน)
# 🌟 แก้จุดนี้จุดเดียว! หน้าเว็บแดชบอร์ด, สไลเดอร์, กล่อง HUD วิดีโอสด และ Telegram จะเปลี่ยนตามทั้งหมดอัตโนมัติ
# ==========================================
# โหมดกล้อง: ตั้งค่า "WEBCAM" สำหรับกล้อง USB ทั่วไป, หรือ "MOBILE" สำหรับ Arduino IoT Remote App
INPUT_MODE = "WEBCAM"  

# ----------------------------------------------------
# คีย์เวิร์ดตรวจจับของโมเดล AI (Single Source of Truth)
# ----------------------------------------------------
# ค่าตั้งต้น: เป็น "fire" (ไฟ) เป็นค่าเริ่มต้นมาตรฐาน
# หากในอนาคตต้องการเปลี่ยนไปตรวจจับวัตถุชนิดอื่น ให้แก้ไขที่ 4 ตัวแปรนี้ (ระบบทั้งหมดจะเปลี่ยนตามทันที):
TARGET_LABEL = "fire"              # Keyword จากโมเดล Edge Impulse เช่น "fire", "person", "smoke", "helmet", "car"
TARGET_DISPLAY_NAME = "Fire"       # ชื่อแสดงผล เช่น "Fire", "Person", "Safety Helmet"
TARGET_ICON = "🔥"                 # ไอคอนแสดงผล เช่น "🔥", "👤", "⛑️", "🚗", "🎯"
APP_TITLE = "Fire & Smoke AI"      # ชื่อหัวเว็บ/ระบบ เช่น "Fire & Smoke AI", "Person AI Guard"

# ----------------------------------------------------
# การตั้งค่าบอท Telegram (Telegram Bot Configuration)
# ----------------------------------------------------
TELEGRAM_TOKEN = "8859583029:AAGrJxWYDnmPtRaIlu5MBHIFYvFV--4nmXI"
TELEGRAM_CHAT_ID = "7246017877"

# ----------------------------------------------------
# เกณฑ์ตรวจจับเริ่มต้น (Default Thresholds)
# ----------------------------------------------------
DEFAULT_FIRE_THRESHOLD = 80.0     # 80% AI Confidence
DEFAULT_SMOKE_THRESHOLD = 600.0   # 600 ppm (Parts Per Million)

# ระยะเวลาหน่วงป้องกันการส่ง Telegram ซ้ำซ้อน (วินาที)
TELEGRAM_COOLDOWN = 20

# ชื่อไฟล์โมเดล Edge Impulse (.eim)
MODEL_PATH = "wildfire-dt-model.eim"

# พิกัดตำแหน่งติดตั้ง (Latitude & Longitude สำหรับสร้างลิงก์ Google Maps ใน Telegram)
LATITUDE = "-"
LONGITUDE = "-"

# ==========================================
# GLOBAL STATE
# ==========================================
# Fallback Defaults
if not TARGET_ICON:
    TARGET_ICON = "🔥" if TARGET_DISPLAY_NAME.lower() == "fire" else "🎯"
if not APP_TITLE:
    APP_TITLE = "Fire & Smoke AI" if TARGET_DISPLAY_NAME.lower() == "fire" else f"{TARGET_DISPLAY_NAME} Detection AI"

current_fire_threshold = DEFAULT_FIRE_THRESHOLD
current_smoke_threshold = DEFAULT_SMOKE_THRESHOLD

last_telegram_time = 0
telegram_send_count = 0
telegram_last_status = "Standby"
telegram_history = []
latest_detections = {
    "fire": 0.0,
    "smoke": 50.0,
    "smoke_ppm": 50.0,
    "mq2_raw": 0,
    "temperature": 25.0,
    "humidity": 50.0,
    "target_label": TARGET_LABEL,
    "target_name": TARGET_DISPLAY_NAME,
    "target_icon": TARGET_ICON,
    "app_title": APP_TITLE
}

# MQ-2 State (Pin A0)
current_mq2_raw = 0
current_smoke_ppm = 50.0
mq2_lock = threading.Lock()

# DHT-22 State (Pin D2)
current_temperature = 25.0
current_humidity = 50.0
dht_lock = threading.Lock()

ui = WebUI()

# Initialize AI Model
runner = None
model_info = None
try:
    import stat
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    actual_model_path = os.path.join(BASE_DIR, MODEL_PATH)
    if os.path.exists(actual_model_path):
        # Automatically ensure executable permissions (chmod +x)
        try:
            current_mode = os.stat(actual_model_path).st_mode
            os.chmod(actual_model_path, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH | stat.S_IRUSR | stat.S_IWUSR)
            print(f"Ensured executable permissions for {actual_model_path}")
        except Exception as perm_e:
            print(f"Warning setting chmod on model: {perm_e}")

        runner_candidate = ImageImpulseRunner(actual_model_path)
        model_info = runner_candidate.init()
        runner = runner_candidate
        print(f"Edge Impulse model initialized successfully from: {actual_model_path}")
        print("Model info:", model_info)
    else:
        print(f"Warning: Model file not found at {actual_model_path}")
except Exception as e:
    runner = None
    model_info = None
    print(f"Error initializing Edge Impulse model: {e}")

# ==========================================
# HARDWARE BRIDGE: SERVO (PIN 9)
# ==========================================
class ServoController:
    """
    Non-blocking Servo controller on Pin 9:
    - In STANDBY: Detached, zero PWM, zero jittering.
    - When Fire >= threshold:
      1. Attach & Rotate to 90 degrees.
      2. Hold for 10 seconds.
      3. Rotate back to 0 degrees.
      4. Wait 1.5s to reach 0, then Detach (cuts PWM completely to prevent twitching).
      5. Cooldown for 60 seconds (1 minute).
      6. If fire persists after cooldown, re-triggers automatically.
    """
    def __init__(self):
        self.state = "STANDBY"  # STANDBY | ACTIVE | COOLDOWN
        self.angle = 0
        self.lock = threading.Lock()
        self.cooldown_until = 0

    def get_status(self):
        with self.lock:
            now = time.time()
            rem = max(0, int(self.cooldown_until - now)) if self.state == "COOLDOWN" else 0
            return {
                "state": self.state,
                "angle": self.angle,
                "remaining_cooldown": rem
            }

    def set_hardware_angle(self, angle: int):
        self.angle = angle
        if Bridge:
            try:
                Bridge.call("set_servo", int(angle))
            except Exception as e:
                print(f"[Servo Bridge Error] Failed to set angle to {angle}: {e}")
        else:
            print(f"[Servo Sim] Set angle to {angle}°")

    def detach_hardware_servo(self):
        if Bridge:
            try:
                Bridge.call("detach_servo")
            except Exception as e:
                print(f"[Servo Bridge Error] Failed to detach: {e}")
        else:
            print("[Servo Sim] Detached (Zero PWM)")

    def trigger(self):
        with self.lock:
            if self.state != "STANDBY":
                return False  # Already active or cooling down
            self.state = "ACTIVE"
        
        # Launch asynchronous worker thread
        threading.Thread(target=self._run_servo_cycle, daemon=True).start()
        return True

    def _run_servo_cycle(self):
        try:
            print("[Servo] Fire detected! Attaching & rotating to 90 degrees...")
            self.set_hardware_angle(90)
            update_servo_ui_status()

            # Hold for 10 seconds (non-blocking to video/web UI)
            time.sleep(10)

            print("[Servo] 10s elapsed. Returning to 0 degrees...")
            self.set_hardware_angle(0)

            # Give motor 1.5 seconds to physically reach 0° position
            time.sleep(1.5)

            # Cut PWM signal completely to eliminate any jittering/buzzing!
            print("[Servo] Detaching servo to stop all PWM jitter...")
            self.detach_hardware_servo()

            # Start 1-minute (60 seconds) cooldown
            with self.lock:
                self.state = "COOLDOWN"
                self.cooldown_until = time.time() + 60.0
            print("[Servo] Cooldown active for 60 seconds...")
            update_servo_ui_status()

            # Countdown during cooldown
            while time.time() < self.cooldown_until:
                time.sleep(1)
                update_servo_ui_status()

            # Cooldown completed
            with self.lock:
                self.state = "STANDBY"
            print("[Servo] Cooldown complete. Ready on STANDBY.")
            update_servo_ui_status()

            # If fire is STILL detected after cooldown, repeat!
            if latest_detections.get("fire", 0.0) >= current_fire_threshold:
                print("[Servo] Fire is STILL detected! Re-triggering servo cycle...")
                self.trigger()

        except Exception as e:
            print(f"[Servo Exception] {e}")
            with self.lock:
                self.state = "STANDBY"
            self.detach_hardware_servo()
            update_servo_ui_status()

servo_controller = ServoController()

def update_servo_ui_status():
    ui.send_message("servo_status", servo_controller.get_status())

# ==========================================
# MQ-2 SENSOR: PPM CALCULATION (PIN A0)
# ==========================================
def raw_to_smoke_ppm(raw_val: int) -> float:
    """
    Convert MQ-2 ADC reading to estimated Smoke PPM (Parts Per Million).
    MQ-2 standard smoke range: 300 - 10,000 ppm.
    Clean air baseline: ~50 - 150 ppm.
    """
    try:
        normalized_raw = float(raw_val)
        if normalized_raw > 1023:
            normalized_raw = (normalized_raw / 4095.0) * 1023.0
        
        if normalized_raw <= 20:
            return 50.0  # Clean air floor
        
        # Log-exponential response curve for MQ-2 smoke sensor
        # ~100 raw -> ~110 ppm (Clean air)
        # ~300 raw -> ~470 ppm (Mild smoke)
        # ~400 raw -> ~740 ppm (Smoke threshold trigger)
        # ~600 raw -> ~1440 ppm (Dense smoke)
        # ~800 raw -> ~2320 ppm (Heavy fire smoke)
        ppm = 50.0 * (1.0 + (normalized_raw / 80.0) ** 1.8)
        return min(10000.0, max(50.0, round(ppm, 1)))
    except Exception:
        return 50.0

def on_mq2_stream_data(raw_val):
    global current_mq2_raw, current_smoke_ppm
    try:
        with mq2_lock:
            current_mq2_raw = int(raw_val)
            current_smoke_ppm = raw_to_smoke_ppm(current_mq2_raw)
    except Exception as e:
        print(f"Error handling mq2_data: {e}")

def on_dht_temp_data(raw_val):
    global current_temperature
    try:
        with dht_lock:
            current_temperature = round(float(raw_val), 1)
    except Exception as e:
        print(f"Error handling dht_temp: {e}")

def on_dht_hum_data(raw_val):
    global current_humidity
    try:
        with dht_lock:
            current_humidity = round(float(raw_val), 1)
    except Exception as e:
        print(f"Error handling dht_hum: {e}")

if Bridge:
    try:
        Bridge.provide("mq2_data", on_mq2_stream_data)
        print("Bridge RPC 'mq2_data' handler registered.")
    except Exception as e:
        print(f"Error registering 'mq2_data' handler with Bridge: {e}")

    try:
        Bridge.provide("dht_temp", on_dht_temp_data)
        Bridge.provide("dht_hum", on_dht_hum_data)
        print("Bridge RPC DHT22 handlers registered.")
    except Exception as e:
        print(f"Error registering DHT22 handlers with Bridge: {e}")

# Periodic fallback poller for Sensors (MQ-2 and DHT-22)
def sensor_polling_worker():
    while True:
        if Bridge:
            try:
                val = Bridge.call("read_mq2")
                if val is not None:
                    on_mq2_stream_data(val)
            except Exception:
                pass

            try:
                t = Bridge.call("read_dht_temp")
                if t is not None:
                    on_dht_temp_data(t)
                h = Bridge.call("read_dht_hum")
                if h is not None:
                    on_dht_hum_data(h)
            except Exception:
                pass
        time.sleep(1.0)

threading.Thread(target=sensor_polling_worker, daemon=True).start()

# ==========================================
# TELEGRAM NOTIFICATION
# ==========================================
telegram_lock = threading.Lock()

def trigger_telegram_alert(image_frame, fire_conf, smoke_ppm, mq2_raw, reason="Alert"):
    global last_telegram_time
    
    with telegram_lock:
        current_time = time.time()
        if current_time - last_telegram_time < TELEGRAM_COOLDOWN:
            return False
        last_telegram_time = current_time
        
    threading.Thread(
        target=send_telegram_alert,
        args=(image_frame, fire_conf, smoke_ppm, mq2_raw, reason),
        daemon=True
    ).start()
    return True

def send_telegram_alert(image_frame, fire_conf, smoke_ppm, mq2_raw, reason):
    global telegram_send_count, telegram_last_status, telegram_history
    
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        telegram_last_status = "Failed (Invalid Token)"
        update_telegram_ui_status()
        return

    # Encode frame to JPEG
    ret, buffer = cv2.imencode('.jpg', image_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not ret:
        return
    
    # Bangkok timezone (UTC+7)
    tz_bangkok = timezone(timedelta(hours=7))
    now_bangkok = datetime.now(tz_bangkok)
    
    timestamp_display = now_bangkok.strftime("%d/%m/%Y - %H:%M:%S")
    timestamp_iso = now_bangkok.isoformat()

    with dht_lock:
        temp_val = current_temperature
        hum_val = current_humidity

    target_icon = TARGET_ICON if TARGET_ICON else ("🔥" if TARGET_DISPLAY_NAME.lower() == "fire" else "🎯")
    caption = (f"🚨 ALARM: {reason} Detected! 🚨\n"
               f"{target_icon} {TARGET_DISPLAY_NAME} Level: {fire_conf:.1f}% (Threshold: {current_fire_threshold:.0f}%)\n"
               f"💨 Smoke Level: {smoke_ppm:.1f} ppm (Threshold: {current_smoke_threshold:.0f} ppm)\n"
               f"🌡️ Temperature: {temp_val:.1f} °C\n"
               f"💧 Humidity: {hum_val:.1f} %\n"
               f"📟 Sensor Raw (A0): {mq2_raw}\n"
               f"⚙️ Servo Status: {servo_controller.state}\n"
               f"📍 Location: {LATITUDE}, {LONGITUDE}\n"
               f"🗺️ Maps: https://www.google.com/maps?q={LATITUDE},{LONGITUDE}\n"
               f"🕒 Time: {timestamp_display}")

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        files = {'photo': ('alert.jpg', buffer.tobytes(), 'image/jpeg')}
        data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
        
        response = requests.post(url, files=files, data=data, timeout=10)
        
        if response.status_code == 200:
            telegram_send_count += 1
            telegram_last_status = "Success"
            telegram_history.insert(0, timestamp_iso)
            if len(telegram_history) > 5:
                telegram_history.pop()
        else:
            telegram_last_status = f"Failed ({response.status_code})"
            
    except Exception as e:
        telegram_last_status = f"Error: {str(e)}"
        
    update_telegram_ui_status()

def update_telegram_ui_status():
    ui.send_message("telegram_status", {
        "count": telegram_send_count,
        "last_status": telegram_last_status,
        "history": telegram_history
    })

# ==========================================
# UI CONTROLS & EVENTS
# ==========================================
ui.on_message("override_fire_th", lambda sid, threshold: update_fire_threshold(threshold))
ui.on_message("override_smoke_th", lambda sid, threshold: update_smoke_threshold(threshold))

def update_fire_threshold(threshold):
    global current_fire_threshold
    try:
        current_fire_threshold = float(threshold)
        print(f"Fire Camera threshold updated to: {current_fire_threshold}%")
    except ValueError:
        pass

def update_smoke_threshold(threshold):
    global current_smoke_threshold
    try:
        current_smoke_threshold = float(threshold)
        print(f"Smoke Sensor threshold updated to: {current_smoke_threshold} ppm")
    except ValueError:
        pass

# ==========================================
# VIDEO PROCESSING & AI INFERENCE
# ==========================================
def process_frame(frame):
    global latest_detections
    
    if frame is None or frame.size == 0 or frame.shape[0] == 0 or frame.shape[1] == 0:
        return

    # Resize frame for UI display
    ui_frame = cv2.resize(frame, (640, 480))
    
    fire_conf = 0.0
    
    # AI Classification on USB webcam frame
    if runner and model_info:
        try:
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            features, cropped = runner.get_features_from_image(img_rgb)
            res = runner.classify(features)
            
            if "bounding_boxes" in res.get("result", {}):
                for bb in res["result"]["bounding_boxes"]:
                    label = bb.get('label', '')
                    conf = bb.get('value', 0.0) * 100.0
                    x, y, w, h = int(bb['x']), int(bb['y']), int(bb['width']), int(bb['height'])
                    
                    if label.lower() == TARGET_LABEL.lower():
                        fire_conf = max(fire_conf, conf)
                        color = (0, 0, 255) # BGR Red
                        if conf > 20.0:
                            cv2.rectangle(ui_frame, (x, y), (x + w, y + h), color, 2)
                            cv2.putText(ui_frame, f"{TARGET_DISPLAY_NAME} {conf:.1f}%", (x, max(20, y - 10)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        except Exception as e:
            print(f"Inference error: {e}")

    # Smoke level is calculated directly in ppm from MQ-2 on A0
    with mq2_lock:
        smoke_ppm = current_smoke_ppm
        mq2_val = current_mq2_raw

    with dht_lock:
        temp_val = current_temperature
        hum_val = current_humidity

    latest_detections["fire"] = fire_conf
    latest_detections["smoke"] = smoke_ppm
    latest_detections["smoke_ppm"] = smoke_ppm
    latest_detections["mq2_raw"] = mq2_val
    latest_detections["temperature"] = temp_val
    latest_detections["humidity"] = hum_val
    latest_detections["target_label"] = TARGET_LABEL
    latest_detections["target_name"] = TARGET_DISPLAY_NAME
    
    # Overlay HUD telemetry on the frame
    hud_bg_color = (0, 0, 0)
    cv2.rectangle(ui_frame, (10, 10), (350, 115), hud_bg_color, -1)
    cv2.rectangle(ui_frame, (10, 10), (350, 115), (100, 100, 100), 1)

    fire_color = (0, 0, 255) if fire_conf >= current_fire_threshold else (0, 255, 0)
    smoke_color = (0, 165, 255) if smoke_ppm >= current_smoke_threshold else (200, 200, 200)

    cv2.putText(ui_frame, f"{TARGET_DISPLAY_NAME} (AI): {fire_conf:.1f}% (Th: {current_fire_threshold:.0f}%)", (20, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.52, fire_color, 2)
    cv2.putText(ui_frame, f"Smoke (MQ2): {smoke_ppm:.1f} ppm (Th: {current_smoke_threshold:.0f})", (20, 54),
                cv2.FONT_HERSHEY_SIMPLEX, 0.50, smoke_color, 2)
    cv2.putText(ui_frame, f"DHT22 (D2): {temp_val:.1f}C | {hum_val:.1f}%", (20, 76),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 230, 255), 1)
    
    servo_st = servo_controller.get_status()
    servo_txt = f"Servo (Pin 9): {servo_st['state']}"
    if servo_st['state'] == "COOLDOWN":
        servo_txt += f" ({servo_st['remaining_cooldown']}s)"
    elif servo_st['state'] == "ACTIVE":
        servo_txt += f" (90 deg)"
    cv2.putText(ui_frame, servo_txt, (20, 98),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 255), 1)

    # Send telemetry to Web UI
    ui.send_message("detection", latest_detections)
    update_servo_ui_status()
    
    # Trigger Conditions
    is_fire = (fire_conf >= current_fire_threshold)
    is_smoke = (smoke_ppm >= current_smoke_threshold)

    if is_fire or is_smoke:
        reason = f"{TARGET_DISPLAY_NAME} & Smoke" if (is_fire and is_smoke) else (TARGET_DISPLAY_NAME if is_fire else "Smoke (MQ-2)")
        trigger_telegram_alert(ui_frame.copy(), fire_conf, smoke_ppm, mq2_val, reason)
        
    # Servo only triggers when FIRE threshold is exceeded
    if is_fire:
        servo_controller.trigger()
        
    # Send frame to UI (Base64 JPEG)
    ret, buffer = cv2.imencode('.jpg', ui_frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
    if ret:
        b64_img = base64.b64encode(buffer).decode('utf-8')
        ui.send_message("video_frame", f"data:image/jpeg;base64,{b64_img}")

# ==========================================
# CAMERA LOOP
# ==========================================
def open_usb_camera():
    """Attempt to open USB webcam at index 2, 0, 1."""
    for idx in [2, 0, 1]:
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"USB Webcam successfully opened on index {idx}")
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                return cap
            cap.release()
    print("Warning: Could not open USB Webcam on default indexes [2, 0, 1]")
    return None

def camera_loop():
    if INPUT_MODE == "WEBCAM":
        cap = None
        while True:
            if cap is None or not cap.isOpened():
                cap = open_usb_camera()
                if cap is None:
                    time.sleep(2)
                    continue

            ret, frame = cap.read()
            if ret and frame is not None:
                process_frame(frame)
            else:
                print("Failed to read frame from webcam, reconnecting...")
                cap.release()
                cap = None
                time.sleep(1)

            time.sleep(0.04)  # ~25 FPS
    else:
        pass

# ==========================================
# UI CONNECTION HANDLER
# ==========================================
def handle_ui_connect(sid):
    print(f"UI Client connected: {sid}")
    ui.send_message("welcome", {
        "mode": "WEBCAM",
        "fire_threshold": current_fire_threshold,
        "smoke_threshold": current_smoke_threshold,
        "target_label": TARGET_LABEL,
        "target_name": TARGET_DISPLAY_NAME,
        "target_icon": TARGET_ICON,
        "app_title": APP_TITLE,
        "temperature": current_temperature,
        "humidity": current_humidity
    })
    update_telegram_ui_status()
    update_servo_ui_status()

ui.on_connect(handle_ui_connect)

# Start Video Processing Thread
threading.Thread(target=camera_loop, daemon=True).start()

# Keep App Lab runtime running
App.run()
