# UAV Security ML - Enterprise-Grade Threat Detection System

<div align="center">

![UAV Security](https://img.shields.io/badge/UAV-Security-blue)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**A professional, enterprise-level UAV security detection system with modern GUI, comprehensive features, and production-ready architecture.**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [API](#api) • [Contributing](#contributing)

</div>

---

## 🚀 Features

### Core Capabilities
- **🤖 Advanced ML Detection**: Multiple algorithms (Random Forest, XGBoost, SVM, Neural Networks)
- **🔐 Enterprise Security**: JWT authentication, RBAC, session management, audit logging
- **📊 Real-time Monitoring**: Live threat detection dashboard with WebSocket updates
- **📈 Advanced Analytics**: Interactive visualizations with Chart.js and Plotly
- **🚨 Alert Management**: Multi-channel notifications (Email, Slack, in-app)
- **👥 User Management**: Role-based access control (Admin, Analyst, Viewer)
- **📁 Batch Processing**: CSV upload for bulk threat detection
- **🎨 Modern UI**: Responsive Bootstrap 5 design with dark/light themes

### Technical Highlights
- **Blueprint Architecture**: Modular, scalable Flask application structure
- **SQLAlchemy ORM**: Robust database management with migrations
- **Service Layer**: Clean separation of concerns with dedicated services
- **RESTful API**: Complete API with Swagger documentation
- **Caching**: Redis integration for performance optimization
- **Production Ready**: Docker support, health checks, comprehensive logging

---

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 💻 System Requirements

- **Python**: 3.8 or higher
- **Database**: SQLite (default) or PostgreSQL (production)
- **Optional**: Redis for caching and session management
- **OS**: Linux, macOS, or Windows

---

## 🔧 Installation

### Quick Start (Local Development)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/uav_security_ml.git
   cd uav_security_ml
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python run.py
   # Database will be created automatically on first run
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`
   - Default admin credentials:
     - Username: `admin`
     - Password: `admin123`

---

## ⚙️ Configuration

### Environment Variables

Edit the `.env` file to configure your application:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///uav_security.db

# Admin User
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@uavsecurity.com
ADMIN_PASSWORD=change-this-password

# Email Settings (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-password
```

### Database Configuration

**SQLite (Default - Development)**
```env
DATABASE_URL=sqlite:///uav_security.db
```

**PostgreSQL (Production)**
```env
DATABASE_URL=postgresql://username:password@localhost:5432/uav_security
```

---

## 📖 Usage

### Application Entry Points

This project provides two entry points for running the application:

#### **1. run.py (RECOMMENDED - Full Application)**

The primary entry point for the complete, production-ready application with all features:

```bash
python run.py
```

**Features:**
- ✅ User authentication and authorization (login required)
- ✅ Database persistence (all data saved to database)
- ✅ Alert system with severity levels
- ✅ Advanced analytics dashboard
- ✅ Admin panel for user management
- ✅ RESTful API endpoints
- ✅ CSRF protection for all forms
- ✅ Real-time updates via WebSocket
- ✅ Rate limiting and security features
- ✅ Session management

**Access:** `http://localhost:5000`

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

#### **2. app.py (DEMO - Simplified Version)**

A lightweight demo version for testing basic ML functionality:

```bash
python app.py
```

**Features:**
- ⚠️ No authentication (open access)
- ⚠️ In-memory storage only (data lost on restart)
- ⚠️ No database persistence
- ⚠️ Limited to basic detection routes
- ⚠️ No CSRF protection
- ✅ Quick testing of ML models
- ✅ Simpler codebase for learning

**Use Cases:**
- Quick demonstrations
- Learning the basic ML prediction flow
- Development/debugging of core ML functionality
- Testing without database setup

**⚠️ WARNING:** `app.py` is NOT suitable for production use. Always use `run.py` for production deployments.

### User Roles

1. **Admin** - Full system access, user management, system settings
2. **Analyst** - Detection operations, analytics, alert management
3. **Viewer** - Read-only access to dashboards and reports

### Main Features

#### 1. Live Threat Detection
- Navigate to **Live Detection** from the sidebar
- Enter UAV communication parameters
- Click **Detect Threat** to analyze
- View prediction results with confidence scores

#### 2. Detection History
- View all past detections
- Filter by prediction type or threat level
- Paginated results with search functionality

#### 3. Analytics Dashboard
- Real-time metrics cards
- Interactive charts and visualizations
- Detection trends over time
- Model performance metrics

#### 4. Alert Management
- View active security alerts
- Acknowledge and resolve alerts
- Filter by status and severity
- Assignment workflow for team collaboration

#### 5. Admin Panel (Admin Only)
- User management (create, activate, deactivate users)
- System settings
- Audit log viewer
- Database statistics

---

## 🏗️ Project Structure

```
uav_security_ml/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models/                  # Database models
│   │   ├── user.py
│   │   ├── detection.py
│   │   ├── alert.py
│   │   ├── ml_model.py
│   │   └── audit.py
│   ├── routes/                  # Blueprint routes
│   │   ├── auth.py
│   │   ├── main.py
│   │   ├── detection.py
│   │   ├── analytics.py
│   │   ├── alerts.py
│   │   ├── admin.py
│   │   └── api.py
│   ├── services/                # Business logic
│   │   └── ml_service.py
│   ├── utils/                   # Utility functions
│   │   ├── decorators.py
│   │   └── helpers.py
│   ├── static/                  # CSS, JS, images
│   └── templates/               # Jinja2 templates
├── ml_models/                   # ML models storage
├── config.py                    # Configuration classes
├── run.py                       # Development entry point
├── wsgi.py                      # Production entry point
└── requirements.txt             # Python dependencies
```

---

## 🔌 API Documentation

### Authentication

All API endpoints require authentication. Include JWT token in header:
```
Authorization: Bearer <your-jwt-token>
```

### Endpoints

#### POST /api/v1/detect
Perform single UAV threat detection.

**Request Body:**
```json
{
  "packet_size": 512.0,
  "inter_arrival": 0.02,
  "packet_rate": 120.0,
  "duration": 15.0,
  "failed_logins": 0
}
```

**Response:**
```json
{
  "success": true,
  "detection_id": 123,
  "prediction": "Normal",
  "confidence": 0.95,
  "threat_level": "Low",
  "model_used": "RandomForest"
}
```

#### GET /api/v1/history
Retrieve detection history with pagination.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Results per page (default: 20)

**Response:**
```json
{
  "detections": [...],
  "total": 150,
  "pages": 8,
  "current_page": 1
}
```

#### GET /api/v1/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "UAV Security ML",
  "version": "2.0.0"
}
```

---

## 🛠️ Development

### Running in Development Mode

```bash
python run.py
```

The application will run on `http://localhost:5000` with debug mode enabled.

### Database Migrations

```bash
# Initialize migrations (first time only)
flask db init

# Create a migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade
```

### Code Style

This project follows PEP 8 style guidelines. Format your code with:

```bash
black .
flake8 .
```

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

---

## 🚀 Deployment

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Production with Gunicorn

```bash
# Install Gunicorn (included in requirements.txt)
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

### Environment Setup

1. Set `FLASK_ENV=production` in `.env`
2. Use a strong `SECRET_KEY`
3. Configure PostgreSQL database
4. Set up Redis for caching
5. Configure email settings for notifications

---

## 🐛 Troubleshooting

### Database Errors

If you encounter database errors:
```bash
# Reset database
rm uav_security.db
python run.py
```

### Import Errors

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Port Already in Use

Change the port in `run.py`:
```python
socketio.run(app, debug=True, host='0.0.0.0', port=5001)
```

---

## 📊 Dataset Generation

This project uses a **synthetic dataset** that simulates realistic UAV network traffic patterns.

### Generate Dataset

```bash
# Generate 13,000 samples (10,000 normal + 3,000 attack)
python generate_data.py
```

**Dataset Features:**
- `packet_size`: Size of network packets (bytes)
- `inter_arrival_time`: Time between packets (milliseconds)
- `packet_rate`: Number of packets per second
- `connection_duration`: Length of connection session (seconds)
- `failed_logins`: Number of failed authentication attempts
- `label`: Classification (normal/attack)

**Normal Traffic Characteristics:**
- Packet Size: 480-550 bytes
- Inter-Arrival Time: 0.01-0.05ms
- Packet Rate: 100-150 packets/sec
- Duration: 15-25 seconds
- Failed Logins: 0-1

**Attack Traffic Characteristics:**
- Packet Size: 1400-1800 bytes (flooding)
- Inter-Arrival Time: 0.40-0.70ms (irregular)
- Packet Rate: 800-1000 packets/sec (DDoS)
- Duration: 1-5 seconds (hit-and-run)
- Failed Logins: 5-15 (brute force)

### Train Model

```bash
# Train Random Forest model with 80-20 split
python train_model.py
```

**Expected Output:**
- Training samples: 10,400
- Test samples: 2,600
- Model Accuracy: ~95%
- Saved to: `model/uav_security_model.pkl`

## 🎓 Academic Note

This synthetic dataset is created for **educational purposes** to demonstrate machine learning methodology. In production deployment, this would be replaced with real UAV network traffic data collected from actual drone communication systems.

The dataset generation is based on research of network intrusion detection patterns and UAV communication protocols, ensuring realistic value ranges and attack characteristics.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Authors

- **Shivansh Sharma** - Initial work

---

## 🙏 Acknowledgments

- Flask framework and community
- Bootstrap 5 for UI components
- Chart.js for data visualization
- scikit-learn for ML capabilities

---

## 📧 Contact

For questions or support, please open an issue on GitHub or contact: shivanshsep16@gmail.com

---

<div align="center">

**Made with ❤️ for UAV Security**

[Report Bug](https://github.com/yourusername/uav_security_ml/issues) • [Request Feature](https://github.com/yourusername/uav_security_ml/issues)

</div>
