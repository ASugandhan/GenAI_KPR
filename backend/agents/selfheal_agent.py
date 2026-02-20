"""
ZeroTrust AI — Self-Healing Agent
Post-incident hardening: analyzes response, writes permanent rules, updates health score.
"""
import uuid
import json
from datetime import datetime
from agents.base_agent import BaseAgent
from core.models import Event, SelfHealLog, SystemHealth
from utils.llm import call_llm


class SelfHealAgent(BaseAgent):
    """Post-incident hardening agent powered by Gemini LLM."""

    def __init__(self):
        super().__init__("selfheal")

    def _get_or_init_health(self, db) -> SystemHealth:
        """Get or initialize the system health record."""
        health = db.query(SystemHealth).filter(SystemHealth.id == 1).first()
        if not health:
            health = SystemHealth(id=1, health_score=100.0, total_healed=0, last_updated=datetime.utcnow())
            db.add(health)
            db.commit()
            db.refresh(health)
        return health

    async def process(self, data: dict = None, db=None) -> dict:
        """
        Analyze a resolved incident and recommend hardening.
        1. Get incident details
        2. Call LLM for hardening analysis
        3. Write permanent rules + update health score
        """
        if db is None:
            return {"error": "No database session"}

        self.log("starting_selfheal")

        # Get recent critical/high events
        recent_events = (
            db.query(Event)
            .filter(Event.severity.in_(["CRITICAL", "HIGH"]))
            .order_by(Event.timestamp.desc())
            .limit(10)
            .all()
        )

        if not recent_events:
            health = self._get_or_init_health(db)
            return {
                "message": "No critical/high incidents to heal.",
                "heal_id": "none",
                "incidents_healed": 0,
                "health_score_before": health.health_score,
                "health_score_after": health.health_score,
                "health_score_delta": 0.0,
                "permanent_rules": [],
                "hardening_recommendations": [],
                "lessons_learned": "No recent critical incidents detected.",
            }

        # Build incident summary for LLM
        incidents_summary = []
        for e in recent_events:
            incidents_summary.append({
                "attack_type": e.attack_type,
                "severity": e.severity,
                "src_ip": e.src_ip,
                "dst_ip": e.dst_ip,
                "port": e.port,
                "reasoning": e.reasoning,
                "resolved": e.resolved,
            })

        # Call LLM for hardening recommendations
        prompt = (
            f"You are a cybersecurity hardening advisor. Analyze these recent incidents:\n"
            f"{json.dumps(incidents_summary, indent=2)}\n\n"
            f"Respond in JSON with:\n"
            f"- permanent_rules: list of rules that should be made permanent\n"
            f"- hardening_recommendations: list of security improvements\n"
            f"- health_score_delta: positive number (how much system health improved)\n"
            f"- lessons_learned: what we learned from these incidents"
        )

        llm_result = await call_llm(
            prompt,
            attack_type=recent_events[0].attack_type if recent_events else "normal",
            prompt_type="selfheal",
        )

        # Update system health
        health = self._get_or_init_health(db)
        health_before = health.health_score
        delta = float(llm_result.get("health_score_delta", 5.0))
        health.health_score = min(100.0, health.health_score + delta)
        health.total_healed += 1
        health.last_updated = datetime.utcnow()

        # Mark events as resolved
        for e in recent_events:
            e.resolved = True

        # Log self-heal action
        heal_log = SelfHealLog(
            id=str(uuid.uuid4()),
            incident_id=recent_events[0].id if recent_events else "",
            triggered_at=datetime.utcnow(),
            health_score_before=health_before,
            health_score_after=health.health_score,
            permanent_rules=json.dumps(llm_result.get("permanent_rules", [])),
            lessons_learned=json.dumps(llm_result.get("lessons_learned", "")),
            hardening_recommendations=json.dumps(llm_result.get("hardening_recommendations", [])),
        )
        db.add(heal_log)
        db.commit()

        result = {
            "heal_id": heal_log.id,
            "incidents_healed": len(recent_events),
            "health_score_before": health_before,
            "health_score_after": health.health_score,
            "health_score_delta": delta,
            "permanent_rules": llm_result.get("permanent_rules", []),
            "hardening_recommendations": llm_result.get("hardening_recommendations", []),
            "lessons_learned": llm_result.get("lessons_learned", ""),
        }

        self.log("selfheal_complete", {
            "healed": len(recent_events),
            "health_delta": delta,
        })

        return result


# Singleton
selfheal = SelfHealAgent()
