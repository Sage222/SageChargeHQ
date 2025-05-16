import socketio
import urllib.parse
import requests
import datetime
import threading
import time
import tkinter as tk
from tkinter import ttk

# === CONFIG ===
TOKEN = "CHARGEHQTOKEN"
HA_URL = "http://homeassistant.local:8123"
HA_TOKEN = "HOMEASSISTTOKEN"
THROTTLE_INTERVAL = 15  # seconds

HA_HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

# === Global State ===
last_update_time = datetime.datetime.min
latest_data = None
lock = threading.Lock()
connection_status = "Disconnected"

# === Socket.IO Client ===
sio = socketio.Client()

@sio.event
def connect():
    global connection_status
    connection_status = "Connected to ChargeHQ"

@sio.event
def disconnect():
    global connection_status
    connection_status = "Disconnected"

@sio.event
def connect_error(data):
    global connection_status
    connection_status = f"Connection error: {data}"

@sio.on("site-state")
def handle_site_state(data):
    global latest_data
    with lock:
        latest_data = data

# === Home Assistant Communication ===
def send_to_home_assistant(entity_id, value):
    url = f"{HA_URL}/api/services/input_number/set_value"
    payload = {
        "entity_id": entity_id,
        "value": round(value, 2),
    }

    try:
        r = requests.post(url, headers=HA_HEADERS, json=payload, timeout=5)
        if r.status_code != 200:
            print(f"[ERROR] Failed to update {entity_id}: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"[ERROR] Failed to connect to HA: {e}")

# === Throttle Update Function ===
def throttled_update_loop(update_ui_callback):
    global last_update_time, latest_data
    while True:
        now = datetime.datetime.now()
        with lock:
            if latest_data and (now - last_update_time).total_seconds() >= THROTTLE_INTERVAL:
                try:
                    solar_kw = latest_data["powerFlows"]["pvKw"]
                    ev_kw = latest_data["powerFlows"]["evKw"]
                    battery_level = latest_data["teslaState"]["fields"]["battery_level"]

                    send_to_home_assistant("input_number.chargehq_solar_kw", solar_kw)
                    send_to_home_assistant("input_number.chargehq_ev_kw", ev_kw)
                    send_to_home_assistant("input_number.chargehq_battery", battery_level)

                    last_update_time = now
                    update_ui_callback(solar_kw, ev_kw, battery_level)
                    latest_data = None

                except KeyError as e:
                    print(f"[WARN] Missing key: {e}")
                except Exception as e:
                    print(f"[ERROR] Failed to process data: {e}")
        time.sleep(1)

# === GUI Setup ===
def start_gui():
    root = tk.Tk()
    root.title("ChargeHQ Monitor")
    root.geometry("320x220")
    root.resizable(False, False)

    style = ttk.Style()
    style.configure("TLabel", font=("Segoe UI", 12))

    label_title = ttk.Label(root, text="⚡ ChargeHQ Monitor", font=("Segoe UI", 16, "bold"))
    label_title.pack(pady=10)

    solar_var = tk.StringVar(value="🔆 Solar Power: -- kW")
    ev_var = tk.StringVar(value="🚗 EV Charging: -- kW")
    battery_var = tk.StringVar(value="🔋 Battery Level: --%")
    status_var = tk.StringVar(value="Status: Connecting...")

    ttk.Label(root, textvariable=solar_var).pack(pady=2)
    ttk.Label(root, textvariable=ev_var).pack(pady=2)
    ttk.Label(root, textvariable=battery_var).pack(pady=2)
    ttk.Label(root, textvariable=status_var, font=("Segoe UI", 10)).pack(pady=10)

    def update_ui(solar, ev, battery):
        solar_var.set(f"🔆 Solar Power: {solar:.2f} kW")
        ev_var.set(f"🚗 EV Charging: {ev:.2f} kW")
        battery_var.set(f"🔋 Battery Level: {battery}%")

    def refresh_status():
        status_var.set(f"Status: {connection_status}")
        root.after(1000, refresh_status)

    refresh_status()

    # Start background update loop
    threading.Thread(target=throttled_update_loop, args=(update_ui,), daemon=True).start()

    # Start WebSocket connection in another thread
    def start_socketio():
        try:
            query = urllib.parse.urlencode({"token": TOKEN, "apiVersion": "4"})
            url = f"https://api.chargehq.net?{query}"
            sio.connect(
                url,
                transports=["websocket"],
                socketio_path="/socket.io",
                headers={"Origin": "https://app.chargehq.net"}
            )
            sio.wait()
        except Exception as e:
            print(f"[FATAL] Failed to connect: {e}")
            status_var.set("Status: Failed to connect")

    threading.Thread(target=start_socketio, daemon=True).start()

    root.mainloop()

# === Run GUI ===
if __name__ == "__main__":
    start_gui()
