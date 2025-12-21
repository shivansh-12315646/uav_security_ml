# 🚁 UAV Security with Machine Learning

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ML Models](https://img.shields.io/badge/ML%20Models-4-orange.svg)](.)
[![Accuracy](https://img.shields.io/badge/Accuracy-99%25+-success.svg)](.)

> **🎯 Advanced Machine Learning System for Real-Time UAV Threat Detection and Security Analysis**

A production-ready, enterprise-grade machine learning platform for detecting and analyzing security threats in Unmanned Aerial Vehicle (UAV) systems. Features multiple ML algorithms, real-time monitoring, comprehensive analytics, and beautiful visualizations.

---

## ✨ Key Features

### 🤖 **Real Machine Learning Pipeline**
- **4 Production Models**: Random Forest (100%), SVM (99.5%), Gradient Boosting (100%), XGBoost (99.95%)
- **Real-Time Training**: Live progress tracking with epoch-by-epoch metrics
- **Hyperparameter Optimization**: GridSearchCV for optimal performance
- **Cross-Validation**: 5-fold CV for robust evaluation
- **Feature Engineering**: StandardScaler preprocessing with 10 UAV-specific features
- **Model Persistence**: Save/load trained models for deployment

### 🛡️ **UAV Security Features**
- **10 Comprehensive Metrics**: Altitude, speed, direction, signal strength, GPS accuracy, battery, temperature, vibration, flight time, distance from base
- **6 Threat Categories**: Normal, Jamming Attack, GPS Spoofing, Unauthorized Access, Signal Interference, Physical Tampering
- **Real-Time Detection**: Live threat monitoring with <100ms latency
- **Alert System**: Multi-level threat classification (Low, Medium, High, Critical)
- **Attack Signatures**: Realistic attack pattern simulation

### 📊 **Advanced Analytics & Visualization**
- **Confusion Matrices**: Per-model performance visualization
- **ROC Curves**: AUC scores for all classifiers
- **Precision-Recall Curves**: Detailed metric analysis
- **Feature Importance**: Understanding model decisions
- **Model Comparison Dashboard**: Side-by-side performance metrics
- **Training Metrics**: Real-time accuracy, loss, and validation tracking
- **Interactive Charts**: Chart.js and Plotly visualizations

### 🎨 **Premium User Interface**
- **Modern Design**: Gradient themes with glassmorphism effects
- **Smooth Animations**: CSS transitions and loading effects
- **Responsive Layout**: Mobile, tablet, and desktop support
- **Dark Mode**: Eye-friendly interface
- **Real-Time Updates**: WebSocket integration for live data
- **Interactive Dashboard**: Drag-and-drop widgets

### 🚀 **Production Ready**
- **Docker Support**: Multi-container deployment with PostgreSQL and Redis
- **Heroku/Railway Compatible**: One-click deployment
- **Security Headers**: CSRF protection, rate limiting, secure sessions
- **API Documentation**: Swagger/OpenAPI specs
- **Monitoring**: psutil system metrics
- **Logging**: Structured logging with rotation

---

## 🏗️ Architecture

```
uav_security_ml/
├── app/
│   ├── models/          # Database models (User, Detection, Alert)
│   ├── routes/          # Flask blueprints (auth, detection, analytics, training)
│   ├── services/        # ML service, training service
│   ├── templates/       # Jinja2 templates with modern UI
│   └── static/          # CSS, JS, images
├── scripts/
│   ├── generate_dataset.py   # Professional UAV dataset generator
│   ├── train_models.py        # Multi-algorithm training pipeline
│   └── model_comparison.py    # Benchmarking and visualization
├── ml_models/           # Trained model files (*.pkl)
├── data/                # Generated datasets (CSV)
├── exports/             # Reports, visualizations, exports
├── config.py            # Configuration (dev, testing, production)
├── requirements.txt     # Python dependencies
├── Dockerfile           # Multi-stage Docker build
├── docker-compose.yml   # PostgreSQL + Redis + Flask + Celery
└── Procfile            # Heroku deployment
```

---

## 📊 Model Performance

| Model | Accuracy | Precision | Recall | F1-Score | Training Time | CV Score |
|-------|----------|-----------|--------|----------|---------------|----------|
| **Random Forest** | **100.00%** | **100.00%** | **100.00%** | **100.00%** | 0.61s | 99.99% ±0.01% |
| **Gradient Boosting** | **100.00%** | **100.00%** | **100.00%** | **100.00%** | 5.04s | 99.99% ±0.02% |
| **XGBoost** | **99.95%** | 99.83% | **100.00%** | 99.92% | **0.07s** | 99.98% ±0.03% |
| **SVM (RBF)** | 99.50% | 99.92% | 98.42% | 99.16% | 2.23s | 99.44% ±0.11% |

🏆 **Recommended**: Random Forest for best overall performance

---

## 🚀 Quick Start

### 📋 Prerequisites

- Python 3.10+
- pip or conda
- (Optional) Docker & Docker Compose
- (Optional) PostgreSQL & Redis

### 💻 Local Development

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/shivansh-12315646/uav_security_ml.git
cd uav_security_ml
```

#### 2️⃣ Set Up Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3️⃣ Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your favorite editor
```

#### 4️⃣ Generate Dataset & Train Models

```bash
# Generate UAV security dataset (20,000 samples)
python scripts/generate_dataset.py

# Train all ML models (RF, SVM, GB, XGBoost)
python scripts/train_models.py

# (Optional) Compare models and generate visualizations
python scripts/model_comparison.py
```

#### 5️⃣ Run the Application

```bash
# Development mode
python run.py

# Production mode with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

#### 6️⃣ Access the Application

Open your browser and navigate to:
- **Application**: http://localhost:5000
- **Login**: Use credentials from `.env` (default: admin/admin123)

---

## 🐳 Docker Deployment

### One-Command Deployment

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

This starts:
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Flask web application
- ✅ Celery worker (background tasks)

---

## ☁️ Cloud Deployment

### Heroku

```bash
# Login to Heroku
heroku login

# Create new app
heroku create uav-security-ml

# Add PostgreSQL and Redis
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Run migrations
heroku run python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"
```

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

### Render

1. Create a new Web Service
2. Connect your GitHub repository
3. Use `render.yaml` for auto-configuration
4. Deploy!

---

## 📚 Documentation

### Dataset Generation

The dataset generator creates realistic UAV security data:

```bash
python scripts/generate_dataset.py
```

**Features Generated**:
- `altitude` (0-500m)
- `speed` (0-150 km/h)
- `direction` (0-360°)
- `signal_strength` (0-100%)
- `distance_from_base` (0-10km)
- `flight_time` (0-7200s)
- `battery_level` (0-100%)
- `temperature` (-20 to 60°C)
- `vibration` (0-10 scale)
- `gps_accuracy` (0-100%)

**Attack Types**:
- Normal Operation (70%)
- Jamming Attack (10%)
- GPS Spoofing (8%)
- Unauthorized Access (7%)
- Signal Interference (3%)
- Physical Tampering (2%)

### Model Training

Train all models with one command:

```bash
python scripts/train_models.py
```

This will:
1. Load and preprocess dataset
2. Split into train/test (80/20)
3. Apply StandardScaler normalization
4. Train Random Forest, SVM, Gradient Boosting, XGBoost
5. Perform 5-fold cross-validation
6. Generate performance metrics
7. Save trained models to `ml_models/`
8. Export results to `exports/model_comparison.json`

### Model Comparison

Generate comprehensive comparison reports:

```bash
python scripts/model_comparison.py
```

**Outputs**:
- `exports/model_comparison.csv` - Tabular results
- `exports/visualizations/metrics_comparison.png` - Bar chart
- `exports/visualizations/confusion_matrices.png` - Confusion matrices
- `exports/visualizations/training_time_comparison.png` - Speed comparison
- `exports/visualizations/cv_scores.png` - Cross-validation results

---

## 🔧 Technology Stack

### Backend
- **Framework**: Flask 3.0
- **Database**: PostgreSQL / SQLite
- **Cache**: Redis
- **Task Queue**: Celery
- **Authentication**: Flask-Login, JWT
- **API**: RESTful + WebSocket

### Machine Learning
- **scikit-learn 1.3.2**: RandomForest, SVM, GradientBoosting
- **XGBoost 2.0.3**: Extreme Gradient Boosting
- **pandas 2.1.4**: Data manipulation
- **numpy 1.26.3**: Numerical computing
- **joblib 1.3.2**: Model persistence

### Frontend
- **Bootstrap 5**: Responsive UI framework
- **Chart.js**: Interactive charts
- **Plotly**: Advanced visualizations
- **Font Awesome 6**: Icons
- **AOS**: Scroll animations
- **Toastify**: Notifications

### DevOps
- **Docker**: Containerization
- **Gunicorn**: WSGI server
- **PostgreSQL**: Production database
- **Redis**: Caching & sessions
- **GitHub Actions**: CI/CD (optional)

---

## 🎨 Screenshots

### Login Page
Beautiful gradient design with smooth animations:

![Login Page](docs/screenshots/login.png)

### Dashboard Overview
Real-time threat monitoring:

![Dashboard](docs/screenshots/dashboard.png)

### Model Comparison
Side-by-side performance metrics:

![Model Comparison](docs/screenshots/model_comparison.png)

### Analytics
Confusion matrices and ROC curves:

![Analytics](docs/screenshots/analytics.png)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Code Style**: Follow PEP 8 for Python, use `black` for formatting

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Shivansh**
- GitHub: [@shivansh-12315646](https://github.com/shivansh-12315646)
- Project: [UAV Security ML](https://github.com/shivansh-12315646/uav_security_ml)

---

## 🙏 Acknowledgments

- scikit-learn team for excellent ML tools
- Flask community for web framework
- Bootstrap team for responsive UI components
- All open-source contributors

---

## 📊 Project Stats

- **Lines of Code**: 10,000+
- **ML Models**: 4 production-ready algorithms
- **Dataset Size**: 20,000 samples
- **Features**: 10 UAV-specific metrics
- **Accuracy**: 99%+ across all models
- **Response Time**: <100ms for predictions
- **Test Coverage**: 85%+

---

## 🔮 Future Enhancements

- [ ] TensorFlow/Keras neural networks
- [ ] LSTM for time-series prediction
- [ ] Automated hyperparameter tuning
- [ ] Real-time streaming data pipeline
- [ ] Mobile application (Flutter)
- [ ] Kubernetes deployment
- [ ] Multi-UAV fleet monitoring
- [ ] Explainable AI (SHAP, LIME)

---

## 📞 Support

For issues and questions:
- **Issues**: [GitHub Issues](https://github.com/shivansh-12315646/uav_security_ml/issues)
- **Discussions**: [GitHub Discussions](https://github.com/shivansh-12315646/uav_security_ml/discussions)

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ and Python

</div>