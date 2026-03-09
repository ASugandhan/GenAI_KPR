"""
ZeroTrust AI - Traffic Stream API
GET /api/traffic/stream - SSE stream of simulated/live packets.
"""
import asyncio
import json

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from config import ATTACK_PROBABILITY, PACKETS_PER_SECOND, PACKET_SOURCE
from core.live_capture import live_capture
from ml.simulator import generate_packet

router = APIRouter(prefix="/api/traffic", tags=["Traffic"])


async def _packet_generator():
    """Async generator that yields packets as SSE events."""
    if PACKET_SOURCE == "live":
        async for packet in live_capture.packet_stream():
            yield {"event": "packet", "data": json.dumps(packet, default=str)}
        return

    while True:
        packet = generate_packet(attack_probability=ATTACK_PROBABILITY)
        yield {"event": "packet", "data": json.dumps(packet, default=str)}
        await asyncio.sleep(1.0 / PACKETS_PER_SECOND)


@router.get("/stream")
async def stream_traffic():
    """Server-Sent Events stream of network packets."""
    return EventSourceResponse(_packet_generator())


@router.get("/capture/status")
async def capture_status():
    """Status of live packet capture service."""
    return {
        "packet_source": PACKET_SOURCE,
        "capture": live_capture.status(),
    }


@router.get("/capture/interfaces")
async def capture_interfaces():
    """List interfaces visible to scapy for packet capture."""
    return {
        "interfaces": live_capture.list_interfaces(),
        "hint": "Set CAPTURE_INTERFACE to one exact value from this list and restart backend.",
    }
