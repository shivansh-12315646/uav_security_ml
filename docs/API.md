# 📚 API Documentation

## Overview

The UAV Security ML API provides RESTful endpoints for threat detection, model management, and analytics. All endpoints return JSON responses and support authentication via JWT tokens or session cookies.

**Base URL**: `http://localhost:5000/api` (development)

---

## Authentication

### Login
Authenticate and receive session cookie or JWT token.

**Endpoint**: `POST /auth/login`

**Request Body**:
```json
{
  "username": "admin",
  "password": "admin123",
  "remember": false
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@uavsecurity.com",
    "role": "admin"
  }
}
```

### Logout
End current session.

**Endpoint**: `POST /auth/logout`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## Detection API

### Real-Time Threat Detection
Submit UAV metrics for real-time threat analysis.

**Endpoint**: `POST /api/detect`

**Authentication**: Required

**Request Body**:
```json
{
  "altitude": 250.5,
  "speed": 45.2,
  "direction": 180.0,
  "signal_strength": 85.5,
  "distance_from_base": 2500.0,
  "flight_time": 1800,
  "battery_level": 65.0,
  "temperature": 25.0,
  "vibration": 1.5,
  "gps_accuracy": 92.0,
  "model": "RandomForest"  // Optional, defaults to active model
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "detection_id": 123,
  "prediction": "Normal",  // or "Threat"
  "confidence": 0.9876,
  "threat_level": "Low",  // Low, Medium, High, Critical
  "model_used": "RandomForest",
  "timestamp": "2025-12-21T06:15:30.123456",
  "features": {
    "altitude": 250.5,
    "speed": 45.2,
    // ... all features
  }
}
```

**Response** (400 Bad Request):
```json
{
  "success": false,
  "error": "Missing required field: altitude"
}
```

### Batch Detection
Analyze multiple samples at once.

**Endpoint**: `POST /api/detect/batch`

**Request Body**:
```json
{
  "samples": [
    {
      "altitude": 250.5,
      "speed": 45.2,
      // ... all features
    },
    {
      "altitude": 100.0,
      "speed": 120.0,
      // ... all features
    }
  ],
  "model": "RandomForest"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "results": [
    {
      "index": 0,
      "prediction": "Normal",
      "confidence": 0.9876,
      "threat_level": "Low"
    },
    {
      "index": 1,
      "prediction": "Threat",
      "confidence": 0.8542,
      "threat_level": "High"
    }
  ],
  "summary": {
    "total": 2,
    "normal": 1,
    "threats": 1
  }
}
```

### Detection History
Retrieve historical detection records.

**Endpoint**: `GET /api/detections`

**Query Parameters**:
- `page` (int): Page number (default: 1)
- `per_page` (int): Results per page (default: 20, max: 100)
- `start_date` (string): Filter from date (ISO 8601)
- `end_date` (string): Filter to date (ISO 8601)
- `prediction` (string): Filter by prediction ("Normal" or "Threat")
- `model` (string): Filter by model name

**Response** (200 OK):
```json
{
  "success": true,
  "detections": [
    {
      "id": 123,
      "prediction": "Normal",
      "confidence": 0.9876,
      "threat_level": "Low",
      "model_used": "RandomForest",
      "timestamp": "2025-12-21T06:15:30.123456",
      "features": {...}
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8
  }
}
```

### Get Detection by ID
Retrieve a specific detection record.

**Endpoint**: `GET /api/detections/:id`

**Response** (200 OK):
```json
{
  "success": true,
  "detection": {
    "id": 123,
    "prediction": "Normal",
    "confidence": 0.9876,
    "threat_level": "Low",
    "model_used": "RandomForest",
    "timestamp": "2025-12-21T06:15:30.123456",
    "features": {...}
  }
}
```

---

## Model Management API

### List Available Models
Get all loaded ML models.

**Endpoint**: `GET /api/models`

**Response** (200 OK):
```json
{
  "success": true,
  "models": [
    {
      "name": "RandomForest",
      "active": true,
      "accuracy": 1.0,
      "loaded": true
    },
    {
      "name": "SVM",
      "active": false,
      "accuracy": 0.995,
      "loaded": true
    },
    {
      "name": "GradientBoosting",
      "active": false,
      "accuracy": 1.0,
      "loaded": true
    },
    {
      "name": "XGBoost",
      "active": false,
      "accuracy": 0.9995,
      "loaded": true
    }
  ],
  "active_model": "RandomForest"
}
```

### Switch Active Model
Change the active model for predictions.

**Endpoint**: `POST /api/models/activate`

**Request Body**:
```json
{
  "model_name": "XGBoost"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Active model changed to XGBoost",
  "previous_model": "RandomForest",
  "current_model": "XGBoost"
}
```

### Model Performance
Get detailed performance metrics for a model.

**Endpoint**: `GET /api/models/:name/performance`

**Response** (200 OK):
```json
{
  "success": true,
  "model": "RandomForest",
  "metrics": {
    "accuracy": 1.0,
    "precision": 1.0,
    "recall": 1.0,
    "f1_score": 1.0,
    "roc_auc": 1.0,
    "cv_mean": 0.9999,
    "cv_std": 0.0001,
    "training_time": 0.61
  },
  "confusion_matrix": [[2800, 0], [0, 1200]],
  "feature_importance": {
    "Altitude": 0.15,
    "Speed": 0.12,
    "Signal Strength": 0.18,
    // ... other features
  }
}
```

### Compare Models
Get side-by-side comparison of all models.

**Endpoint**: `GET /api/models/comparison`

**Response** (200 OK):
```json
{
  "success": true,
  "comparison": [
    {
      "model": "RandomForest",
      "accuracy": 1.0,
      "precision": 1.0,
      "recall": 1.0,
      "f1_score": 1.0,
      "training_time": 0.61
    },
    {
      "model": "XGBoost",
      "accuracy": 0.9995,
      "precision": 0.9983,
      "recall": 1.0,
      "f1_score": 0.9992,
      "training_time": 0.07
    }
    // ... other models
  ],
  "best_model": "RandomForest",
  "fastest_model": "XGBoost"
}
```

---

## Alerts API

### List Alerts
Get all security alerts.

**Endpoint**: `GET /api/alerts`

**Query Parameters**:
- `page` (int): Page number
- `per_page` (int): Results per page
- `severity` (string): Filter by severity (Low, Medium, High, Critical)
- `status` (string): Filter by status (Active, Acknowledged, Resolved)

**Response** (200 OK):
```json
{
  "success": true,
  "alerts": [
    {
      "id": 45,
      "title": "High Threat Detected",
      "description": "GPS spoofing attack detected on UAV-001",
      "severity": "High",
      "status": "Active",
      "detection_id": 123,
      "created_at": "2025-12-21T06:15:30.123456",
      "acknowledged_at": null
    }
  ],
  "pagination": {...}
}
```

### Acknowledge Alert
Mark an alert as acknowledged.

**Endpoint**: `POST /api/alerts/:id/acknowledge`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Alert acknowledged",
  "alert": {
    "id": 45,
    "status": "Acknowledged",
    "acknowledged_at": "2025-12-21T06:20:00.000000"
  }
}
```

### Resolve Alert
Mark an alert as resolved.

**Endpoint**: `POST /api/alerts/:id/resolve`

**Request Body** (optional):
```json
{
  "resolution_notes": "False positive - maintenance activity"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Alert resolved",
  "alert": {
    "id": 45,
    "status": "Resolved",
    "resolved_at": "2025-12-21T06:25:00.000000",
    "resolution_notes": "False positive - maintenance activity"
  }
}
```

---

## Analytics API

### Dashboard Statistics
Get overview statistics for dashboard.

**Endpoint**: `GET /api/analytics/dashboard`

**Query Parameters**:
- `period` (string): Time period (today, week, month, year)

**Response** (200 OK):
```json
{
  "success": true,
  "statistics": {
    "total_detections": 15000,
    "total_threats": 4500,
    "active_alerts": 12,
    "threat_rate": 30.0,
    "average_confidence": 0.9456,
    "detections_today": 150,
    "threats_today": 45,
    "critical_alerts": 3
  },
  "trend": {
    "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "normal": [100, 120, 115, 130, 125, 95, 105],
    "threats": [30, 35, 32, 40, 38, 28, 33]
  }
}
```

### Dataset Statistics
Get statistics about the training dataset.

**Endpoint**: `GET /api/analytics/dataset`

**Response** (200 OK):
```json
{
  "success": true,
  "dataset": {
    "total_samples": 20000,
    "features": 10,
    "normal_samples": 14000,
    "threat_samples": 6000,
    "threat_distribution": {
      "jamming_attack": 2000,
      "gps_spoofing": 1600,
      "unauthorized_access": 1400,
      "signal_interference": 600,
      "physical_tampering": 400
    },
    "feature_statistics": {
      "altitude": {"min": 0.13, "max": 599.31, "mean": 227.20, "std": 112.42},
      "speed": {"min": 0.07, "max": 149.86, "mean": 48.28, "std": 25.72}
      // ... other features
    }
  }
}
```

---

## Training API

### Start Training
Initiate model training (admin only).

**Endpoint**: `POST /api/training/start`

**Request Body**:
```json
{
  "model_type": "RandomForest",  // or "all" for all models
  "dataset_file": "data/uav_security_dataset.csv",
  "test_size": 0.2,
  "cross_validation": true,
  "cv_folds": 5
}
```

**Response** (202 Accepted):
```json
{
  "success": true,
  "message": "Training started",
  "task_id": "training-abc123",
  "status_url": "/api/training/status/training-abc123"
}
```

### Training Status
Check status of ongoing training.

**Endpoint**: `GET /api/training/status/:task_id`

**Response** (200 OK):
```json
{
  "success": true,
  "task_id": "training-abc123",
  "status": "running",  // queued, running, completed, failed
  "progress": 60,
  "current_step": "Training XGBoost",
  "completed_models": ["RandomForest", "SVM", "GradientBoosting"],
  "estimated_time_remaining": 45  // seconds
}
```

---

## Error Responses

All endpoints may return these error responses:

### 400 Bad Request
```json
{
  "success": false,
  "error": "Invalid request parameters",
  "details": {
    "altitude": "Must be between 0 and 500"
  }
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "success": false,
  "error": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "retry_after": 60  // seconds
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

---

## Rate Limiting

API requests are rate limited to prevent abuse:

- **Default**: 200 requests per day, 50 requests per hour
- **Authenticated**: Higher limits based on user role
- **Admin**: Unlimited requests

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 200
X-RateLimit-Remaining: 195
X-RateLimit-Reset: 1640000000
```

---

## WebSocket API

### Real-Time Updates
Connect to WebSocket for live detection updates.

**Endpoint**: `ws://localhost:5000/socket.io/`

**Events**:

#### `connect`
Connection established.

#### `detection_update`
New detection event.
```json
{
  "type": "detection",
  "detection": {
    "id": 123,
    "prediction": "Threat",
    "confidence": 0.8765,
    "timestamp": "2025-12-21T06:15:30.123456"
  }
}
```

#### `training_progress`
Training progress update.
```json
{
  "type": "training",
  "task_id": "training-abc123",
  "progress": 75,
  "current_step": "Training XGBoost",
  "message": "Model 3 of 4 completed"
}
```

#### `alert_created`
New alert created.
```json
{
  "type": "alert",
  "alert": {
    "id": 45,
    "severity": "High",
    "title": "High Threat Detected"
  }
}
```

---

## Code Examples

### Python (requests)
```python
import requests

# Login
response = requests.post(
    'http://localhost:5000/auth/login',
    json={'username': 'admin', 'password': 'admin123'}
)
session = response.cookies

# Make detection
data = {
    'altitude': 250.5,
    'speed': 45.2,
    'direction': 180.0,
    'signal_strength': 85.5,
    'distance_from_base': 2500.0,
    'flight_time': 1800,
    'battery_level': 65.0,
    'temperature': 25.0,
    'vibration': 1.5,
    'gps_accuracy': 92.0
}

response = requests.post(
    'http://localhost:5000/api/detect',
    json=data,
    cookies=session
)

result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']}")
```

### JavaScript (fetch)
```javascript
// Login
const loginResponse = await fetch('http://localhost:5000/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  }),
  credentials: 'include'
});

// Make detection
const data = {
  altitude: 250.5,
  speed: 45.2,
  direction: 180.0,
  signal_strength: 85.5,
  distance_from_base: 2500.0,
  flight_time: 1800,
  battery_level: 65.0,
  temperature: 25.0,
  vibration: 1.5,
  gps_accuracy: 92.0
};

const detectResponse = await fetch('http://localhost:5000/api/detect', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(data),
  credentials: 'include'
});

const result = await detectResponse.json();
console.log(`Prediction: ${result.prediction}`);
console.log(`Confidence: ${result.confidence}`);
```

### cURL
```bash
# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -c cookies.txt

# Make detection
curl -X POST http://localhost:5000/api/detect \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "altitude": 250.5,
    "speed": 45.2,
    "direction": 180.0,
    "signal_strength": 85.5,
    "distance_from_base": 2500.0,
    "flight_time": 1800,
    "battery_level": 65.0,
    "temperature": 25.0,
    "vibration": 1.5,
    "gps_accuracy": 92.0
  }'
```

---

## Versioning

The API uses URL versioning. Current version: **v1**

Future versions will be available at `/api/v2/`, `/api/v3/`, etc.

---

## Support

For API issues or questions:
- **Documentation**: [GitHub Wiki](https://github.com/shivansh-12315646/uav_security_ml/wiki)
- **Issues**: [GitHub Issues](https://github.com/shivansh-12315646/uav_security_ml/issues)
