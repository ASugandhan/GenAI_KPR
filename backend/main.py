"""
ZeroTrust AI — FastAPI Main Application
Entry point: mounts all routers, CORS, startup/shutdown events.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import init_db

# Import routers
from api.traffic import router as traffic_router
from api.detect import router as detect_router
from api.rules import router as rules_router
from api.trust import router as trust_router
from api.summarize import router as summarize_router
from api.selfheal import router as selfheal_router
from api.logs import router as logs_router


app = FastAPI(
    title="ZeroTrust AI",
    description="Multi-Agent AI-Powered Firewall — Real-time threat detection, classification, and response",
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

# Mount all routers
app.include_router(traffic_router)
app.include_router(detect_router)
app.include_router(rules_router)
app.include_router(trust_router)
app.include_router(summarize_router)
app.include_router(selfheal_router)
app.include_router(logs_router)


@app.on_event("startup")
async def startup():
    """Initialize database tables on startup."""
    init_db()
    print("🛡️  ZeroTrust AI — Backend started!")
    print("📊  Database initialized")
    print("🔗  API docs at http://localhost:8000/docs")


@app.get("/api/health", tags=["System"])
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "ZeroTrust AI",
        "version": "1.0.0",
    }
