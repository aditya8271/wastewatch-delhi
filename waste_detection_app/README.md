# 🛰️ Illegal Dump Detection System — Ludhiana
Satellite + AI powered waste detection · Built with Streamlit

## 📁 Project structure
```
waste_detection_app/
├── app.py                  ← Main dashboard (run this)
├── pages/
│   ├── 1_satellite_scan.py ← NDVI + before/after + AI model
│   ├── 2_dump_map.py       ← Live Folium map
│   ├── 3_report_dump.py    ← Citizen report form
│   ├── 4_alerts.py         ← WhatsApp + Email alerts
│   └── 5_disease_risk.py   ← Disease outbreak predictor
├── utils/
│   ├── db.py               ← SQLite database
│   ├── ndvi.py             ← Satellite + AI model logic
│   ├── alerts.py           ← Twilio + SMTP
│   └── risk.py             ← Disease risk scoring
├── data/
│   └── mock_dumps.csv      ← Sample Ludhiana data
├── .streamlit/config.toml  ← Theme config
└── requirements.txt
```

## ⚡ Quick start (5 minutes)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. Open in browser
```
Local:   http://localhost:8501
Mobile:  http://YOUR_IP:8501   (same WiFi)
```

## 🤖 Adding your GitHub pretrained model

1. Download model weights from GitHub (`.pt` / `.h5` / `.pkl`)
2. Place file in `utils/` folder
3. Open `utils/ndvi.py` → find `run_model_inference()`
4. Replace mock logic with your model:

```python
# Example for PyTorch YOLOv8:
from ultralytics import YOLO
model = YOLO("utils/best.pt")
results = model(image_array)
label = results[0].names[results[0].probs.top1]

# Example for TensorFlow:
import tensorflow as tf
model = tf.keras.models.load_model("utils/model.h5")
pred = model.predict(preprocessed_image)
```

## 📱 Mobile access
Streamlit works on mobile browser automatically.
Share your IP address with team on same WiFi.

## 🚨 WhatsApp alerts setup

1. Sign up at [twilio.com](https://twilio.com) (free trial)
2. Go to Messaging → Try it out → WhatsApp
3. Join sandbox: send `join <word>` to +1 415 523 8886
4. Create `.env` file:

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
ALERT_PHONE=whatsapp:+91XXXXXXXXXX
EMAIL_USER=your@gmail.com
EMAIL_PASS=your_app_password
ALERT_EMAIL=officer@example.com
```

5. Install dotenv loader:
```python
# Add to top of app.py
from dotenv import load_dotenv
load_dotenv()
```

## 🌐 Free deployment (Streamlit Cloud)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repo → select `app.py`
4. Add secrets in Streamlit Cloud settings
5. Share link with anyone!

## 📊 Features
- 🛰️ NDVI satellite change detection
- 🔄 Before vs after image comparison  
- 🤖 AI model upload & inference
- 🗺️ Interactive Folium map with filters
- 📋 Citizen dump reporting form
- 🚨 WhatsApp + Email alerts (Twilio)
- 🦟 Disease outbreak risk predictor
- 📈 Analytics + ward leaderboard
- 💾 SQLite database (persistent)
- 📱 Mobile responsive UI
