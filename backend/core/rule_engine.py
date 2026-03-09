"""
ZeroTrust AI — Rule Engine
Generates safe firewall rules: intent → iptables command with validation.
"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from core.models import Rule
from core.firewall_executor import apply_firewall_rule, remove_firewall_rule
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import PROTECTED_IPS, AUTO_APPLY_RULES, RULE_COOLDOWN_SECONDS, MAX_ACTIVE_RULES


# Action → TTL (Time to live for the rule)
ACTION_TTL = {
    "monitor": None,  # No rule needed
    "rate_limit": timedelta(minutes=30),
    "block_temp": timedelta(minutes=5),
    "block_perm": None,  # Permanent
}


def _extract_rule_params(iptables_cmd: str) -> tuple[str, int, str]:
    """Parse src_ip/port/protocol from stored iptables command (best-effort)."""
    src_ip = ""
    port = 0
    protocol = "tcp"
    if not iptables_cmd:
        return src_ip, port, protocol
    parts = iptables_cmd.split()
    for i, token in enumerate(parts):
        if token == "-s" and i + 1 < len(parts):
            src_ip = parts[i + 1]
        elif token == "--dport" and i + 1 < len(parts):
            try:
                port = int(parts[i + 1])
            except ValueError:
                port = 0
        elif token == "-p" and i + 1 < len(parts):
            protocol = parts[i + 1]
    return src_ip, port, protocol


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


def _find_recent_duplicate_rule(db: Session, src_ip: str, action: str):
    """Return a recent active rule for same source and action, if present."""
    if RULE_COOLDOWN_SECONDS <= 0:
        return None
    threshold = datetime.utcnow() - timedelta(seconds=RULE_COOLDOWN_SECONDS)
    return (
        db.query(Rule)
        .filter(Rule.active == True)
        .filter(Rule.action == action)
        .filter(Rule.created_at >= threshold)
        .filter(Rule.iptables_cmd.like(f"%-s {src_ip} %"))
        .order_by(Rule.created_at.desc())
        .first()
    )


def _threshold_reached(db: Session) -> bool:
    if MAX_ACTIVE_RULES <= 0:
        return False
    active_count = db.query(Rule).filter(Rule.active == True).count()
    return active_count >= MAX_ACTIVE_RULES


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

    if _threshold_reached(db):
        declined = Rule(
            id=str(uuid.uuid4()),
            event_id=event_id,
            action=action,
            rule_text=f"[AUTO-DECLINED: threshold] {rule_text}",
            iptables_cmd=iptables_cmd,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            active=False,
            human_approved=False,
        )
        db.add(declined)
        db.commit()
        db.refresh(declined)
        return {
            "id": declined.id,
            "action": action,
            "rule_text": declined.rule_text,
            "iptables_cmd": iptables_cmd,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "active": False,
            "human_approved": False,
            "execution": {
                "auto_applied": False,
                "applied_at": None,
                "executor_os": None,
                "executor_message": f"auto_declined_threshold_reached:{MAX_ACTIVE_RULES}",
            },
        }

    duplicate = _find_recent_duplicate_rule(db, src_ip, action)
    if duplicate:
        return {
            "id": duplicate.id,
            "action": duplicate.action,
            "rule_text": duplicate.rule_text,
            "iptables_cmd": duplicate.iptables_cmd,
            "expires_at": duplicate.expires_at.isoformat() if duplicate.expires_at else None,
            "active": duplicate.active,
            "human_approved": duplicate.human_approved,
            "execution": {
                "auto_applied": False,
                "applied_at": None,
                "executor_os": None,
                "executor_message": "duplicate_rule_reused",
            },
        }

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

    execution = {
        "auto_applied": False,
        "applied_at": None,
        "executor_os": None,
        "executor_message": "auto_apply_disabled",
    }
    if AUTO_APPLY_RULES and action in ("block_temp", "block_perm"):
        execution = apply_firewall_rule(
            rule_id=rule.id,
            action=action,
            src_ip=src_ip,
            port=port,
            protocol=protocol,
            expires_at=expires_at,
        )
        if execution.get("auto_applied"):
            rule.human_approved = True
        else:
            # Fail-safe: disable rule if OS-level enforcement fails.
            rule.active = False
            rule.human_approved = False
        db.commit()
        db.refresh(rule)

    return {
        "id": rule.id,
        "action": action,
        "rule_text": rule_text,
        "iptables_cmd": iptables_cmd,
        "expires_at": expires_at.isoformat() if expires_at else None,
        "active": rule.active,
        "human_approved": rule.human_approved,
        "execution": execution,
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
    if approved and _threshold_reached(db):
        rule.human_approved = False
        rule.active = False
        db.commit()
        db.refresh(rule)
        return {
            "id": rule.id,
            "human_approved": rule.human_approved,
            "active": rule.active,
            "execution": {
                "executor_message": f"manual_approve_denied_threshold_reached:{MAX_ACTIVE_RULES}"
            },
        }

    src_ip, port, protocol = _extract_rule_params(rule.iptables_cmd or "")
    execution = {"executor_message": "manual_override_only"}
    if approved and not AUTO_APPLY_RULES and rule.action in ("block_temp", "block_perm"):
        execution = apply_firewall_rule(
            rule_id=rule.id,
            action=rule.action,
            src_ip=src_ip,
            port=port,
            protocol=protocol,
            expires_at=rule.expires_at,
        )
        if not execution.get("auto_applied"):
            rule.active = False
    if not approved:
        if rule.action in ("block_temp", "block_perm"):
            # Best-effort rollback from host firewall.
            execution = remove_firewall_rule(
                rule_id=rule.id,
                action=rule.action,
                src_ip=src_ip,
                port=port,
                protocol=protocol,
            )
        rule.active = False
    db.commit()
    db.refresh(rule)

    return {
        "id": rule.id,
        "human_approved": rule.human_approved,
        "active": rule.active,
        "execution": execution,
    }
