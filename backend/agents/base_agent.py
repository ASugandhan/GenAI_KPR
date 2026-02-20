"""
ZeroTrust AI — Base Agent
Abstract base class for all AI agents.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from utils.logger import EventLogger


class BaseAgent(ABC):
    """Base class for all ZeroTrust AI agents."""

    def __init__(self, name: str):
        self.name = name
        self.logger = EventLogger(name)
        self.created_at = datetime.utcnow()
        self._action_count = 0

    @abstractmethod
    async def process(self, data: dict, db=None) -> dict:
        """Process input data — must be implemented by subclasses."""
        pass

    def log(self, action: str, details: dict = None):
        """Log an agent action."""
        self._action_count += 1
        return self.logger.log_agent_action(self.name, action, details)

    def get_status(self) -> dict:
        """Get agent status summary."""
        return {
            "agent": self.name,
            "actions_taken": self._action_count,
            "uptime_seconds": (datetime.utcnow() - self.created_at).total_seconds(),
        }
