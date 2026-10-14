from datetime import datetime
import io
import os
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
import numpy as np
from PIL import Image
import pytesseract
import pytz

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

system_data = {
    "temp": 0,
    "carbon": 0,
    "hum": 0,
    "en_t": 1,
    "en_c": 1,
    "en_h": 1,
    "t_min": 30,
    "t_max": 82,
    "c_min": 10,
    "c_max": 50,
    "h_min": 50,
    "h_max": 90,
    "timestamp": "ยังไม่มีข้อมูล",
}


@app.route("/", methods=["GET"])
def health_check():
  return jsonify({"status": "Cloud OCR Server is running!"}), 200


@app.route("/process_ocr", methods=["POST"])
def process_ocr():
  if "image" not in request.files:
    return (
        jsonify({"success": False, "number": "--.-", "error": "No image sent"}),
        400,
    )

  file = request.files["image"]
  image_bytes = file.read()

  try:
    image = Image.open(io.BytesIO(image_bytes)).convert("L")
    custom_config = r"--psm 7 -c tessedit_char_whitelist=0123456789.-"
    detected_number = pytesseract.image_to_string(
        image, config=custom_config
    ).strip()

    if detected_number:
      print(f"[Cloud OCR Result]: {detected_number}")
      return jsonify({"success": True, "number": detected_number})
    else:
      return jsonify({"success": False, "number": "--.-"})

  except Exception as e:
    print(f"Error processing image: {e}")
    return jsonify({"success": False, "number": "ERR", "error": str(e)}), 500


@app.route("/update_readings", methods=["POST"])
def update_readings():
  global system_data
  data = request.form if request.form else request.json
  if not data:
    data = request.args

  if "temp" in data and data.get("temp") is not None:
    try:
      system_data["temp"] = float(data.get("temp"))
    except:
      pass
  if "carbon" in data and data.get("carbon") is not None:
    try:
      system_data["carbon"] = float(data.get("carbon"))
    except:
      pass
  if "hum" in data and data.get("hum") is not None:
    try:
      system_data["hum"] = float(data.get("hum"))
    except:
      pass

  if "en_t" in data:
    try:
      system_data["en_t"] = int(data.get("en_t"))
    except:
      pass
  if "en_c" in data:
    try:
      system_data["en_c"] = int(data.get("en_c"))
    except:
      pass
  if "en_h" in data:
    try:
      system_data["en_h"] = int(data.get("en_h"))
    except:
      pass

  if "t_min" in data:
    try:
      system_data["t_min"] = float(data.get("t_min"))
    except:
      pass
  if "t_max" in data:
    try:
      system_data["t_max"] = float(data.get("t_max"))
    except:
      pass
  if "c_min" in data:
    try:
      system_data["c_min"] = float(data.get("c_min"))
    except:
      pass
  if "c_max" in data:
    try:
      system_data["c_max"] = float(data.get("c_max"))
    except:
      pass
  if "h_min" in data:
    try:
      system_data["h_min"] = float(data.get("h_min"))
    except:
      pass
  if "h_max" in data:
    try:
      system_data["h_max"] = float(data.get("h_max"))
    except:
      pass

  tz = pytz.timezone("Asia/Bangkok")
  system_data["timestamp"] = datetime.now(tz).strftime("%d/%m/%Y, %H:%M:%S")
  return jsonify({"success": True})


@app.route("/api/data", methods=["GET"])
def get_api_data():
  return jsonify(system_data)


@app.route("/dashboard", methods=["GET"])
def dashboard():
  html_content = """
    <!DOCTYPE html>
    <html lang="th">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>ESP32 Engineering Telemetry Dashboard</title>
      <style>
        :root {
          --bg-color: #0f172a;
          --card-bg: #1e293b;
          --border-color: #334155;
          --text-main: #f8fafc;
          --text-muted: #94a3b8;
          --accent-green: #10b981;
          --accent-orange: #f59e0b;
          --accent-red: #ef4444;
        }
        * { box-sizing: border-box; }
        body { background: var(--bg-color); color: var(--text-main); font-family: 'Segoe UI', Inter, sans-serif; margin: 0; padding: 25px; text-align: center; }
        
        header { max-width: 1000px; margin: 0 auto 25px auto; border-bottom: 1px solid var(--border-color); padding-bottom: 15px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
        h1 { margin: 0; font-size: 1.4rem; color: var(--text-main); letter-spacing: 0.5px; display: flex; align-items: center; gap: 10px; }
        .system-status { font-size: 0.85rem; background: rgba(16, 185, 129, 0.15); color: var(--accent-green); padding: 5px 12px; border-radius: 20px; border: 1px solid rgba(16, 185, 129, 0.3); font-weight: 600; }

        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; max-width: 1000px; margin: 0 auto; }
        
        .card { background: var(--card-bg); border-radius: 10px; padding: 20px; border: 1px solid var(--border-color); box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); text-align: left; position: relative; overflow: hidden; }
        .card::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; }
        .card.temp::before { background: var(--accent-orange); }
        .card.carbon::before { background: #38bdf8; }
        .card.hum::before { background: var(--accent-green); }

        .card-title { font-size: 0.9rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; }
        
        .metric-display { display: flex; align-items: baseline; justify-content: space-between; margin: 15px 0; }
        .metric-value { font-size: 2.8rem; font-weight: 700; font-family: 'Courier New', monospace; color: var(--text-main); }
        .disabled-text { font-size: 2rem; color: var(--text-muted); font-style: italic; }
        
        .threshold-panel { background: rgba(15, 23, 42, 0.6); border: 1px solid var(--border-color); border-radius: 6px; padding: 10px 12px; font-size: 0.82rem; display: flex; justify-content: space-between; color: var(--text-muted); }
        .threshold-panel span b { color: var(--text-main); font-family: monospace; }

        .footer-info { max-width: 1000px; margin: 25px auto 0 auto; font-size: 0.85rem; color: var(--text-muted); display: flex; justify-content: space-between; border-top: 1px solid var(--border-color); padding-top: 15px; }
      </style>
    </head>
    <body>

      <header>
        <h1><span>⚙️</span> ESP32 Engineering Telemetry Dashboard</h1>
        <div class="system-status">● SYSTEM ONLINE</div>
      </header>

      <div class="dashboard-grid">
        <!-- อุณหภูมิ -->
        <div class="card temp">
          <div class="card-title">🌡️ อุณหภูมิ (Temperature)</div>
          <div class="metric-display">
            <div class="metric-value" id="v-temp">--.-</div>
            <div style="color: var(--text-muted); font-weight: 600;" id="unit-temp">UNIT</div>
          </div>
          <div class="threshold-panel" id="panel-temp">
            <span>Min Limit: <b id="t-min" style="color:var(--accent-orange)">--</b></span>
            <span>Max Limit: <b id="t-max" style="color:var(--accent-red)">--</b></span>
          </div>
        </div>

        <!-- คาร์บอน -->
        <div class="card carbon">
          <div class="card-title">🧪 คาร์บอน (Carbon)</div>
          <div class="metric-display">
            <div class="metric-value" id="v-carbon">--.-</div>
            <div style="color: var(--text-muted); font-weight: 600;" id="unit-carbon">PPM</div>
          </div>
          <div class="threshold-panel" id="panel-carbon">
            <span>Min Limit: <b id="c-min" style="color:var(--accent-orange)">--</b></span>
            <span>Max Limit: <b id="c-max" style="color:var(--accent-red)">--</b></span>
          </div>
        </div>

        <!-- ความชื้น -->
        <div class="card hum">
          <div class="card-title">💧 ความชื้น (Humidity)</div>
          <div class="metric-display">
            <div class="metric-value" id="v-hum">--.-</div>
            <div style="color: var(--text-muted); font-weight: 600;" id="unit-hum">%RH</div>
          </div>
          <div class="threshold-panel" id="panel-hum">
            <span>Min Limit: <b id="h-min" style="color:var(--accent-orange)">--</b></span>
            <span>Max Limit: <b id="h-max" style="color:var(--accent-red)">--</b></span>
          </div>
        </div>
      </div>

      <div class="footer-info">
        <div>Architecture: Flask / Cloud OCR Engine</div>
        <div>Last Synchronized: <span id="v-time" style="color: var(--text-main); font-family: monospace;">Waiting for sync...</span></div>
      </div>

      <script>
        async function fetchTelemetry() {
          try {
            const res = await fetch('/api/data');
            const data = await res.json();
            
            if (data.en_t == 1) {
              document.getElementById('v-temp').innerText = data.temp;
              document.getElementById('unit-temp').style.display = 'block';
              document.getElementById('panel-temp').style.display = 'flex';
            } else {
              document.getElementById('v-temp').innerHTML = '<span class="disabled-text">DISABLED</span>';
              document.getElementById('unit-temp').style.display = 'none';
              document.getElementById('panel-temp').style.display = 'none';
            }
            document.getElementById('t-min').innerText = data.t_min;
            document.getElementById('t-max').innerText = data.t_max;

            if (data.en_c == 1) {
              document.getElementById('v-carbon').innerText = data.carbon;
              document.getElementById('unit-carbon').style.display = 'block';
              document.getElementById('panel-carbon').style.display = 'flex';
            } else {
              document.getElementById('v-carbon').innerHTML = '<span class="disabled-text">DISABLED</span>';
              document.getElementById('unit-carbon').style.display = 'none';
              document.getElementById('panel-carbon').style.display = 'none';
            }
            document.getElementById('c-min').innerText = data.c_min;
            document.getElementById('c-max').innerText = data.c_max;

            if (data.en_h == 1) {
              document.getElementById('v-hum').innerText = data.hum;
              document.getElementById('unit-hum').style.display = 'block';
              document.getElementById('panel-hum').style.display = 'flex';
            } else {
              document.getElementById('v-hum').innerHTML = '<span class="disabled-text">DISABLED</span>';
              document.getElementById('unit-hum').style.display = 'none';
              document.getElementById('panel-hum').style.display = 'none';
            }
            document.getElementById('h-min').innerText = data.h_min;
            document.getElementById('h-max').innerText = data.h_max;

            document.getElementById('v-time').innerText = data.timestamp;
          } catch(e) { console.error("Telemetry fetch error:", e); }
        }
        setInterval(fetchTelemetry, 2000);
        fetchTelemetry();
      </script>
    </body>
    </html>
    """
  return render_template_string(html_content)


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port, debug=False)
