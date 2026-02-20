"""
ZeroTrust AI — ML Inference
Loads saved models and predicts attack type + confidence for a packet.
"""
import os
import joblib
import numpy as np

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

# Lazy-loaded models
_models = {}


def _load_models():
    """Load all saved models (lazy, once)."""
    if _models:
        return
    _models["xgb"] = joblib.load(os.path.join(MODELS_DIR, "xgboost_clf.pkl"))
    _models["iso"] = joblib.load(os.path.join(MODELS_DIR, "iso_forest.pkl"))
    _models["scaler"] = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
    _models["label_enc"] = joblib.load(os.path.join(MODELS_DIR, "label_encoder.pkl"))
    _models["proto_enc"] = joblib.load(os.path.join(MODELS_DIR, "protocol_encoder.pkl"))


def predict(packet: dict) -> dict:
    """
    Run ML inference on a single packet.
    Returns: {attack_type, confidence, is_anomaly, probabilities}
    """
    _load_models()

    # Encode protocol
    protocol = packet.get("protocol", "TCP")
    try:
        proto_enc = _models["proto_enc"].transform([protocol])[0]
    except ValueError:
        proto_enc = 0  # unknown protocol

    port = packet.get("port", 80)
    pkt_bytes = packet.get("bytes", 0)
    duration = packet.get("duration", 0.01)
    packet_count = packet.get("packet_count", 1)
    bytes_per_packet = pkt_bytes / (packet_count + 1)
    packets_per_sec = packet_count / (duration + 0.001)

    features = np.array([[port, pkt_bytes, duration, packet_count,
                          proto_enc, bytes_per_packet, packets_per_sec]])

    # Scale
    X_scaled = _models["scaler"].transform(features)

    # XGBoost prediction
    probabilities = _models["xgb"].predict_proba(X_scaled)[0]
    predicted_class = int(np.argmax(probabilities))
    confidence = float(probabilities[predicted_class])
    attack_type = _models["label_enc"].inverse_transform([predicted_class])[0]

    # Isolation Forest anomaly check
    anomaly_score = _models["iso"].decision_function(X_scaled)[0]
    is_anomaly = _models["iso"].predict(X_scaled)[0] == -1

    return {
        "attack_type": attack_type,
        "confidence": round(confidence, 4),
        "is_anomaly": bool(is_anomaly),
        "anomaly_score": round(float(anomaly_score), 4),
        "probabilities": {
            _models["label_enc"].inverse_transform([i])[0]: round(float(p), 4)
            for i, p in enumerate(probabilities)
        },
    }
