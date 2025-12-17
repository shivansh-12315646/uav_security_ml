# 🚀 Quick Start Guide - UAV Security ML

## Prerequisites
- Python 3.8+ installed
- Git installed
- Terminal/Command Prompt access

## Step-by-Step Instructions

### 1️⃣ Clone and Navigate to Directory
```bash
git clone https://github.com/shivansh-12315646/uav_security_ml.git
cd uav_security_ml
```

### 2️⃣ Create Virtual Environment
**On Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
*This will take 2-3 minutes*

### 4️⃣ Set Up Environment Variables
```bash
# Copy the example environment file
cp .env.example .env
```

*Note: The default settings work for local development - no changes needed!*

### 5️⃣ Run the Application
```bash
python run.py
```

You should see output like:
```
* Serving Flask app 'app'
* Debug mode: on
* Running on http://127.0.0.1:5000
```

### 6️⃣ Access the Application

1. Open your web browser
2. Navigate to: **http://localhost:5000**
3. You'll see the login page

### 7️⃣ Login with Demo Credentials

**Username:** `admin`  
**Password:** `admin123`

---

## 📱 What You Can Do After Login

### ✅ **Dashboard**
- View real-time metrics (Total Detections, Threats, Alerts)
- See detection trends chart
- Monitor recent activity

### ✅ **Live Detection**
Navigate to "Live Detection" from the sidebar:
1. Enter UAV communication parameters:
   - **Packet Size**: e.g., `512` (normal) or `1600` (attack)
   - **Inter-arrival Time**: e.g., `0.02` (normal) or `0.50` (attack)
   - **Packet Rate**: e.g., `120` (normal) or `900` (attack)
   - **Connection Duration**: e.g., `15` (normal) or `3` (attack)
   - **Failed Logins**: e.g., `0` (normal) or `7` (attack)
2. Click "Detect Threat"
3. View the prediction result with confidence score

### ✅ **Detection History**
- View all past detections
- Filter by prediction type (Normal/Threat)
- Filter by threat level (Low/Medium/High/Critical)

### ✅ **Alerts**
- View active security alerts
- Acknowledge and resolve alerts
- Track alert status

### ✅ **Admin Panel** (Admin only)
- Manage users (activate/deactivate)
- View system statistics
- Access audit logs

### ✅ **Dark/Light Theme**
Click the moon/sun icon in the top navbar to toggle between themes

---

## 🧪 Testing the Detection System

### Example 1: Normal UAV Traffic
```
Packet Size: 512
Inter-arrival Time: 0.02
Packet Rate: 120
Connection Duration: 15
Failed Logins: 0
```
**Expected Result:** Normal (Low threat)

### Example 2: Attack Pattern
```
Packet Size: 1600
Inter-arrival Time: 0.50
Packet Rate: 900
Connection Duration: 3
Failed Logins: 7
```
**Expected Result:** Threat (High/Critical)

---

## 🐳 Alternative: Run with Docker

If you prefer Docker:

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access at http://localhost:5000
```

Stop with:
```bash
docker-compose down
```

---

## 🔑 User Roles

The system has three user roles:

1. **Admin** (`admin`) - Full system access
   - User management
   - System settings
   - All analytics and detections

2. **Analyst** - Detection operations
   - Run detections
   - View analytics
   - Manage alerts

3. **Viewer** - Read-only access
   - View dashboards
   - View reports
   - No detection or admin capabilities

---

## 📊 Using the API

You can also interact via REST API:

### Health Check
```bash
curl http://localhost:5000/api/v1/health
```

### Detect Threat (requires authentication)
```bash
curl -X POST http://localhost:5000/api/v1/detect \
  -H "Content-Type: application/json" \
  -d '{
    "packet_size": 1600,
    "inter_arrival": 0.50,
    "packet_rate": 900,
    "duration": 3,
    "failed_logins": 7
  }'
```

---

## ❌ Troubleshooting

### Port Already in Use
If port 5000 is busy:
1. Edit `run.py`
2. Change `port=5000` to `port=5001`
3. Access at `http://localhost:5001`

### Database Errors
Reset the database:
```bash
rm uav_security.db
python run.py
```

### Module Not Found
Ensure virtual environment is activated:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows
```

Then reinstall:
```bash
pip install -r requirements.txt
```

### Flask App Not Starting
Check Python version:
```bash
python --version  # Should be 3.8 or higher
```

---

## 🛑 Stopping the Application

Press `Ctrl+C` in the terminal where the app is running.

---

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API endpoints
- Customize the `.env` file for your environment
- Set up email notifications
- Deploy to production with Docker

---

## 💡 Need Help?

- Check the [README.md](README.md) for comprehensive documentation
- Review the code in `app/routes/` to understand the endpoints
- Look at `app/models/` to understand the database schema
- Check logs in the terminal for error messages

---

**🎉 You're all set! Enjoy using UAV Security ML!**
