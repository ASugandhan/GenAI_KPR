"""
ZeroTrust AI — Structured Logger
Provides consistent logging for all agents and API events.
"""
import logging
import json
from datetime import datetime

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class EventLogger:
    """Structured event logger for agents and API."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._events = []

    def log_event(self, event_type: str, data: dict, level: str = "info"):
        """Log a structured event."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "source": self.logger.name,
            "event_type": event_type,
            **data,
        }
        self._events.append(entry)

        msg = json.dumps(entry, default=str)
        getattr(self.logger, level, self.logger.info)(msg)
        return entry

    def log_threat(self, packet: dict, verdict: dict):
        """Log a threat detection event."""
        return self.log_event("threat_detected", {
            "src_ip": packet.get("src_ip"),
            "dst_ip": packet.get("dst_ip"),
            "attack_type": verdict.get("attack_type"),
            "confidence": verdict.get("confidence"),
            "severity": verdict.get("severity", "UNKNOWN"),
        }, level="warning")

    def log_rule(self, rule: dict):
        """Log a rule generation event."""
        return self.log_event("rule_generated", {
            "action": rule.get("action"),
            "rule_text": rule.get("rule_text"),
        })

    def log_agent_action(self, agent: str, action: str, details: dict = None):
        """Log an agent action."""
        return self.log_event("agent_action", {
            "agent": agent,
            "action": action,
            **(details or {}),
        })

    def get_recent_events(self, n: int = 50) -> list:
        """Get last N events."""
        return self._events[-n:]


# Global loggers for each component
sentinel_logger = EventLogger("sentinel")
tactician_logger = EventLogger("tactician")
analyst_logger = EventLogger("analyst")
selfheal_logger = EventLogger("selfheal")
api_logger = EventLogger("api")
