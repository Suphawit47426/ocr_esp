const express = require('express');
const app = express();

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// ตัวแปรเก็บค่าปัจจุบันและค่า Threshold
let systemData = {
  temp: 0,
  carbon: 0,
  hum: 0,
  t_min: 30, t_max: 82,
  c_min: 10, c_max: 50,
  h_min: 50, h_max: 90,
  timestamp: 'ยังไม่มีข้อมูล'
};

// 1. รับค่าที่ส่งมาจาก ESP32 (รองรับทั้งค่าเซ็นเซอร์และค่า Threshold)
app.post('/update_readings', (req, res) => {
  const { temp, carbon, hum, t_min, t_max, c_min, c_max, h_min, h_max } = req.body;
  
  if (temp !== undefined) systemData.temp = temp;
  if (carbon !== undefined) systemData.carbon = carbon;
  if (hum !== undefined) systemData.hum = hum;
  if (t_min !== undefined) systemData.t_min = t_min;
  if (t_max !== undefined) systemData.t_max = t_max;
  if (c_min !== undefined) systemData.c_min = c_min;
  if (c_max !== undefined) systemData.c_max = c_max;
  if (h_min !== undefined) systemData.h_min = h_min;
  if (h_max !== undefined) systemData.h_max = h_max;

  systemData.timestamp = new Date().toLocaleString('th-TH', { timeZone: 'Asia/Bangkok' });
  console.log("📥 Received data from ESP32:", systemData);

  res.json({ success: true });
});

// 2. API ให้หน้าเว็บ Dashboard ดึงข้อมูลไปแสดงผลแบบเรียลไทม์
app.get('/api/data', (req, res) => {
  res.json(systemData);
});

// 3. หน้าเว็บ Dashboard
app.get('/dashboard', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="th">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>ESP32 Live Dashboard</title>
      <style>
        * { box-sizing: border-box; }
        body { background: #121212; color: #fff; font-family: 'Segoe UI', sans-serif; text-align: center; padding: 20px; margin: 0; }
        h2 { color: #00e676; margin-bottom: 5px; }
        p { color: #aaa; font-size: 0.9rem; }
        .grid { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; max-width: 900px; margin: 20px auto; }
        .card { background: #1e1e1e; border-radius: 12px; padding: 20px; width: 260px; border: 1px solid #333; box-shadow: 0 4px 12px rgba(0,0,0,0.5); text-align: left; }
        .card h3 { margin-top: 0; font-size: 1rem; color: #ffeb3b; border-bottom: 1px solid #444; padding-bottom: 8px; }
        .val-box { text-align: center; margin: 15px 0; }
        .val { font-size: 2.5rem; color: #00e676; font-family: monospace; font-weight: bold; }
        .thresholds { font-size: 0.85rem; color: #bbb; background: #2a2a2a; padding: 8px; border-radius: 6px; display: flex; justify-content: space-between; }
        .footer { color: #888; font-size: 0.85rem; margin-top: 20px; }
      </style>
    </head>
    <body>
      <h2>📊 ESP32 Live Monitoring Dashboard</h2>
      <p>แสดงผลค่าเซ็นเซอร์และเกณฑ์มาตรฐานแบบเรียลไทม์</p>

      <div class="grid">
        <!-- อุณหภูมิ -->
        <div class="card">
          <h3>🌡️ อุณหภูมิ (Temperature)</h3>
          <div class="val-box">
            <div class="val" id="v-temp">--.-</div>
          </div>
          <div class="thresholds">
            <span>ต่ำสุด: <b id="t-min" style="color:#ff9800">--</b></span>
            <span>สูงสุด: <b id="t-max" style="color:#ff5252">--</b></span>
          </div>
        </div>

        <!-- คาร์บอน -->
        <div class="card">
          <h3>🧪 คาร์บอน (Carbon)</h3>
          <div class="val-box">
            <div class="val" id="v-carbon">--.-</div>
          </div>
          <div class="thresholds">
            <span>ต่ำสุด: <b id="c-min" style="color:#ff9800">--</b></span>
            <span>สูงสุด: <b id="c-max" style="color:#ff5252">--</b></span>
          </div>
        </div>

        <!-- ความชื้น -->
        <div class="card">
          <h3>💧 ความชื้น (Humidity)</h3>
          <div class="val-box">
            <div class="val" id="v-hum">--.-</div>
          </div>
          <div class="thresholds">
            <span>ต่ำสุด: <b id="h-min" style="color:#ff9800">--</b></span>
            <span>สูงสุด: <b id="h-max" style="color:#ff5252">--</b></span>
          </div>
        </div>
      </div>

      <div class="footer">อัปเดตล่าสุดจากอุปกรณ์: <span id="v-time">-</span></div>

      <script>
        async function updateDashboard() {
          try {
            const res = await fetch('/api/data');
            const data = await res.json();
            
            document.getElementById('v-temp').innerText = data.temp;
            document.getElementById('t-min').innerText = data.t_min;
            document.getElementById('t-max').innerText = data.t_max;

            document.getElementById('v-carbon').innerText = data.carbon;
            document.getElementById('c-min').innerText = data.c_min;
            document.getElementById('c-max').innerText = data.c_max;

            document.getElementById('v-hum').innerText = data.hum;
            document.getElementById('h-min').innerText = data.h_min;
            document.getElementById('h-max').innerText = data.h_max;

            document.getElementById('v-time').innerText = data.timestamp;
          } catch(e) {
            console.error("Fetch error:", e);
          }
        }
        setInterval(updateDashboard, 2000);
        updateDashboard();
      </script>
    </body>
    </html>
  `);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Dashboard server running on port ${PORT}`));
