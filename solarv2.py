import socketio
import urllib.parse
import requests

# === CONFIG ===
TOKEN = "CHARGEHQTOKEN"  # ChargeHQ WebSocket token
HA_URL = "http://homeassistant.local:8123"  # Or your IP, e.g. http://192.168.1.100:8123
HA_TOKEN = "HOMEASSISTANTTOKEN"

HA_HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

# === Connect to ChargeHQ ===
sio = socketio.Client()

@sio.on("site-state")
def handle_site_state(data):
    try:
        solar_kw = data["powerFlows"]["pvKw"]
        ev_kw = data["powerFlows"]["evKw"]
        battery_level = data["teslaState"]["fields"]["battery_level"]

        print(f"🔆 Solar: {solar_kw:.2f} kW | 🚗 EV: {ev_kw:.2f} kW | 🔋 Battery: {battery_level}%")

        send_to_home_assistant("input_number.chargehq_solar_kw", solar_kw)
        send_to_home_assistant("input_number.chargehq_ev_kw", ev_kw)
        send_to_home_assistant("input_number.chargehq_battery", battery_level)

    except KeyError as e:
        print(f"[WARN] Missing key: {e}")
    except Exception as e:
        print(f"[ERROR] {e}")

def send_to_home_assistant(entity_id, value):
    url = f"{HA_URL}/api/services/input_number/set_value"
    payload = {
        "entity_id": entity_id,
        "value": round(value, 2),
    }

    try:
        r = requests.post(url, headers=HA_HEADERS, json=payload)
        if r.status_code != 200:
            print(f"[ERROR] Failed to update {entity_id}: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"[ERROR] Failed to connect to HA: {e}")

# === Build connection URL ===
query = urllib.parse.urlencode({
    "token": TOKEN,
    "apiVersion": "4"
})
url = f"https://api.chargehq.net?{query}"

sio.connect(
    url,
    transports=["websocket"],
    socketio_path="/socket.io",
    headers={"Origin": "https://app.chargehq.net"}
)

sio.wait()
