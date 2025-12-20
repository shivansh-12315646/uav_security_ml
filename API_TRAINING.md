# API Documentation - Training Endpoints

## Training API Reference

This document describes the RESTful API endpoints for model training and management.

---

## Authentication

All training endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

**Note:** Training endpoints are restricted to admin users only.

---

## Endpoints

### 1. Upload Dataset

Upload a CSV dataset for training or analysis.

**Endpoint:** `POST /training/upload-dataset`

**Headers:**
```
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**Request Body:**
```
dataset: <CSV file>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "filepath": "/path/to/uploaded/dataset.csv",
  "total_samples": 13000,
  "normal_samples": 10000,
  "attack_samples": 3000,
  "features": 5,
  "feature_stats": {
    "packet_size": {
      "mean": 650.5,
      "std": 300.2,
      "min": 480.0,
      "max": 1800.0,
      "25%": 500.0,
      "50%": 520.0,
      "75%": 1500.0
    },
    ...
  },
  "null_values": {
    "packet_size": 0,
    "inter_arrival_time": 0,
    ...
  }
}
```

**Error Response:** `400 Bad Request`
```json
{
  "success": false,
  "error": "No file uploaded"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/training/upload-dataset \
  -H "Authorization: Bearer your-token" \
  -F "dataset=@uav_data.csv"
```

---

### 2. Start Training

Start training a new ML model.

**Endpoint:** `POST /training/start-training`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "algorithm": "RandomForest",
  "dataset_path": "/path/to/dataset.csv",
  "test_size": 0.2,
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": null,
    "random_state": 42
  }
}
```

**Parameters:**
- `algorithm` (required): One of: `RandomForest`, `XGBoost`, `SVM`, `NeuralNetwork`, `GradientBoosting`
- `dataset_path` (required): Path to uploaded dataset
- `test_size` (optional): Test split ratio (0.1 - 0.4), default: 0.2
- `hyperparameters` (optional): Algorithm-specific parameters

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Training started successfully",
  "training_id": "train_1702401234"
}
```

**Error Response:** `400 Bad Request`
```json
{
  "success": false,
  "error": "Unsupported algorithm: InvalidAlgo"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/training/start-training \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "RandomForest",
    "dataset_path": "/uploads/uav_data.csv",
    "test_size": 0.2
  }'
```

**WebSocket Events:**

Connect to `/training` namespace to receive real-time updates:

```javascript
const socket = io('/training');

socket.on('training_started', (data) => {
  console.log('Training started:', data.training_id);
});

socket.on('training_update', (data) => {
  console.log('Progress:', data.progress + '%');
  console.log('Stage:', data.stage);
  console.log('Message:', data.message);
});

socket.on('training_complete', (data) => {
  console.log('Accuracy:', data.metrics.accuracy);
  console.log('F1 Score:', data.metrics.f1_score);
  console.log('Model saved:', data.model_path);
});

socket.on('training_error', (data) => {
  console.error('Error:', data.error);
});
```

---

### 3. List Models

Get list of all trained models.

**Endpoint:** `GET /training/models`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "models": [
    {
      "id": 1,
      "name": "RandomForest",
      "version": "1.0",
      "accuracy": 0.9542,
      "precision": 0.9601,
      "recall": 0.9523,
      "f1_score": 0.9562,
      "is_active": true,
      "file_path": "/models/RandomForest_20231220_143025.pkl",
      "created_at": "2023-12-20T14:30:25",
      "trained_by": 1,
      "training_dataset_size": 13000,
      "training_duration": 45.3,
      "description": "Trained on 13000 samples"
    },
    ...
  ]
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/training/models \
  -H "Authorization: Bearer your-token"
```

---

### 4. Activate Model

Activate a specific model for use in predictions.

**Endpoint:** `POST /training/models/<model_id>/activate`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Model activated successfully"
}
```

**Error Response:** `404 Not Found`
```json
{
  "success": false,
  "error": "Model not found"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/training/models/1/activate \
  -H "Authorization: Bearer your-token"
```

---

### 5. Delete Model

Delete a trained model.

**Endpoint:** `DELETE /training/models/<model_id>`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Model deleted successfully"
}
```

**Error Response:** `404 Not Found`
```json
{
  "success": false,
  "error": "Model not found"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:5000/training/models/1 \
  -H "Authorization: Bearer your-token"
```

---

### 6. Compare Models

Compare performance metrics of multiple models.

**Endpoint:** `POST /training/compare-models`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "model_ids": [1, 2, 3]
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "comparison": {
    "models": [
      {
        "id": 1,
        "name": "RandomForest",
        "accuracy": 0.9542,
        "precision": 0.9601,
        "recall": 0.9523,
        "f1_score": 0.9562,
        ...
      },
      ...
    ],
    "best_accuracy": "RandomForest",
    "best_f1": "XGBoost",
    "best_precision": "SVM",
    "best_recall": "RandomForest"
  }
}
```

**Error Response:** `400 Bad Request`
```json
{
  "success": false,
  "error": "Please select at least 2 models to compare"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/training/compare-models \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"model_ids": [1, 2, 3]}'
```

---

### 7. Analyze Dataset

Analyze dataset quality and statistics.

**Endpoint:** `POST /training/analyze-dataset`

**Headers:**
```
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**Request Body:**
```
dataset: <CSV file>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "total_samples": 13000,
  "features": 5,
  "normal_samples": 10000,
  "attack_samples": 3000,
  "feature_stats": {
    "packet_size": {
      "mean": 650.5,
      "std": 300.2,
      "min": 480.0,
      "max": 1800.0,
      "25%": 500.0,
      "50%": 520.0,
      "75%": 1500.0
    },
    ...
  },
  "null_values": {
    "packet_size": 0,
    "inter_arrival_time": 0,
    "packet_rate": 0,
    "connection_duration": 0,
    "failed_logins": 0
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/training/analyze-dataset \
  -H "Authorization: Bearer your-token" \
  -F "dataset=@uav_data.csv"
```

---

## Algorithm-Specific Hyperparameters

### Random Forest

```json
{
  "n_estimators": 100,
  "max_depth": null,
  "min_samples_split": 2,
  "min_samples_leaf": 1,
  "random_state": 42,
  "n_jobs": -1
}
```

### XGBoost

```json
{
  "n_estimators": 100,
  "max_depth": 6,
  "learning_rate": 0.1,
  "random_state": 42,
  "n_jobs": -1,
  "use_label_encoder": false,
  "eval_metric": "logloss"
}
```

### SVM

```json
{
  "kernel": "rbf",
  "C": 1.0,
  "gamma": "scale",
  "probability": true,
  "random_state": 42
}
```

### Neural Network (MLP)

```json
{
  "hidden_layer_sizes": [100, 50],
  "activation": "relu",
  "solver": "adam",
  "max_iter": 500,
  "random_state": 42
}
```

### Gradient Boosting

```json
{
  "n_estimators": 100,
  "learning_rate": 0.1,
  "max_depth": 3,
  "random_state": 42
}
```

---

## WebSocket Events

### Connection

Connect to the `/training` namespace:

```javascript
const socket = io('/training');
```

### Events

#### `training_started`

Emitted when training begins.

**Data:**
```json
{
  "training_id": "train_1702401234",
  "algorithm": "RandomForest",
  "timestamp": "2023-12-20T14:30:25.123456"
}
```

#### `training_update`

Emitted during training progress.

**Data:**
```json
{
  "stage": "training",
  "progress": 60,
  "message": "Training RandomForest model..."
}
```

**Stages:**
- `loading`: Loading dataset
- `preprocessing`: Preprocessing features
- `splitting`: Splitting data
- `scaling`: Scaling features
- `initializing`: Initializing model
- `training`: Training model
- `evaluating`: Evaluating performance
- `saving`: Saving model

#### `training_complete`

Emitted when training successfully completes.

**Data:**
```json
{
  "training_id": "train_1702401234",
  "progress": 100,
  "message": "Training completed successfully!",
  "metrics": {
    "accuracy": 0.9542,
    "precision": 0.9601,
    "recall": 0.9523,
    "f1_score": 0.9562,
    "roc_auc": 0.9834
  },
  "confusion_matrix": [[2100, 50], [40, 410]],
  "training_duration": 45.3,
  "model_path": "/models/RandomForest_20231220_143025.pkl",
  "scaler_path": "/models/scaler_RandomForest_20231220_143025.pkl",
  "dataset_size": {
    "train": 10400,
    "test": 2600,
    "total": 13000
  }
}
```

#### `training_error`

Emitted when training fails.

**Data:**
```json
{
  "training_id": "train_1702401234",
  "error": "Error message describing what went wrong"
}
```

---

## Error Codes

- `400`: Bad Request - Invalid parameters
- `401`: Unauthorized - Missing or invalid authentication
- `403`: Forbidden - Insufficient permissions (not admin)
- `404`: Not Found - Resource not found
- `500`: Internal Server Error - Server-side error

---

## Rate Limiting

Training endpoints have the following rate limits:

- Upload dataset: 10 requests per minute
- Start training: 5 requests per minute
- Other endpoints: 60 requests per minute

---

## Best Practices

1. **Always validate dataset before training**
   - Use the analyze-dataset endpoint first
   - Check for missing values and class imbalance

2. **Monitor training progress**
   - Connect to WebSocket for real-time updates
   - Don't start multiple training sessions simultaneously

3. **Compare models before activation**
   - Train multiple algorithms
   - Use comparison endpoint to identify best performer
   - Consider multiple metrics, not just accuracy

4. **Backup models**
   - Download important model files
   - Keep track of model metadata

5. **Use appropriate hyperparameters**
   - Start with defaults
   - Tune based on dataset characteristics
   - Document custom hyperparameters

---

## Examples

### Complete Training Workflow

```python
import requests
import socketio

API_URL = "http://localhost:5000"
TOKEN = "your-jwt-token"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# 1. Upload dataset
files = {'dataset': open('uav_data.csv', 'rb')}
response = requests.post(
    f"{API_URL}/training/upload-dataset",
    headers=HEADERS,
    files=files
)
data = response.json()
dataset_path = data['filepath']

# 2. Connect to WebSocket for real-time updates
sio = socketio.Client()

@sio.on('training_complete', namespace='/training')
def on_complete(data):
    print(f"Training complete! Accuracy: {data['metrics']['accuracy']}")

sio.connect(API_URL, namespaces=['/training'])

# 3. Start training
response = requests.post(
    f"{API_URL}/training/start-training",
    headers=HEADERS,
    json={
        "algorithm": "RandomForest",
        "dataset_path": dataset_path,
        "test_size": 0.2
    }
)
print(response.json())

# 4. Wait for completion (handled by WebSocket)
sio.wait()

# 5. List models
response = requests.get(
    f"{API_URL}/training/models",
    headers=HEADERS
)
models = response.json()['models']

# 6. Activate best model
best_model_id = models[0]['id']
response = requests.post(
    f"{API_URL}/training/models/{best_model_id}/activate",
    headers=HEADERS
)
print(response.json())
```

---

## Support

For API issues or questions:
- GitHub Issues: https://github.com/shivansh-12315646/uav_security_ml/issues
- Email: shivanshsep16@gmail.com
