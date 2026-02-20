"""
ZeroTrust AI — Rule Engine
Generates safe firewall rules: intent → iptables command with validation.
"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from core.models import Rule
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import PROTECTED_IPS


# Action → TTL (Time to live for the rule)
ACTION_TTL = {
    "monitor": None,  # No rule needed
    "rate_limit": timedelta(minutes=30),
    "block_temp": timedelta(minutes=5),
    "block_perm": None,  # Permanent
}


def generate_iptables_cmd(action: str, src_ip: str, port: int, protocol: str = "tcp") -> str:
    """Generate a safe iptables command from action intent."""
    protocol = protocol.lower()
    if protocol not in ("tcp", "udp", "icmp"):
        protocol = "tcp"

    if action == "rate_limit":
        return f"iptables -A INPUT -s {src_ip} -p {protocol} --dport {port} -m limit --limit 10/s -j ACCEPT"
    elif action == "block_temp":
        return f"iptables -A INPUT -s {src_ip} -p {protocol} --dport {port} -j DROP"
    elif action == "block_perm":
        return f"iptables -A INPUT -s {src_ip} -j DROP"
    else:
        return ""


def generate_rule_text(action: str, src_ip: str, port: int, attack_type: str) -> str:
    """Generate human-readable rule description."""
    texts = {
        "monitor": f"Monitor traffic from {src_ip} on port {port} ({attack_type})",
        "rate_limit": f"Rate limit {src_ip} to 10 req/s on port {port} ({attack_type})",
        "block_temp": f"Temporarily block {src_ip} on port {port} for 5 minutes ({attack_type})",
        "block_perm": f"Permanently block {src_ip} — repeated {attack_type} violations",
    }
    return texts.get(action, f"Unknown action for {src_ip}")


def create_rule(
    db: Session,
    event_id: str,
    action: str,
    src_ip: str,
    port: int,
    protocol: str,
    attack_type: str,
) -> dict:
    """Create and persist a firewall rule."""
    # Safety check — never block protected IPs
    if src_ip in PROTECTED_IPS and action in ("block_temp", "block_perm"):
        action = "rate_limit"  # Downgrade to rate limit

    iptables_cmd = generate_iptables_cmd(action, src_ip, port, protocol)
    rule_text = generate_rule_text(action, src_ip, port, attack_type)

    ttl = ACTION_TTL.get(action)
    expires_at = (datetime.utcnow() + ttl) if ttl else None

    rule = Rule(
        id=str(uuid.uuid4()),
        event_id=event_id,
        action=action,
        rule_text=rule_text,
        iptables_cmd=iptables_cmd,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
        active=True,
        human_approved=None,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)

    return {
        "id": rule.id,
        "action": action,
        "rule_text": rule_text,
        "iptables_cmd": iptables_cmd,
        "expires_at": expires_at.isoformat() if expires_at else None,
        "active": True,
    }


def get_active_rules(db: Session) -> list:
    """Get all active firewall rules."""
    rules = db.query(Rule).filter(Rule.active == True).all()
    return [
        {
            "id": r.id,
            "event_id": r.event_id,
            "action": r.action,
            "rule_text": r.rule_text,
            "iptables_cmd": r.iptables_cmd,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "expires_at": r.expires_at.isoformat() if r.expires_at else None,
            "active": r.active,
            "human_approved": r.human_approved,
        }
        for r in rules
    ]


def override_rule(db: Session, rule_id: str, approved: bool) -> dict:
    """Human override — approve or reject a rule."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        return {"error": "Rule not found"}

    rule.human_approved = approved
    if not approved:
        rule.active = False
    db.commit()
    db.refresh(rule)

    return {
        "id": rule.id,
        "human_approved": rule.human_approved,
        "active": rule.active,
    }
