# 🚁 UAV Security with Unsupervised Machine Learning

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-5.0-green.svg)](https://www.djangoproject.com/)
[![ML Models](https://img.shields.io/badge/ML%20Models-7-orange.svg)](.)
[![Unsupervised](https://img.shields.io/badge/Unsupervised-K--Means%20%7C%20DBSCAN%20%7C%20Isolation%20Forest-blueviolet)](.)

> **Unsupervised Machine Learning system for UAV threat detection and anomaly analysis — clustering, anomaly detection, and dimensionality reduction without labeled data.**

A production-ready machine learning platform built with **Django 5.0** for detecting and analyzing security threats in Unmanned Aerial Vehicle (UAV) systems. Features both **unsupervised** (K-Means, DBSCAN, Isolation Forest, PCA, t-SNE) and **supervised** (Random Forest, SVM, Gradient Boosting, XGBoost) algorithms, with an interactive web dashboard.

---

## 🎯 Project Focus: Unsupervised Learning

This project demonstrates the application of **unsupervised machine learning** to UAV cybersecurity. The key unsupervised methods include:

| Algorithm | Type | Purpose |
|-----------|------|---------|
| **K-Means** | Clustering | Partition UAV telemetry into k behavioral groups |
| **DBSCAN** | Density-Based Clustering | Find arbitrary-shaped clusters and noise/outlier points |
| **Isolation Forest** | Anomaly Detection | Detect anomalous UAV behavior without labels |
| **PCA** | Dimensionality Reduction | Reduce 10D feature space to 2D for visualization |
| **t-SNE** | Manifold Learning | Non-linear embedding for cluster visualization |

### Evaluation Metrics (No Labels Required)
- **Silhouette Score** — cluster cohesion vs. separation [-1, 1]
- **Calinski-Harabasz Index** — between-cluster vs. within-cluster variance
- **Davies-Bouldin Index** — average inter-cluster similarity (lower = better)
- **Elbow Method** — optimal k selection via inertia analysis

---

## ✨ Key Features

### 🤖 Machine Learning Pipeline
- **4 Unsupervised Models**: K-Means, DBSCAN, Isolation Forest, PCA/t-SNE
- **4 Supervised Models**: Random Forest (100%), SVM (99.5%), Gradient Boosting (100%), XGBoost (99.95%)
- **10 UAV-Specific Features**: Altitude, speed, direction, signal strength, GPS accuracy, battery, temperature, vibration, flight time, distance from base
- **6 Threat Categories**: Normal, Jamming Attack, GPS Spoofing, Unauthorized Access, Signal Interference, Physical Tampering
- **Automated Training Pipeline**: One-command training for all models

### 🛡️ UAV Security Analysis
- **Cluster-Based Threat Discovery**: Unsupervised clustering reveals natural groupings in UAV behavior
- **Anomaly Detection**: Isolation Forest flags unusual flight patterns without needing labeled training data
- **Real-Time Detection**: Live threat monitoring with <100ms latency
- **Batch Processing**: Upload CSV files for bulk analysis

### 🛰️ Real Drone Connection (NEW)
- **REST API Integration**: Connect real drones via HTTP API with API key authentication
- **Live Telemetry Stream**: Drones send sensor data every N seconds for continuous monitoring
- **Device Registration**: Register unlimited drones with unique API keys
- **Auto Threat Detection**: Every telemetry packet is run through the ML pipeline in real-time
- **Connection Health Monitoring**: Heartbeat endpoint for connectivity checks
- **Ready-to-use Code Examples**: Python, cURL, and Arduino integration guides

### 📱 Threat Notifications (NEW)
- **Telegram Bot**: Instant push notifications to phone & smartwatch via Telegram
- **Email Alerts**: SMTP email notifications with HTML-formatted threat reports
- **Browser Push**: Native browser notifications for the dashboard
- **Configurable**: Enable/disable per channel via `.env`

### 📊 Interactive Visualizations
- **Elbow Method Chart**: Optimal k determination with gradient fill
- **Silhouette Analysis**: Per-k clustering quality scores with best-k highlighting
- **Cluster Distribution**: Premium doughnut charts of cluster sizes
- **Anomaly Distribution**: Normal vs. anomaly breakdown
- **Interactive PCA Scatter Plot**: Live 2D projection of 3,000+ UAV records colored by cluster (API-powered)
- **Algorithm Comparison Bar**: K-Means vs DBSCAN silhouette scores side-by-side
- **PCA Explained Variance**: Component-wise variance capture doughnut
- **Isolation Forest Score Analysis**: Min/Mean/Max anomaly scores with statistical cards
- **Detection Timeline**: Time-series trend charts (7/30/90 day ranges)
- **Algorithm Comparison Table**: Side-by-side unsupervised metrics

### 🎨 Premium Dashboard
- Dark cybersecurity theme with glassmorphism
- Responsive design (mobile, tablet, desktop)
- Smooth animations and micro-interactions
- Role-based access (Admin, Analyst, Viewer)

---

## 🏗️ Architecture

```
uav_security_ml/
├── uav_project/              # Django project settings
│   ├── settings.py           # Configuration
│   ├── urls.py               # Root URL config
│   └── wsgi.py               # WSGI entry point
├── core/                     # Main Django app
│   ├── models.py             # ORM models (User, Detection, Alert, MLModel, DroneDevice)
│   ├── views/
│   │   ├── main.py           # Dashboard views
│   │   ├── unsupervised.py   # Unsupervised analysis views
│   │   ├── detection.py      # Threat detection views
│   │   ├── drone_connection.py  # Real drone REST API + dashboard
│   │   ├── analytics.py      # Analytics dashboard
│   │   ├── training.py       # Model training views
│   │   └── ...
│   └── urls.py               # URL patterns
├── services/
│   ├── unsupervised_service.py    # K-Means, DBSCAN, Isolation Forest, PCA, t-SNE
│   ├── ml_service.py              # Supervised prediction service
│   ├── training_service.py        # Model training service
│   └── notification_service.py    # Telegram + Email threat alerts
├── scripts/
│   ├── generate_dataset.py        # UAV dataset generator (126K samples)
│   ├── train_unsupervised.py      # Unsupervised training pipeline
│   ├── train_models.py            # Supervised training pipeline
│   └── model_comparison.py        # Benchmarking
├── templates/                # Django templates (Bootstrap 5)
│   ├── unsupervised/         # Unsupervised analysis pages
│   ├── dashboard/            # Dashboard & analytics
│   ├── detection/            # Detection & batch processing
│   └── drone/                # Drone connection & API docs
├── static/                   # CSS, JS
├── ml_models/                # Trained model .pkl files
├── data/                     # Generated datasets (CSV)
├── exports/                  # Results JSON, reports
└── requirements.txt
```

---

## 📊 Results

### Unsupervised Learning

| Algorithm | Clusters | Silhouette | Calinski-Harabasz | Notes |
|-----------|----------|------------|-------------------|-------|
| **K-Means** | Auto (elbow) | > 0.40 | High | Best overall clustering |
| **DBSCAN** | Auto (density) | Variable | — | Discovers noise points |
| **Isolation Forest** | — | — | — | ~10% anomaly rate |
| **PCA** | 2 components | — | — | ~39.5% variance explained |

### Supervised Learning (Baseline Comparison)

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| Random Forest | 100.00% | 100.00% | 100.00% | 100.00% |
| XGBoost | 99.95% | 99.83% | 100.00% | 99.92% |
| Gradient Boosting | 99.98% | 99.98% | 99.98% | 99.98% |
| SVM (RBF) | 99.50% | 99.92% | 98.42% | 99.16% |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Setup

```bash
# Clone
git clone https://github.com/shivansh-12315646/uav_security_ml.git
cd uav_security_ml

# Virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Generate Dataset & Train Models

```bash
# 1. Generate UAV security dataset (126K samples, 5 threat classes)
python scripts/generate_dataset.py

# 2. Train UNSUPERVISED models (K-Means, DBSCAN, Isolation Forest, PCA, t-SNE)
python scripts/train_unsupervised.py

# 3. Train supervised models (RF, SVM, GB, XGBoost) — for comparison
python scripts/train_models.py
```

### Run the Application

```bash
python manage.py migrate
python manage.py create_admin
python manage.py runserver
```

**Access**: http://localhost:8000 — Login: `admin` / `admin123`

---

## 🛰️ Connecting a Real Drone

### 1. Register a drone
On the **Drone Connection** page, click "Register Drone" and save the generated API key.

### 2. Send telemetry from the drone

**Python (Raspberry Pi / Companion Computer):**
```python
import requests, time

API_KEY = "YOUR_API_KEY_HERE"
BASE_URL = "http://YOUR_SERVER:8000"

while True:
    telemetry = {
        "altitude": read_altimeter(),
        "speed": read_gps_speed(),
        "direction": read_compass(),
        "signal_strength": read_signal(),
        "distance_from_base": calc_distance(),
        "flight_time": get_flight_time(),
        "battery_level": read_battery(),
        "temperature": read_temp(),
        "vibration": read_imu(),
        "gps_accuracy": read_gps_hdop(),
    }

    resp = requests.post(
        f"{BASE_URL}/drone/api/telemetry/",
        json=telemetry,
        headers={"X-API-Key": API_KEY},
    )
    result = resp.json()
    print(f"Prediction: {result['prediction']} ({result['confidence']:.1%})")

    time.sleep(5)
```

**cURL (Quick Test):**
```bash
curl -X POST http://localhost:8000/drone/api/telemetry/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"altitude":50,"speed":10,"direction":0,"signal_strength":47,"distance_from_base":4989,"flight_time":143,"battery_level":15,"temperature":15,"vibration":0,"gps_accuracy":17}'
```

### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/drone/api/register/` | Session | Register a new drone |
| `POST` | `/drone/api/telemetry/` | X-API-Key | Submit telemetry, get prediction |
| `GET`  | `/drone/api/heartbeat/` | X-API-Key | Connectivity check |
| `GET`  | `/drone/api/{id}/history/` | Session | Telemetry history |
| `POST` | `/drone/api/{id}/delete/` | Session | Unregister a drone |

---

## 📱 Setting Up Notifications

### Telegram (Recommended — works on phone, watch, desktop)

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts to create a bot
3. Copy the bot token
4. Message your bot, then visit `https://api.telegram.org/bot<TOKEN>/getUpdates` to find your chat ID
5. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=123456:ABCdefGHIjklMNO
   TELEGRAM_CHAT_ID=987654321
   NOTIFICATIONS_ENABLED=true
   ```

### Email (SMTP)

Add to `.env`:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECIPIENT=alert-recipient@email.com
```

---

## 🔧 Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 5.0, SQLite/PostgreSQL |
| **ML (Unsupervised)** | scikit-learn (K-Means, DBSCAN, Isolation Forest, PCA), t-SNE |
| **ML (Supervised)** | scikit-learn (RF, SVM, GB), XGBoost |
| **Data Science** | pandas, numpy, joblib |
| **Frontend** | Bootstrap 5, Chart.js, Font Awesome 6, AOS animations |
| **Notifications** | Telegram Bot API, SMTP Email |
| **Static Files** | WhiteNoise |
| **Production** | Gunicorn, Docker |

---

## 🚀 Deployment Guide

### Free Cloud Deployment (Recommended for Demo)

#### Option 1: PythonAnywhere (Easiest — Free Tier)
1. Create free account at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your project via the Files tab or clone from GitHub:
   ```bash
   git clone https://github.com/shivansh-12315646/uav_security_ml.git
   ```
3. Create a virtual environment:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.11 uav_env
   pip install -r uav_security_ml/requirements.txt
   ```
4. Go to **Web** tab → **Add a new web app** → **Manual configuration** → **Python 3.11**
5. Set:
   - **Source code**: `/home/yourusername/uav_security_ml`
   - **WSGI file**: Edit to point to `uav_project.wsgi`
   - **Virtualenv**: `/home/yourusername/.virtualenvs/uav_env`
6. In the WSGI config file, add:
   ```python
   import os, sys
   path = '/home/yourusername/uav_security_ml'
   if path not in sys.path:
       sys.path.append(path)
   os.environ['DJANGO_SETTINGS_MODULE'] = 'uav_project.settings'
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
7. Set `ALLOWED_HOSTS` in `settings.py`: `['yourusername.pythonanywhere.com']`
8. Run migrations and create admin via the Bash console
9. Click **Reload** → Your app is live!

#### Option 2: Render (Auto-deploy from GitHub)
1. Create account at [render.com](https://render.com)
2. New → **Web Service** → Connect your GitHub repo
3. Settings:
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn uav_project.wsgi:application`
4. Add env vars: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS=*.onrender.com`

#### Option 3: Railway (One-Click Deploy)
1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub Repo
3. Railway auto-detects Django and sets up everything
4. Add env vars in the dashboard

---

## 👨‍💻 Author

**Shivansh**
- GitHub: [@shivansh-12315646](https://github.com/shivansh-12315646)

---

## 📄 License

MIT License