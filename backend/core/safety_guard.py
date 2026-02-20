"""
ZeroTrust AI — Safety Guard
LLM output validation — sanitizes and validates AI-generated content.
"""
import re
import json


DANGEROUS_PATTERNS = [
    r"rm\s+-rf",
    r"format\s+[a-z]:",
    r"del\s+/[fqs]",
    r"shutdown",
    r"reboot",
    r"DROP\s+DATABASE",
    r"DROP\s+TABLE",
    r";\s*--",
    r"eval\s*\(",
    r"exec\s*\(",
    r"__import__",
    r"subprocess",
    r"os\.system",
]

ALLOWED_IPTABLES_ACTIONS = ["INPUT", "OUTPUT", "FORWARD", "DROP", "ACCEPT", "REJECT", "LOG"]


def validate_llm_output(text: str) -> dict:
    """Validate LLM-generated text for dangerous content."""
    issues = []

    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            issues.append(f"Dangerous pattern detected: {pattern}")

    return {
        "is_safe": len(issues) == 0,
        "issues": issues,
        "sanitized": text if len(issues) == 0 else "[BLOCKED — unsafe content detected]",
    }


def validate_iptables_cmd(cmd: str) -> dict:
    """Validate an iptables command for safety."""
    issues = []

    if not cmd.startswith("iptables"):
        issues.append("Command must start with 'iptables'")

    # Check for dangerous chaining
    if ";" in cmd or "&&" in cmd or "|" in cmd:
        issues.append("No command chaining allowed")

    # Validate action
    parts = cmd.split()
    has_valid_action = any(a in parts for a in ALLOWED_IPTABLES_ACTIONS)
    if not has_valid_action:
        issues.append("No valid iptables action found")

    return {
        "is_safe": len(issues) == 0,
        "issues": issues,
        "command": cmd if len(issues) == 0 else "",
    }


def sanitize_json_response(text: str) -> dict:
    """Try to parse and sanitize a JSON response from LLM."""
    try:
        # Strip markdown code blocks
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        data = json.loads(text)

        # Validate any iptables commands in the response
        if "iptables_cmd" in data:
            validation = validate_iptables_cmd(data["iptables_cmd"])
            if not validation["is_safe"]:
                data["iptables_cmd"] = ""
                data["safety_warning"] = validation["issues"]

        return {"success": True, "data": data}

    except json.JSONDecodeError:
        return {"success": False, "data": {"raw_text": text}, "error": "Invalid JSON from LLM"}
