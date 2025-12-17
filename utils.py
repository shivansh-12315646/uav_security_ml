import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

def load_dataset(path):
    return pd.read_csv(path)

def preprocess_data(df):
    X = df.drop("label", axis=1)
    y = df["label"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    joblib.dump(scaler, "scaler.pkl")
    return X_scaled, y
