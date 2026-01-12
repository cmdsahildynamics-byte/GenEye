# dashboard.py
from flask import Flask, render_template
import paho.mqtt.client as mqtt
import time

app = Flask(__name__)
latest = {
    "Battery_Voltage": 0.0,
    "No_of_Starts": 0,
    "Running_Hours": 0.0,
    "Status": "OFF",
    "Timestamp": "—"
}

def payload_to_registers(payload: bytes):
    usable = payload[3:]
    return [int.from_bytes(usable[i:i+2], "big") for i in range(0, len(usable), 2)]

def on_message(client, userdata, msg):
    regs = payload_to_registers(msg.payload)
    latest["Battery_Voltage"] = round(regs[51] * 0.001, 3)
    latest["No_of_Starts"] = regs[59]
    latest["Running_Hours"] = round(regs[61] * 0.05, 3)
    latest["Status"] = "ON" if regs[2] == 1 else "OFF"
    latest["Timestamp"] = time.strftime("%d-%m-%Y %H:%M:%S")

client = mqtt.Client()
client.username_pw_set("scadaboxflow", "Jaimataji@9966")
client.on_message = on_message
client.connect("exceliot.com", 1883, 60)
client.subscribe("/data/genset/02500924120800025541")
client.loop_start()

@app.route("/")
def dashboard():
    return render_template("dashboard.html", data=latest)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
