"""
ZeroTrust AI — Configuration
Loads all environment variables with sensible defaults.
"""
import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


# --- Gemini / LLM ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
OFFLINE_MODE = os.getenv("OFFLINE_MODE", "true").lower() == "true"
MOCK_LLM = os.getenv("MOCK_LLM", "true").lower() == "true"
LLM_CONFIDENCE_MIN = float(os.getenv("LLM_CONFIDENCE_MIN", "0.4"))
LLM_CONFIDENCE_MAX = float(os.getenv("LLM_CONFIDENCE_MAX", "0.8"))
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "3"))

# --- Database ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./zerotrust.db")

# --- Self-Healing ---
SELFHEAL_TRIGGER_SEVERITY = os.getenv("SELFHEAL_TRIGGER_SEVERITY", "HIGH")
SYSTEM_HEALTH_INITIAL = float(os.getenv("SYSTEM_HEALTH_INITIAL", "100.0"))
PACKETS_PER_SECOND = int(os.getenv("PACKETS_PER_SECOND", "2"))
ATTACK_PROBABILITY = float(os.getenv("ATTACK_PROBABILITY", "0.15"))
PACKET_SOURCE = os.getenv("PACKET_SOURCE", "simulator").lower()  # simulator | live
CAPTURE_INTERFACE = os.getenv("CAPTURE_INTERFACE", "")
CAPTURE_BPF_FILTER = os.getenv("CAPTURE_BPF_FILTER", "")
AUTO_APPLY_RULES = os.getenv("AUTO_APPLY_RULES", "false").lower() == "true"
EXCLUDE_SELF_TRAFFIC = os.getenv("EXCLUDE_SELF_TRAFFIC", "true").lower() == "true"
SELF_TRAFFIC_PORTS = [
    int(p.strip())
    for p in os.getenv("SELF_TRAFFIC_PORTS", "3000,8000").split(",")
    if p.strip().isdigit()
]
THREAT_PENALTY_COOLDOWN_SECONDS = int(os.getenv("THREAT_PENALTY_COOLDOWN_SECONDS", "30"))
RULE_COOLDOWN_SECONDS = int(os.getenv("RULE_COOLDOWN_SECONDS", "120"))
ANALYST_COOLDOWN_SECONDS = int(os.getenv("ANALYST_COOLDOWN_SECONDS", "30"))
SELFHEAL_COOLDOWN_SECONDS = int(os.getenv("SELFHEAL_COOLDOWN_SECONDS", "300"))
MAX_ACTIVE_RULES = int(os.getenv("MAX_ACTIVE_RULES", "500"))

# --- Frontend ---
NEXT_PUBLIC_API_URL = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:8000")

# --- Safety ---
PROTECTED_IPS = ["10.0.0.1", "192.168.1.1", "127.0.0.1"]  # Never block these
