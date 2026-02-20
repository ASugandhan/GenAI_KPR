"""
ZeroTrust AI — Tactician Agent
Generates proportional response rules based on threat severity and trust score.
"""
import uuid
from datetime import datetime
from agents.base_agent import BaseAgent
from core.trust_engine import get_or_create_device, apply_penalty, get_recommended_action
from core.rule_engine import create_rule
from core.models import Event
from config import PROTECTED_IPS


class TacticianAgent(BaseAgent):
    """Generates adaptive firewall rules and proportional responses."""

    def __init__(self):
        super().__init__("tactician")

    async def process(self, verdict: dict, db=None, packet: dict = None) -> dict:
        """
        Process a Sentinel verdict and generate appropriate response.
        1. Check trust score
        2. Determine action (proportional to severity + trust level)
        3. Generate firewall rule
        4. Persist event + rule
        """
        if not verdict.get("is_threat"):
            return {"action": "none", "reason": "No threat detected"}

        if db is None:
            return {"action": "error", "reason": "No database session"}

        src_ip = packet.get("src_ip", "unknown") if packet else "unknown"
        dst_ip = packet.get("dst_ip", "unknown") if packet else "unknown"
        port = packet.get("port", 0) if packet else 0
        protocol = packet.get("protocol", "TCP") if packet else "TCP"
        attack_type = verdict.get("attack_type", "unknown")
        severity = verdict.get("severity", "LOW")
        confidence = verdict.get("confidence", 0.0)

        self.log("processing_verdict", {"attack_type": attack_type, "severity": severity})

        # Step 1: Apply trust penalty
        device = apply_penalty(db, src_ip, severity)
        trust_score = device.trust_score

        # Step 2: Determine action
        action = get_recommended_action(trust_score)

        # Safety constraint: never permanently block protected IPs
        if src_ip in PROTECTED_IPS and action == "block_perm":
            action = "rate_limit"
            self.log("safety_override", {"reason": "Protected IP", "ip": src_ip})

        # Step 3: Persist the event
        event = Event(
            id=verdict.get("threat_id", str(uuid.uuid4())),
            timestamp=datetime.utcnow(),
            src_ip=src_ip,
            dst_ip=dst_ip,
            port=port,
            protocol=protocol,
            attack_type=attack_type,
            confidence=confidence,
            severity=severity,
            agent="sentinel",
            reasoning=verdict.get("reasoning", ""),
            resolved=False,
        )
        db.add(event)
        db.commit()

        # Step 4: Generate rule
        rule = create_rule(
            db=db,
            event_id=event.id,
            action=action,
            src_ip=src_ip,
            port=port,
            protocol=protocol,
            attack_type=attack_type,
        )

        self.log("response_generated", {
            "action": action,
            "trust_score": trust_score,
            "rule_id": rule["id"],
        })

        return {
            "action": action,
            "rule_generated": rule,
            "trust_score_after": trust_score,
            "severity": severity,
            "justification": f"{attack_type} detected from {src_ip} with {confidence:.0%} confidence. "
                             f"Trust score dropped to {trust_score:.0f}. Action: {action}.",
        }


# Singleton instance
tactician = TacticianAgent()
