"""
OS firewall rule executor.
Supports auto-applying generated rules on Windows and Linux.
"""
import platform
import subprocess
import threading
from datetime import datetime


def _run_command(command: list[str]) -> tuple[bool, str]:
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=12)
        if proc.returncode == 0:
            return True, (proc.stdout or "ok").strip()
        return False, (proc.stderr or proc.stdout or "command failed").strip()
    except Exception as exc:
        return False, str(exc)


def _windows_add_rule(rule_name: str, src_ip: str, port: int, protocol: str, action: str) -> tuple[bool, str]:
    if action not in ("block_temp", "block_perm"):
        return True, "no_os_rule_needed"

    protocol = (protocol or "TCP").upper()
    if protocol not in ("TCP", "UDP", "ICMPV4", "ICMPV6"):
        protocol = "TCP"

    if action == "block_perm":
        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                f"New-NetFirewallRule -DisplayName '{rule_name}' -Direction Inbound "
                f"-Action Block -RemoteAddress '{src_ip}' -Protocol Any"
            ),
        ]
    else:
        # Temporary block with port scope where available.
        if protocol in ("TCP", "UDP") and port > 0:
            ps = (
                f"New-NetFirewallRule -DisplayName '{rule_name}' -Direction Inbound "
                f"-Action Block -RemoteAddress '{src_ip}' -Protocol {protocol} -LocalPort {port}"
            )
        else:
            ps = (
                f"New-NetFirewallRule -DisplayName '{rule_name}' -Direction Inbound "
                f"-Action Block -RemoteAddress '{src_ip}' -Protocol Any"
            )
        command = ["powershell", "-NoProfile", "-Command", ps]

    return _run_command(command)


def _windows_remove_rule(rule_name: str) -> tuple[bool, str]:
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        f"Get-NetFirewallRule -DisplayName '{rule_name}' | Remove-NetFirewallRule",
    ]
    return _run_command(command)


def _linux_add_rule(src_ip: str, port: int, protocol: str, action: str) -> tuple[bool, str]:
    if action == "block_perm":
        cmd = ["iptables", "-A", "INPUT", "-s", src_ip, "-j", "DROP"]
    elif action == "block_temp":
        proto = (protocol or "tcp").lower()
        if proto in ("tcp", "udp") and port > 0:
            cmd = ["iptables", "-A", "INPUT", "-s", src_ip, "-p", proto, "--dport", str(port), "-j", "DROP"]
        else:
            cmd = ["iptables", "-A", "INPUT", "-s", src_ip, "-j", "DROP"]
    else:
        return True, "no_os_rule_needed"
    return _run_command(cmd)


def _linux_remove_rule(src_ip: str, port: int, protocol: str, action: str) -> tuple[bool, str]:
    if action == "block_perm":
        cmd = ["iptables", "-D", "INPUT", "-s", src_ip, "-j", "DROP"]
    elif action == "block_temp":
        proto = (protocol or "tcp").lower()
        if proto in ("tcp", "udp") and port > 0:
            cmd = ["iptables", "-D", "INPUT", "-s", src_ip, "-p", proto, "--dport", str(port), "-j", "DROP"]
        else:
            cmd = ["iptables", "-D", "INPUT", "-s", src_ip, "-j", "DROP"]
    else:
        return True, "no_os_rule_needed"
    return _run_command(cmd)


def apply_firewall_rule(rule_id: str, action: str, src_ip: str, port: int, protocol: str, expires_at=None) -> dict:
    """
    Apply OS firewall rule for generated policy action.
    Returns structured execution result.
    """
    os_name = platform.system().lower()
    rule_name = f"ZeroTrustAI-{rule_id}"
    applied_at = datetime.utcnow().isoformat()

    if os_name == "windows":
        ok, msg = _windows_add_rule(rule_name, src_ip, port, protocol, action)
        if ok and action == "block_temp" and expires_at:
            _schedule_windows_remove(rule_name, expires_at)
    elif os_name == "linux":
        ok, msg = _linux_add_rule(src_ip, port, protocol, action)
        if ok and action == "block_temp" and expires_at:
            _schedule_linux_remove(src_ip, port, protocol, action, expires_at)
    else:
        ok, msg = False, f"unsupported_os:{os_name}"

    return {
        "auto_applied": ok,
        "applied_at": applied_at if ok else None,
        "executor_os": os_name,
        "executor_message": msg,
    }


def remove_firewall_rule(rule_id: str, action: str, src_ip: str, port: int, protocol: str) -> dict:
    os_name = platform.system().lower()
    rule_name = f"ZeroTrustAI-{rule_id}"
    if os_name == "windows":
        ok, msg = _windows_remove_rule(rule_name)
    elif os_name == "linux":
        ok, msg = _linux_remove_rule(src_ip, port, protocol, action)
    else:
        ok, msg = False, f"unsupported_os:{os_name}"
    return {"removed": ok, "executor_os": os_name, "executor_message": msg}


def _schedule_windows_remove(rule_name: str, expires_at):
    delay = max(1, int((expires_at - datetime.utcnow()).total_seconds()))

    def _remove():
        _windows_remove_rule(rule_name)

    threading.Timer(delay, _remove).start()


def _schedule_linux_remove(src_ip: str, port: int, protocol: str, action: str, expires_at):
    delay = max(1, int((expires_at - datetime.utcnow()).total_seconds()))

    def _remove():
        _linux_remove_rule(src_ip, port, protocol, action)

    threading.Timer(delay, _remove).start()

