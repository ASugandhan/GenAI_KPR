"""
ZeroTrust AI — Logs API
GET /api/logs — Paginated threat event logs.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.database import get_db
from core.models import Event

router = APIRouter(prefix="/api", tags=["Logs"])


@router.get("/logs")
async def get_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    severity: str = Query(None),
    db: Session = Depends(get_db),
):
    """Get paginated threat event logs."""
    query = db.query(Event).order_by(Event.timestamp.desc())

    if severity:
        query = query.filter(Event.severity == severity.upper())

    total = query.count()
    events = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "events": [
            {
                "id": e.id,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "src_ip": e.src_ip,
                "dst_ip": e.dst_ip,
                "port": e.port,
                "protocol": e.protocol,
                "attack_type": e.attack_type,
                "confidence": e.confidence,
                "severity": e.severity,
                "agent": e.agent,
                "reasoning": e.reasoning,
                "resolved": e.resolved,
            }
            for e in events
        ],
    }
