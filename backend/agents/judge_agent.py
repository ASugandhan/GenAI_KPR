"""
ZeroTrust AI - Judge Agent
Second-stage adjudication: validates detector verdicts and assigns response priority.
"""
from agents.base_agent import BaseAgent


SEVERITY_PRIORITY = {
    "CRITICAL": "P1",
    "HIGH": "P2",
    "MEDIUM": "P3",
    "LOW": "P4",
}

ATTACK_CATEGORY = {
    "brute_force": "credential_attack",
    "port_scan": "reconnaissance",
    "ddos": "availability_attack",
    "exploit": "exploitation",
    "c2_beacon": "command_and_control",
    "normal": "benign",
}


class JudgeAgent(BaseAgent):
    """Judges threat impact and normalizes classification metadata."""

    def __init__(self):
        super().__init__("judge")

    async def process(self, data: dict, db=None) -> dict:
        attack_type = data.get("attack_type", "normal")
        severity = str(data.get("severity", "LOW")).upper()
        confidence = float(data.get("confidence", 0.0))
        is_threat = bool(data.get("is_threat", False))

        category = ATTACK_CATEGORY.get(attack_type, "unknown")
        priority = SEVERITY_PRIORITY.get(severity, "P4")

        # If detector confidence is very low, downgrade confidence in decision.
        decision_confidence = min(1.0, confidence + 0.05) if is_threat else confidence
        if confidence < 0.25 and is_threat:
            severity = "LOW"
            priority = "P4"

        self.log(
            "judgement_complete",
            {
                "attack_type": attack_type,
                "severity": severity,
                "priority": priority,
                "category": category,
            },
        )

        return {
            **data,
            "severity": severity,
            "priority": priority,
            "category": category,
            "decision_confidence": round(decision_confidence, 4),
            "judged_by": self.name,
        }


judge = JudgeAgent()

