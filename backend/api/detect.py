"""
ZeroTrust AI — Detection API
POST /api/detect — Run packet through Sentinel + Tactician pipeline.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from core.database import get_db
from agents.sentinel_agent import sentinel
from agents.tactician_agent import tactician

router = APIRouter(prefix="/api", tags=["Detection"])


class PacketInput(BaseModel):
    src_ip: str = Field(..., example="192.168.1.45")
    dst_ip: str = Field(..., example="10.0.0.1")
    port: int = Field(..., example=22)
    protocol: str = Field(..., example="TCP")
    bytes: int = Field(..., example=8420)
    duration: float = Field(..., example=0.3)
    packet_count: int = Field(..., example=847)


from utils.auth import get_current_user

from main import limiter
from fastapi import Request

@router.post("/detect")
@limiter.limit("100/minute")
async def detect_threat(request: Request, packet: PacketInput, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Run a packet through the full detection pipeline."""
    packet_dict = packet.model_dump()

    # Step 1: Sentinel detection
    verdict = await sentinel.process(packet_dict)

    # Step 2: Tactician response (only if threat)
    response = {}
    if verdict.get("is_threat"):
        response = await tactician.process(verdict, db=db, packet=packet_dict)

    return {
        **verdict,
        "rule_generated": response.get("rule_generated"),
        "trust_score_after": response.get("trust_score_after"),
        "action": response.get("action", "none"),
    }
