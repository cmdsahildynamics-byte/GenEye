import os
import csv
import threading
import paho.mqtt.client as mqtt
from flask import Flask, jsonify
from flask_cors import CORS

# --- Flask setup ---
app = Flask(__name__)
CORS(app)

# --- Global state ---
latest_decoded = {
    "Battery_Voltage": None,
    "Coolant_Temp": None,
    "Engine_RPM": None,
    "Frequency": None,
    "Fuel_Level": None,
    "No_of_Starts": None,
    "Power_kVA": None,
    "Running_Hours": None,
    "Status": "OFF",
    "Timestamp": "—"
}

# --- CSV init ---
def init_csv():
    if not os.path.exists("data_log.csv"):
        with open("data_log.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(latest_decoded.keys())

def log_to_csv(decoded):
    with open("data_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(decoded.values())

# --- MQTT handlers ---
def on_connect(client, userdata, flags, rc):
    print("Connected to broker with result code", rc)
    client.subscribe("your/topic/here")  # replace with your actual topic

def on_message(client, userdata, msg):
    global latest_decoded
    # Replace with your decoding logic
    decoded = {
        "Battery_Voltage": 24.94,
        "Coolant_Temp": 91.4,
        "Engine_RPM": 112,
        "Frequency": 50,
        "Fuel_Level": 75,
        "No_of_Starts": 111,
        "Power_kVA": 12.5,
        "Running_Hours": 113.2,
        "Status": "ON",
        "Timestamp": "now"
    }
    latest_decoded = decoded
    log_to_csv(decoded)
    print("Message decoded:", decoded)

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("exceliot.com", 1883, 60)  # adjust host/port if needed
    client.loop_forever()

# --- Background thread for MQTT ---
def start_background():
    threading.Thread(target=start_mqtt, daemon=True).start()

# Always start MQTT, even under Gunicorn
start_background()

# --- Flask routes ---
@app.route("/")
def index():
    return "Sahil Dynamics Remote Monitoring Dashboard is running."

@app.route("/data")
def data():
    return jsonify(latest_decoded)

# --- Local run ---
if __name__ == "__main__":
    init_csv()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False, use_reloader=False)
