"""
ZeroTrust AI — Self-Heal API
POST /api/selfheal — Trigger Self-Healing Agent post-incident.
GET /api/health-score — Current system health score.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.models import SystemHealth
from agents.selfheal_agent import selfheal

router = APIRouter(prefix="/api", tags=["Self-Heal"])


@router.post("/selfheal")
async def trigger_selfheal(db: Session = Depends(get_db)):
    """Trigger the Self-Healing Agent to analyze and harden."""
    result = await selfheal.process(db=db)
    return result


@router.get("/health-score")
async def health_score(db: Session = Depends(get_db)):
    """Get current system health score."""
    health = db.query(SystemHealth).filter(SystemHealth.id == 1).first()
    if not health:
        return {"health_score": 100.0, "total_healed": 0}
    return {
        "health_score": health.health_score,
        "total_healed": health.total_healed,
        "last_updated": health.last_updated.isoformat() if health.last_updated else None,
    }
