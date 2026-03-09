"""
ZeroTrust AI - FastAPI Main Application
Entry point: mounts all routers, CORS, startup/shutdown events.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from api.auth import router as auth_router
from api.detect import router as detect_router
from api.logs import router as logs_router
from api.rules import router as rules_router
from api.selfheal import router as selfheal_router
from api.summarize import router as summarize_router
from api.traffic import router as traffic_router
from api.trust import router as trust_router
from core.autonomous_runtime import runtime
from core.database import init_db
from core.live_capture import live_capture
from config import PACKET_SOURCE
from utils.rate_limit import limiter

app = FastAPI(
    title="ZeroTrust AI",
    description="Multi-Agent AI-Powered Firewall - Real-time threat detection, classification, and response",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount all routers
app.include_router(traffic_router)
app.include_router(detect_router)
app.include_router(rules_router)
app.include_router(trust_router)
app.include_router(summarize_router)
app.include_router(selfheal_router)
app.include_router(logs_router)
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])


@app.on_event("startup")
async def startup():
    """Initialize database tables and autonomous workers on startup."""
    init_db()
    await runtime.start()
    if PACKET_SOURCE == "live":
        await live_capture.start(
            lambda packet: runtime.submit_packet(packet, wait_for_result=False)
        )
    print("ZeroTrust AI backend started")


@app.on_event("shutdown")
async def shutdown():
    """Shutdown autonomous workers cleanly."""
    await live_capture.stop()
    await runtime.stop()


@app.get("/api/health", tags=["System"])
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "ZeroTrust AI",
        "version": "1.0.0",
        "autonomous_runtime": "running",
        "packet_source": PACKET_SOURCE,
        "live_capture_running": live_capture.running,
    }
