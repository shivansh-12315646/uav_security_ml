import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from utils import load_dataset, preprocess_data

os.makedirs("model", exist_ok=True)

df = load_dataset("data/uav_data.csv")
X, y = preprocess_data(df)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

joblib.dump(model, "model/uav_security_model.pkl")

print(classification_report(y_test, model.predict(X_test)))
