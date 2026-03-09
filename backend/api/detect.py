"""
ZeroTrust AI - Detection API
POST /api/detect - Submit packet into autonomous 4-agent pipeline.
GET /api/incidents/{incident_id} - Fetch incident state.
GET /api/incidents - Recent incident states.
"""
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field

from core.autonomous_runtime import runtime
from utils.auth import get_current_user
from utils.rate_limit import limiter

router = APIRouter(prefix="/api", tags=["Detection"])


class PacketInput(BaseModel):
    src_ip: str = Field(..., example="192.168.1.45")
    dst_ip: str = Field(..., example="10.0.0.1")
    port: int = Field(..., example=22)
    protocol: str = Field(..., example="TCP")
    bytes: int = Field(..., example=8420)
    duration: float = Field(..., example=0.3)
    packet_count: int = Field(..., example=847)


@router.post("/detect")
@limiter.limit("100/minute")
async def detect_threat(
    request: Request,
    packet: PacketInput,
    user: str = Depends(get_current_user),
):
    """Submit packet to autonomous pipeline and wait for mitigation verdict."""
    packet_dict = packet.model_dump()
    result = await runtime.submit_packet(packet_dict, wait_for_result=True, timeout_seconds=6.0)
    return result


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str, user: str = Depends(get_current_user)):
    incident = runtime.get_incident(incident_id)
    if not incident:
        return {"error": "Incident not found", "incident_id": incident_id}
    return incident


@router.get("/incidents")
async def list_incidents(
    limit: int = Query(20, ge=1, le=100),
    user: str = Depends(get_current_user),
):
    return {"incidents": runtime.list_recent_incidents(limit=limit)}
