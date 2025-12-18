import pandas as pd
import numpy as np
import sys
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

print("🚀 Starting Model Training...\n")

# Load dataset
print("📂 Loading dataset...")
if not os.path.exists('uav_data.csv'):
    print("❌ Error: uav_data.csv not found!")
    print("Please run: python generate_data.py first")
    sys.exit(1)

df = pd.read_csv('uav_data.csv')
print(f"✅ Loaded {len(df)} samples\n")

# Separate features and labels
# Feature columns (all columns except 'label')
feature_columns = ['packet_size', 'inter_arrival_time', 'packet_rate', 'connection_duration', 'failed_logins']
X = df[feature_columns]
y = df['label'].map({'normal': 0, 'attack': 1})

print(f"📊 Dataset Summary:")
print(f"   Total samples: {len(df)}")
print(f"   Normal: {(y == 0).sum()} ({(y == 0).sum()/len(df)*100:.1f}%)")
print(f"   Attack: {(y == 1).sum()} ({(y == 1).sum()/len(df)*100:.1f}%)\n")

# Split data: 80% train, 20% test
print("✂️ Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"   Training set: {len(X_train)} samples")
print(f"   Test set: {len(X_test)} samples\n")

# Feature scaling
print("⚖️ Normalizing features with StandardScaler...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("✅ Scaling complete\n")

# Train Random Forest model
print("🌲 Training Random Forest Classifier (100 trees)...")
# Use conservative CPU allocation to avoid resource contention
n_jobs = min(4, os.cpu_count() or 1)
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=n_jobs
)
model.fit(X_train_scaled, y_train)
print("✅ Training complete\n")

# Make predictions
print("🔮 Making predictions on test set...")
y_pred = model.predict(X_test_scaled)

# Evaluate model
accuracy = accuracy_score(y_test, y_pred)
print(f"\n🎯 MODEL PERFORMANCE:")
print(f"   Accuracy: {accuracy * 100:.2f}%\n")

print("📊 Detailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))

print("\n📉 Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(f"   True Negatives:  {cm[0][0]}")
print(f"   False Positives: {cm[0][1]}")
print(f"   False Negatives: {cm[1][0]}")
print(f"   True Positives:  {cm[1][1]}")

# Feature importance
print("\n🔍 Feature Importance:")
feature_names = ['packet_size', 'inter_arrival_time', 'packet_rate', 'connection_duration', 'failed_logins']
importances = model.feature_importances_
for name, importance in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True):
    print(f"   {name:25} {importance*100:.2f}%")

# Create model directory if it doesn't exist
if not os.path.exists('model'):
    os.makedirs('model')

# Save model and scaler
print("\n💾 Saving model and scaler...")
joblib.dump(model, 'model/uav_security_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
print("✅ Saved to: model/uav_security_model.pkl")
print("✅ Saved to: scaler.pkl")

print("\n🎉 Training Complete! Model is ready to use.")
print(f"\n📌 Remember this accuracy for your presentation: {accuracy * 100:.2f}%")
