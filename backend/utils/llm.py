"""
ZeroTrust AI — LLM Wrapper
Gemini API calls with timeout + mock fallback for offline mode.
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import GEMINI_API_KEY, GEMINI_MODEL, OFFLINE_MODE, MOCK_LLM, LLM_TIMEOUT_SECONDS

# Mock responses for offline mode
MOCK_RESPONSES = {
    "brute_force": {
        "reasoning": "High packet count (847) in short duration (0.3s) targeting SSH port 22 indicates brute force credential attack. The packet frequency exceeds normal authentication patterns by 100x. Recommend immediate rate limiting and credential rotation.",
        "severity": "HIGH",
        "mitre": "T1110 — Brute Force",
    },
    "port_scan": {
        "reasoning": "Sequential probing across multiple ports with minimal payload (40-200 bytes) indicates reconnaissance scanning. This is a precursor to exploitation. Source IP should be flagged for monitoring.",
        "severity": "MEDIUM",
        "mitre": "T1046 — Network Service Discovery",
    },
    "ddos": {
        "reasoning": "Massive volume of traffic (50K+ packets, 100KB+) targeting web ports suggests volumetric DDoS attack. Traffic pattern shows UDP amplification characteristics. Immediate upstream filtering recommended.",
        "severity": "CRITICAL",
        "mitre": "T1498 — Network Denial of Service",
    },
    "exploit": {
        "reasoning": "Large payload (30KB) with structured content targeting web application port suggests exploitation attempt. Payload contains patterns consistent with SQL injection or remote code execution.",
        "severity": "CRITICAL",
        "mitre": "T1190 — Exploit Public-Facing Application",
    },
    "c2_beacon": {
        "reasoning": "Periodic small-payload HTTPS/DNS traffic at regular intervals indicates command and control beaconing. The timing pattern and payload size are consistent with known C2 frameworks.",
        "severity": "HIGH",
        "mitre": "T1059 — Command and Scripting Interpreter",
    },
    "normal": {
        "reasoning": "Traffic pattern is within expected parameters for normal network communication. No indicators of malicious activity detected.",
        "severity": "LOW",
        "mitre": "N/A",
    },
}


def _get_mock_response(attack_type: str, prompt_type: str = "analyze") -> str:
    """Return a pre-cached mock response."""
    mock = MOCK_RESPONSES.get(attack_type, MOCK_RESPONSES["normal"])
    if prompt_type == "analyze":
        return json.dumps(mock)
    elif prompt_type == "selfheal":
        return json.dumps({
            "permanent_rules": [f"Block repeat offenders targeting {attack_type} patterns"],
            "hardening_recommendations": [
                "Update IDS signatures",
                "Enable rate limiting on edge firewall",
                "Rotate exposed credentials",
            ],
            "health_score_delta": 5.0,
            "lessons_learned": f"Incident revealed {attack_type} vulnerability. Automated response was effective.",
        })
    elif prompt_type == "summarize":
        return json.dumps({
            "summary": f"Analysis of recent events shows {attack_type} activity patterns.",
            "correlations": ["Multiple sources targeting same destination subnet"],
            "predicted_next": "Lateral movement attempt likely within 15 minutes",
            "recommended_actions": ["Increase monitoring", "Isolate affected segments"],
        })
    return json.dumps(mock)


async def call_llm(prompt: str, attack_type: str = "normal", prompt_type: str = "analyze") -> dict:
    """
    Call Gemini LLM or return mock response.
    Returns parsed JSON response.
    """
    if OFFLINE_MODE or MOCK_LLM or not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_key_here":
        return json.loads(_get_mock_response(attack_type, prompt_type))

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=500,
            ),
        )
        text = response.text.strip()

        # Try to parse as JSON
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)

    except Exception as e:
        # Fallback to mock on any error
        print(f"⚠️ LLM call failed ({e}), using mock response")
        return json.loads(_get_mock_response(attack_type, prompt_type))
