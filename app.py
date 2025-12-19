"""
Simple Flask Application - DEMO VERSION
========================================

This is a simplified demonstration version of the UAV Security ML system.
It provides basic threat detection functionality but lacks many features
of the full application.

IMPORTANT: This is for demo/testing purposes only.
For the full application with all features, use run.py instead.

Key Differences from Full Application (run.py):
- Uses in-memory history storage (lost on restart)
- No user authentication or authorization
- No database persistence
- No alerts system
- No analytics dashboard
- No admin panel
- No API endpoints
- Missing CSRF protection (not recommended for production)

To run the full application, use:
    python run.py

This simple version is useful for:
- Quick testing and demonstrations
- Learning the basic ML prediction flow
- Development and debugging of core ML functionality
"""
from flask import Flask, render_template, request
import joblib
import numpy as np
from datetime import datetime

app = Flask(__name__)

# Note: Direct model loading - not recommended for production
# The full application uses ml_service for better model management
model = joblib.load("model/uav_security_model.pkl")
scaler = joblib.load("scaler.pkl")

# In-memory history - data is lost when app restarts
# The full application uses database persistence via DetectionHistory model
history = []

@app.route("/")
def overview():
    return render_template("overview.html", total=len(history))

@app.route("/detect", methods=["GET", "POST"])
def detect():
    prediction = None
    if request.method == "POST":
        features = [
            float(request.form["packet_size"]),
            float(request.form["inter_arrival"]),
            float(request.form["packet_rate"]),
            float(request.form["duration"]),
            float(request.form["failed_logins"])
        ]
        scaled = scaler.transform([features])
        prediction = model.predict(scaled)[0]

        history.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "features": features,
            "result": prediction
        })

    return render_template("detect.html", prediction=prediction)

@app.route("/analytics")
def analytics():
    return render_template("analytics.html")

@app.route("/algorithms")
def algorithms():
    return render_template("algorithms.html")

@app.route("/history")
def history_page():
    return render_template("history.html", history=history)

if __name__ == "__main__":
    app.run(debug=True)
