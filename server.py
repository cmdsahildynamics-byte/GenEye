# server.py
from flask import Flask, jsonify
import paho.mqtt.client as mqtt
from datetime import datetime
import json

app = Flask(__name__)

# Store latest messages per topic
latest_data = {}

# MQTT configuration
MQTT_BROKER = "exceliot.com"
MQTT_PORT = 1883
MQTT_USER = "scadaboxflow"
MQTT_PASSWORD = "Jaimataji@9966"
MQTT_TOPIC = "genset/#"  # adjust if your device uses a different topic

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with code", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        # Try to decode as JSON; if not, store raw string
        try:
            decoded = json.loads(payload)
        except:
            decoded = payload
        
        latest_data[msg.topic] = {
            "id": len(latest_data)+1,
            "time": datetime.now().isoformat(),
            "topic": msg.topic,
            "device": msg.topic.split("/")[-1],
            "decoded": decoded
        }
        print(f"Received from {msg.topic}: {decoded}")
    except Exception as e:
        print("Error decoding message:", e)

# Connect to MQTT
client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# API for dashboard
@app.route("/api/latest")
def get_latest():
    return jsonify(list(latest_data.values()))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
