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

# --- Frontend ---
NEXT_PUBLIC_API_URL = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:8000")

# --- Safety ---
PROTECTED_IPS = ["10.0.0.1", "192.168.1.1", "127.0.0.1"]  # Never block these
