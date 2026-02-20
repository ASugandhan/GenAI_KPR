"""
ZeroTrust AI — Traffic Stream API
GET /api/traffic/stream — SSE stream of live simulated packets.
"""
import asyncio
import json
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from ml.simulator import generate_packet
from config import PACKETS_PER_SECOND, ATTACK_PROBABILITY

router = APIRouter(prefix="/api/traffic", tags=["Traffic"])


async def _packet_generator():
    """Async generator that yields packets as SSE events."""
    while True:
        packet = generate_packet(attack_probability=ATTACK_PROBABILITY)
        yield {
            "event": "packet",
            "data": json.dumps(packet, default=str),
        }
        await asyncio.sleep(1.0 / PACKETS_PER_SECOND)


@router.get("/stream")
async def stream_traffic():
    """Server-Sent Events stream of live network packets."""
    return EventSourceResponse(_packet_generator())
