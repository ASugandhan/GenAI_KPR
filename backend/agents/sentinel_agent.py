"""
ZeroTrust AI — Sentinel Agent
Detection + Classification: ML model → LLM reasoning → verdict.
"""
import uuid
from datetime import datetime
from agents.base_agent import BaseAgent
from ml.predict import predict
from utils.llm import call_llm
from config import LLM_CONFIDENCE_MIN, LLM_CONFIDENCE_MAX


# Confidence → severity mapping
def _get_severity(attack_type: str, confidence: float) -> str:
    if attack_type == "normal":
        return "LOW"
    if confidence >= 0.85:
        return "CRITICAL"
    if confidence >= 0.65:
        return "HIGH"
    if confidence >= 0.45:
        return "MEDIUM"
    return "LOW"


class SentinelAgent(BaseAgent):
    """Detects and classifies threats using ML + LLM reasoning."""

    def __init__(self):
        super().__init__("sentinel")

    async def process(self, packet: dict, db=None) -> dict:
        """
        Process a network packet through the detection pipeline.
        1. ML prediction
        2. LLM reasoning (if confidence 0.4–0.8)
        3. Return verdict
        """
        self.log("processing_packet", {"src_ip": packet.get("src_ip"), "dst_ip": packet.get("dst_ip")})

        # Step 1: ML prediction
        ml_result = predict(packet)
        attack_type = ml_result["attack_type"]
        confidence = ml_result["confidence"]
        reasoning = ""

        # Step 2: LLM reasoning (for uncertain predictions)
        if LLM_CONFIDENCE_MIN <= confidence <= LLM_CONFIDENCE_MAX:
            self.log("calling_llm", {"reason": "uncertain_confidence", "confidence": confidence})
            prompt = (
                f"Analyze this network packet for threats:\n"
                f"Source IP: {packet.get('src_ip')}\n"
                f"Destination IP: {packet.get('dst_ip')}\n"
                f"Port: {packet.get('port')}\n"
                f"Protocol: {packet.get('protocol')}\n"
                f"Bytes: {packet.get('bytes')}\n"
                f"Duration: {packet.get('duration')}s\n"
                f"Packet Count: {packet.get('packet_count')}\n"
                f"ML Classification: {attack_type} (confidence: {confidence})\n\n"
                f"Respond in JSON with: reasoning, severity (LOW/MEDIUM/HIGH/CRITICAL), mitre"
            )
            llm_result = await call_llm(prompt, attack_type=attack_type, prompt_type="analyze")
            reasoning = llm_result.get("reasoning", "")

            # LLM may override severity
            llm_severity = llm_result.get("severity")
            if llm_severity:
                severity = llm_severity
            else:
                severity = _get_severity(attack_type, confidence)
        elif confidence > LLM_CONFIDENCE_MAX:
            # High confidence — auto-classify without LLM
            severity = _get_severity(attack_type, confidence)
            reasoning = f"Auto-classified as {attack_type} with {confidence:.0%} confidence. No LLM needed."
        else:
            severity = "LOW"
            reasoning = "Low confidence detection — monitoring only."

        is_threat = attack_type != "normal"

        verdict = {
            "threat_id": str(uuid.uuid4()),
            "is_threat": is_threat,
            "attack_type": attack_type,
            "confidence": confidence,
            "severity": severity,
            "reasoning": reasoning,
            "agent": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "ml_details": ml_result,
        }

        if is_threat:
            self.logger.log_threat(packet, verdict)
        self.log("verdict_issued", {"attack_type": attack_type, "severity": severity})

        return verdict


# Singleton instance
sentinel = SentinelAgent()
