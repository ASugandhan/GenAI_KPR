"""
ZeroTrust AI — Trust API
GET /api/trust — All device trust scores.
GET /api/trust/{device_id} — Single device trust score.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.trust_engine import get_all_scores, get_device_score

router = APIRouter(prefix="/api/trust", tags=["Trust"])


@router.get("")
async def all_trust_scores(db: Session = Depends(get_db)):
    """Get all device trust scores."""
    scores = get_all_scores(db)
    return {
        "devices": [
            {
                "device_id": s.device_id,
                "ip_address": s.ip_address,
                "trust_score": s.trust_score,
                "anomaly_count": s.anomaly_count,
                "last_threat": s.last_threat.isoformat() if s.last_threat else None,
                "last_updated": s.last_updated.isoformat() if s.last_updated else None,
            }
            for s in scores
        ]
    }


@router.get("/{device_id}")
async def device_trust_score(device_id: str, db: Session = Depends(get_db)):
    """Get a single device's trust score."""
    score = get_device_score(db, device_id)
    if not score:
        raise HTTPException(status_code=404, detail="Device not found")
    return {
        "device_id": score.device_id,
        "ip_address": score.ip_address,
        "trust_score": score.trust_score,
        "anomaly_count": score.anomaly_count,
        "last_threat": score.last_threat.isoformat() if score.last_threat else None,
        "last_updated": score.last_updated.isoformat() if score.last_updated else None,
    }
