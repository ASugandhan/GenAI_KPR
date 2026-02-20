"""
ZeroTrust AI — ML Training Script
Trains XGBoost classifier + Isolation Forest anomaly detector.
Run once: python ml/train.py
"""
import os
import sys
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.ensemble import IsolationForest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ml.simulator import generate_training_data

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")


def train():
    """Train and save all ML models."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    print("📊 Generating training data (5000 samples)...")
    raw_data = generate_training_data(n_samples=5000, attack_ratio=0.3)
    df = pd.DataFrame(raw_data)

    # --- Feature engineering ---
    features = ["port", "bytes", "duration", "packet_count"]
    # Encode protocol as numeric
    protocol_encoder = LabelEncoder()
    df["protocol_enc"] = protocol_encoder.fit_transform(df["protocol"])
    features.append("protocol_enc")

    # Derived features
    df["bytes_per_packet"] = df["bytes"] / (df["packet_count"] + 1)
    df["packets_per_sec"] = df["packet_count"] / (df["duration"] + 0.001)
    features.extend(["bytes_per_packet", "packets_per_sec"])

    X = df[features].values
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["attack_type"])

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # --- Train XGBoost Classifier ---
    print("🤖 Training XGBoost classifier...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    xgb_clf = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric="mlogloss",
        random_state=42,
    )
    xgb_clf.fit(X_train, y_train)

    train_acc = xgb_clf.score(X_train, y_train)
    test_acc = xgb_clf.score(X_test, y_test)
    print(f"   Train Accuracy: {train_acc:.4f}")
    print(f"   Test Accuracy:  {test_acc:.4f}")

    # --- Train Isolation Forest (anomaly detection) ---
    print("🔍 Training Isolation Forest anomaly detector...")
    iso_forest = IsolationForest(
        n_estimators=100, contamination=0.15, random_state=42
    )
    iso_forest.fit(X_scaled)

    # --- Save models ---
    joblib.dump(xgb_clf, os.path.join(MODELS_DIR, "xgboost_clf.pkl"))
    joblib.dump(iso_forest, os.path.join(MODELS_DIR, "iso_forest.pkl"))
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
    joblib.dump(label_encoder, os.path.join(MODELS_DIR, "label_encoder.pkl"))
    joblib.dump(protocol_encoder, os.path.join(MODELS_DIR, "protocol_encoder.pkl"))

    print(f"\n✅ All models saved to {MODELS_DIR}/")
    print(f"   Classes: {list(label_encoder.classes_)}")
    print(f"   Protocols: {list(protocol_encoder.classes_)}")


if __name__ == "__main__":
    train()
