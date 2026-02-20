"""
ZeroTrust AI — Analyst Agent
Correlates events, maps to MITRE ATT&CK, predicts next-stage attacks.
"""
import uuid
import json
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent
from core.models import Event, Report
from utils.llm import call_llm


# MITRE ATT&CK pattern mappings
MITRE_PATTERNS = {
    "recon_to_exploit": {
        "sequence": ["port_scan", "exploit"],
        "techniques": ["T1046", "T1190"],
        "description": "Reconnaissance → Exploitation: Port scan followed by exploit attempt",
    },
    "bruteforce_to_lateral": {
        "sequence": ["brute_force"],
        "techniques": ["T1110", "T1021"],
        "description": "Brute Force → Lateral Movement: Credential attack then internal spread",
    },
    "c2_communication": {
        "sequence": ["c2_beacon"],
        "techniques": ["T1059"],
        "description": "Command and Control: Periodic beaconing communication",
    },
    "ddos_escalation": {
        "sequence": ["ddos"],
        "techniques": ["T1498"],
        "description": "DDoS Escalation: Volumetric attack pattern",
    },
    "insider_threat": {
        "sequence": ["normal"],
        "techniques": ["T1078"],
        "description": "Insider Threat: Anomalous internal device behavior",
    },
}


class AnalystAgent(BaseAgent):
    """Correlates patterns across events and predicts attack chains."""

    def __init__(self):
        super().__init__("analyst")

    def _correlate_events(self, events: list) -> list:
        """Find correlations between events."""
        correlations = []

        # Group by source IP
        by_source = {}
        for e in events:
            src = e.src_ip
            if src not in by_source:
                by_source[src] = []
            by_source[src].append(e)

        # Find multi-stage attacks from same source
        for src_ip, src_events in by_source.items():
            if len(src_events) >= 2:
                attack_types = [e.attack_type for e in src_events]
                correlations.append({
                    "source_ip": src_ip,
                    "event_count": len(src_events),
                    "attack_types": list(set(attack_types)),
                    "pattern": "multi_stage" if len(set(attack_types)) > 1 else "repeated",
                })

        # Group by target (destination)
        by_target = {}
        for e in events:
            dst = e.dst_ip
            if dst not in by_target:
                by_target[dst] = []
            by_target[dst].append(e)

        for dst_ip, dst_events in by_target.items():
            if len(dst_events) >= 3:
                sources = list(set(e.src_ip for e in dst_events))
                if len(sources) >= 2:
                    correlations.append({
                        "target_ip": dst_ip,
                        "source_count": len(sources),
                        "sources": sources[:5],
                        "pattern": "coordinated_attack",
                    })

        return correlations

    def _map_to_mitre(self, events: list) -> list:
        """Map event patterns to MITRE ATT&CK techniques."""
        attack_types_seen = set(e.attack_type for e in events if e.attack_type != "normal")
        mapped = []

        for pattern_name, pattern in MITRE_PATTERNS.items():
            for seq_type in pattern["sequence"]:
                if seq_type in attack_types_seen:
                    mapped.append({
                        "pattern": pattern_name,
                        "techniques": pattern["techniques"],
                        "description": pattern["description"],
                        "matched_on": seq_type,
                    })
                    break

        return mapped

    def _predict_next_attack(self, correlations: list, mitre_mappings: list) -> str:
        """Predict the likely next-stage attack based on patterns."""
        if not correlations and not mitre_mappings:
            return "No significant patterns detected. System operating normally."

        predictions = []
        for mapping in mitre_mappings:
            if mapping["pattern"] == "recon_to_exploit":
                predictions.append("Exploitation attempt likely after reconnaissance phase")
            elif mapping["pattern"] == "bruteforce_to_lateral":
                predictions.append("Lateral movement expected after credential compromise")
            elif mapping["pattern"] == "c2_communication":
                predictions.append("Data exfiltration or further payload delivery expected")
            elif mapping["pattern"] == "ddos_escalation":
                predictions.append("Escalation to service disruption expected")

        for corr in correlations:
            if corr.get("pattern") == "coordinated_attack":
                predictions.append(f"Coordinated attack on {corr.get('target_ip')} from {corr.get('source_count')} sources")

        return "; ".join(predictions) if predictions else "Monitor for additional indicators."

    async def process(self, data: dict = None, db=None) -> dict:
        """
        Analyze recent events and generate intelligence report.
        Runs on-demand or periodically.
        """
        if db is None:
            return {"error": "No database session"}

        self.log("starting_analysis")

        # Get events from last 60 minutes
        time_window = datetime.utcnow() - timedelta(minutes=60)
        events = (
            db.query(Event)
            .filter(Event.timestamp >= time_window)
            .order_by(Event.timestamp.desc())
            .limit(100)
            .all()
        )

        if not events:
            return {
                "summary": "No events in the last 60 minutes.",
                "correlations": [],
                "mitre_mappings": [],
                "predicted_next": "System quiet — no threats detected.",
                "event_count": 0,
            }

        # Correlate events
        correlations = self._correlate_events(events)
        mitre_mappings = self._map_to_mitre(events)
        prediction = self._predict_next_attack(correlations, mitre_mappings)

        # Build summary
        attack_counts = {}
        for e in events:
            if e.attack_type != "normal":
                attack_counts[e.attack_type] = attack_counts.get(e.attack_type, 0) + 1

        summary = (
            f"Analyzed {len(events)} events in 60-minute window. "
            f"Threats: {sum(attack_counts.values())} ({', '.join(f'{k}: {v}' for k, v in attack_counts.items())}). "
            f"Correlations found: {len(correlations)}. MITRE patterns matched: {len(mitre_mappings)}."
        )

        # Optional: call LLM for deeper analysis
        llm_insight = await call_llm(
            f"Summarize this threat intelligence:\n{summary}\n\nCorrelations: {json.dumps(correlations)}\nMITRE: {json.dumps(mitre_mappings)}",
            attack_type=list(attack_counts.keys())[0] if attack_counts else "normal",
            prompt_type="summarize",
        )

        # Persist report
        report = Report(
            id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            time_window="60 minutes",
            summary=summary,
            correlations=json.dumps(correlations),
            predicted_next=prediction,
        )
        db.add(report)
        db.commit()

        result = {
            "report_id": report.id,
            "summary": summary,
            "correlations": correlations,
            "mitre_mappings": mitre_mappings,
            "predicted_next": prediction,
            "event_count": len(events),
            "llm_insight": llm_insight,
        }

        self.log("analysis_complete", {"event_count": len(events), "correlations": len(correlations)})
        return result


# Singleton
analyst = AnalystAgent()
