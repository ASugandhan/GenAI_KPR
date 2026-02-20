"""
ZeroTrust AI — Trust Engine
Zero Trust scoring: 0–100, decay on threats, recovery over time.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from core.models import TrustScore
import uuid

# Severity → trust score penalty
SEVERITY_PENALTY = {
    "CRITICAL": 30,
    "HIGH": 15,
    "MEDIUM": 8,
    "LOW": 3,
}

# Trust score → action threshold
ACTION_THRESHOLDS = {
    (70, 100): "monitor",
    (40, 69): "rate_limit",
    (20, 39): "block_temp",
    (0, 19): "block_perm",
}


def get_or_create_device(db: Session, ip_address: str) -> TrustScore:
    """Get existing device trust record or create a new one."""
    device = db.query(TrustScore).filter(TrustScore.ip_address == ip_address).first()
    if not device:
        device = TrustScore(
            device_id=str(uuid.uuid4()),
            ip_address=ip_address,
            trust_score=100.0,
            anomaly_count=0,
            last_updated=datetime.utcnow(),
        )
        db.add(device)
        db.commit()
        db.refresh(device)
    return device


def apply_penalty(db: Session, ip_address: str, severity: str) -> TrustScore:
    """Apply trust penalty based on threat severity."""
    device = get_or_create_device(db, ip_address)
    penalty = SEVERITY_PENALTY.get(severity, 3)

    device.trust_score = max(0.0, device.trust_score - penalty)
    device.anomaly_count += 1
    device.last_threat = datetime.utcnow()
    device.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(device)
    return device


def recover_trust(db: Session, ip_address: str, minutes_clean: int = 1) -> TrustScore:
    """Recover trust score: +1 per clean minute, max 100."""
    device = get_or_create_device(db, ip_address)
    recovery = min(minutes_clean, 100.0 - device.trust_score)
    device.trust_score = min(100.0, device.trust_score + recovery)
    device.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(device)
    return device


def get_recommended_action(trust_score: float) -> str:
    """Get recommended action based on trust score."""
    for (low, high), action in ACTION_THRESHOLDS.items():
        if low <= trust_score <= high:
            return action
    return "block_perm"


def get_all_scores(db: Session) -> list:
    """Get all device trust scores."""
    return db.query(TrustScore).all()


def get_device_score(db: Session, device_id: str) -> TrustScore:
    """Get a single device's trust score."""
    return db.query(TrustScore).filter(TrustScore.device_id == device_id).first()
