from flask import Flask, render_template, request
import joblib
import numpy as np
from datetime import datetime

app = Flask(__name__)

model = joblib.load("model/uav_security_model.pkl")
scaler = joblib.load("scaler.pkl")

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
