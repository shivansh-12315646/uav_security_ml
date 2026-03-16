# 🚁 UAV Security with Machine Learning

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-5.0-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ML Models](https://img.shields.io/badge/ML%20Models-4-orange.svg)](.)
[![Accuracy](https://img.shields.io/badge/Accuracy-99%25+-success.svg)](.)

> **🎯 Advanced Machine Learning System for Real-Time UAV Threat Detection and Security Analysis**

A production-ready, enterprise-grade machine learning platform built with **Django** for detecting and analyzing security threats in Unmanned Aerial Vehicle (UAV) systems. Features multiple ML algorithms, real-time monitoring, comprehensive analytics, and a beautiful dashboard.

---

## ✨ Key Features

### 🤖 **Real Machine Learning Pipeline**
- **4 Production Models**: Random Forest (100%), SVM (99.5%), Gradient Boosting (100%), XGBoost (99.95%)
- **6 Threat Categories**: Normal, Jamming Attack, GPS Spoofing, Unauthorized Access, Signal Interference, Physical Tampering
- **Cross-Validation**: 5-fold CV for robust evaluation
- **Feature Engineering**: StandardScaler preprocessing with 10 UAV-specific features
- **Model Persistence**: Save/load trained models for deployment

### 🛡️ **UAV Security Features**
- **10 Comprehensive Metrics**: Altitude, speed, direction, signal strength, GPS accuracy, battery, temperature, vibration, flight time, distance from base
- **Real-Time Detection**: Live threat monitoring with <100ms latency
- **Alert System**: Multi-level threat classification (Low, Medium, High, Critical)

### 📊 **Advanced Analytics & Visualization**
- Interactive charts with Chart.js and Plotly
- Detection timeline and trend analysis
- Model comparison dashboard

### 🎨 **Premium User Interface**
- Modern Bootstrap 5 responsive design
- Dark mode support
- Role-based access (Admin, Analyst, Viewer)

### 🚀 **Production Ready**
- **Django 5.0** with PostgreSQL / SQLite support
- **WhiteNoise** for efficient static file serving
- **Django Admin** for full data management
- Security headers, CSRF protection, secure sessions

---

## 🏗️ Architecture

```
uav_security_ml/
├── uav_project/          # Django project settings
│   ├── settings.py       # Configuration (dev/prod via env vars)
│   ├── urls.py           # Root URL configuration
│   ├── wsgi.py           # WSGI entry point (Gunicorn)
│   └── asgi.py           # ASGI entry point
├── core/                 # Main Django application
│   ├── models.py         # ORM models (User, Detection, Alert, etc.)
│   ├── views/            # View functions (auth, detection, analytics, etc.)
│   ├── urls.py           # URL patterns
│   ├── admin.py          # Django admin registrations
│   ├── decorators.py     # Role-based access decorators
│   ├── context_processors.py  # Template context
│   └── management/commands/   # Management commands (create_admin)
├── services/             # ML & training services
│   ├── ml_service.py     # Prediction service
│   └── training_service.py    # Model training service
├── templates/            # Django templates (Bootstrap 5)
├── static/               # CSS, JS, images
├── scripts/
│   ├── generate_dataset.py    # UAV dataset generator
│   ├── train_models.py        # Multi-algorithm training pipeline
│   ├── use_real_dataset.py    # Real dataset integration
│   └── model_comparison.py   # Benchmarking
├── ml_models/            # Trained model .pkl files
├── data/                 # Generated datasets (CSV)
├── manage.py             # Django CLI
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variable template
```

---

## 📊 Model Performance

| Model | Accuracy | Precision | Recall | F1-Score | Training Time |
|-------|----------|-----------|--------|----------|---------------|
| **Random Forest** | **100.00%** | **100.00%** | **100.00%** | **100.00%** | 0.6s |
| **XGBoost** | **100.00%** | **100.00%** | **100.00%** | **100.00%** | 0.3s |
| **Gradient Boosting** | **99.98%** | **99.98%** | **99.98%** | **99.98%** | 35s |
| **SVM (RBF)** | **100.00%** | **100.00%** | **100.00%** | **100.00%** | 1.9s |

🏆 **6-class multi-label classification** across Normal + 5 attack types

---

## 🚀 Quick Start

### 📋 Prerequisites

- Python 3.11+
- pip
- (Optional) PostgreSQL

### 💻 Local Development

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/shivansh-12315646/uav_security_ml.git
cd uav_security_ml
```

#### 2️⃣ Set Up Environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

#### 3️⃣ Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your settings (SECRET_KEY, etc.)
```

#### 4️⃣ Generate Dataset & Train Models

```bash
# Generate UAV security dataset (20,000 samples, 6 threat classes)
python scripts/generate_dataset.py

# Train all ML models (RF, SVM, GB, XGBoost)
python scripts/train_models.py
```

#### 5️⃣ Set Up Django & Run

```bash
# Apply database migrations
python manage.py migrate

# Create default admin user
python manage.py create_admin

# Collect static files (for production)
python manage.py collectstatic

# Start development server
python manage.py runserver
```

#### 6️⃣ Access the Application

- **Application**: http://localhost:8000
- **Django Admin**: http://localhost:8000/django-admin/
- **Default Login**: `admin` / `admin123`

---

## 📚 API Documentation

### REST API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/api/v1/detect/` | Run threat detection |
| `GET` | `/api/v1/history/` | Detection history |
| `GET` | `/api/v1/alerts/` | Security alerts |
| `GET` | `/api/v1/health/` | Health check |

### Example: Detect Threat

```bash
curl -X POST http://localhost:8000/api/v1/detect/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your-csrf-token" \
  --cookie "sessionid=your-session-id" \
  -d '{
    "altitude": 550,
    "speed": 95,
    "direction": 275,
    "signal_strength": 75,
    "distance_from_base": 12000,
    "flight_time": 600,
    "battery_level": 45,
    "temperature": 28,
    "vibration": 3.2,
    "gps_accuracy": 15
  }'
```

**Response:**
```json
{
  "success": true,
  "prediction": "GPS Spoofing",
  "confidence": 0.57,
  "threat_level": "Critical",
  "model_used": "RandomForest"
}
```

---

## 🔧 Technology Stack

### Backend
- **Framework**: Django 5.0
- **Database**: PostgreSQL (production) / SQLite (development)
- **Static Files**: WhiteNoise
- **WSGI Server**: Gunicorn

### Machine Learning
- **scikit-learn**: RandomForest, SVM, GradientBoosting
- **XGBoost**: Extreme Gradient Boosting
- **pandas / numpy**: Data manipulation
- **joblib**: Model persistence

### Frontend
- **Bootstrap 5**: Responsive UI
- **Chart.js**: Interactive charts
- **Font Awesome 6**: Icons

### DevOps
- **Gunicorn**: Production WSGI server
- **WhiteNoise**: Static file serving

---

## 🔑 User Roles

| Role | Dashboard | Detection | Alerts | Training | Admin |
|------|-----------|-----------|--------|----------|-------|
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Analyst** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Viewer** | ✅ | ❌ | ✅ | ❌ | ❌ |

Create users via Django Admin at `/django-admin/` or programmatically:
```bash
python manage.py create_admin   # Create default admin
python manage.py createsuperuser  # Interactive superuser creation
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Shivansh**
- GitHub: [@shivansh-12315646](https://github.com/shivansh-12315646)
- Project: [UAV Security ML](https://github.com/shivansh-12315646/uav_security_ml)

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ and Python + Django

</div>

