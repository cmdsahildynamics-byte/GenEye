from flask import Flask, render_template, jsonify, send_file
import paho.mqtt.client as mqtt
import time, csv, os

app = Flask(__name__)
CSV_FILE = "sahil_log.csv"

# Live snapshot keys
latest = {
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

BROKER = "exceliot.com"
PORT = 1883
USERNAME = "scadaboxflow"
PASSWORD = "Jaimataji@9966"
TOPIC = "/data/genset/02500924120800025541"

def payload_to_registers(payload: bytes):
    usable = payload[3:] if len(payload) >= 3 else payload
    return [int.from_bytes(usable[i:i+2], "big") for i in range(0, len(usable), 2)]

def ensure_csv_header():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp"] + list(latest.keys()))

def append_csv_snapshot():
    ensure_csv_header()
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([latest["Timestamp"]] + [latest[k] for k in latest.keys()])

def on_message(client, userdata, msg):
    regs = payload_to_registers(msg.payload)
    try:
        latest["Battery_Voltage"] = round(regs[51] * 0.001, 2)
        latest["Coolant_Temp"]    = round(regs[55] * 0.1, 1)
        latest["Engine_RPM"]      = round(regs[54] * 0.125, 2)
        latest["Frequency"]       = round(regs[58] * 0.01, 2)
        latest["Fuel_Level"]      = round(regs[57] * 0.01, 2)
        latest["No_of_Starts"]    = regs[59]
        latest["Power_kVA"]       = round(regs[60] * 0.1, 2)
        latest["Running_Hours"]   = round(regs[61] * 0.05, 2)
        latest["Status"]          = "ON" if regs[2] == 1 else "OFF"
        latest["Timestamp"]       = time.strftime("%d-%m-%Y %H:%M:%S")
    except Exception:
        return

    append_csv_snapshot()

# MQTT client
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC)
client.loop_start()

@app.route("/")
def dashboard():
    return render_template("sahil_dashboard.html")

@app.route("/data")
def data():
    return jsonify(latest)

@app.route("/history")
def history():
    if not os.path.exists(CSV_FILE):
        return jsonify({"Timestamp": [], "Running_Hours": [], "Fuel_Level": [], "Power_kVA": []})

    try:
        rows = []
        with open(CSV_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        if not rows:
            return jsonify({"Timestamp": [], "Running_Hours": [], "Fuel_Level": [], "Power_kVA": []})

        tail = rows[-20:]
        timestamps   = [r.get("Timestamp", "") for r in tail]
        run_hours    = [float(r.get("Running_Hours", 0) or 0) for r in tail]
        fuel_levels  = [float(r.get("Fuel_Level", 0) or 0) for r in tail]
        power_kva    = [float(r.get("Power_kVA", 0) or 0) for r in tail]

        return jsonify({
            "Timestamp": timestamps,
            "Running_Hours": run_hours,
            "Fuel_Level": fuel_levels,
            "Power_kVA": power_kva
        })
    except Exception:
        return jsonify({"Timestamp": [], "Running_Hours": [], "Fuel_Level": [], "Power_kVA": []})

@app.route("/download")
def download_csv():
    ensure_csv_header()
    return send_file(CSV_FILE, as_attachment=True)

if __name__ == "__main__":
    ensure_csv_header()
    app.run(host="0.0.0.0", port=8080)
