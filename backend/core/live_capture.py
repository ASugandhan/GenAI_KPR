"""
Live packet capture service.
Uses scapy AsyncSniffer and forwards captured packets into the autonomous runtime.
"""
import asyncio
from datetime import datetime
from typing import Callable, Awaitable, Optional

from config import CAPTURE_BPF_FILTER, CAPTURE_INTERFACE, EXCLUDE_SELF_TRAFFIC, SELF_TRAFFIC_PORTS

try:
    from scapy.all import AsyncSniffer, IP, TCP, UDP, ICMP, get_if_list  # type: ignore
    SCAPY_AVAILABLE = True
except Exception:
    AsyncSniffer = None
    IP = TCP = UDP = ICMP = None
    get_if_list = None
    SCAPY_AVAILABLE = False


class LiveCaptureService:
    """Captures live packets and broadcasts them to subscribers."""

    def __init__(self):
        self._sniffer = None
        self._running = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._submit_coro: Optional[Callable[[dict], Awaitable[dict]]] = None
        self._subscribers: set[asyncio.Queue] = set()

        self.packets_captured = 0
        self.packets_dropped = 0
        self.last_packet_at = None
        self.last_error = None

    @property
    def available(self) -> bool:
        return SCAPY_AVAILABLE

    @property
    def running(self) -> bool:
        return self._running

    async def start(self, submit_coro: Callable[[dict], Awaitable[dict]]):
        if self._running:
            return
        if not SCAPY_AVAILABLE:
            self.last_error = "scapy_not_installed"
            return

        self._loop = asyncio.get_running_loop()
        self._submit_coro = submit_coro
        resolved_iface = self._normalize_interface(CAPTURE_INTERFACE)
        self._sniffer = AsyncSniffer(
            iface=resolved_iface or None,
            filter=CAPTURE_BPF_FILTER if CAPTURE_BPF_FILTER else None,
            store=False,
            prn=self._on_packet,
        )
        self._sniffer.start()
        self._running = True

    async def stop(self):
        if not self._running:
            return
        try:
            if self._sniffer:
                self._sniffer.stop()
        except Exception as exc:
            self.last_error = str(exc)
        finally:
            self._running = False
            self._sniffer = None

    def _on_packet(self, pkt):
        if not self._loop:
            return
        try:
            parsed = self._parse_packet(pkt)
            if not parsed:
                return
            if self._is_self_traffic(parsed):
                self.packets_dropped += 1
                return
            self._loop.call_soon_threadsafe(self._broadcast, parsed)
            if self._submit_coro:
                asyncio.run_coroutine_threadsafe(self._submit_coro(parsed), self._loop)
        except Exception as exc:
            self.last_error = str(exc)
            self.packets_dropped += 1

    def _parse_packet(self, pkt):
        if not IP or not pkt.haslayer(IP):
            return None

        protocol = "OTHER"
        dst_port = 0
        if TCP and pkt.haslayer(TCP):
            protocol = "TCP"
            dst_port = int(pkt[TCP].dport)
        elif UDP and pkt.haslayer(UDP):
            protocol = "UDP"
            dst_port = int(pkt[UDP].dport)
        elif ICMP and pkt.haslayer(ICMP):
            protocol = "ICMP"

        packet = {
            "src_ip": str(pkt[IP].src),
            "dst_ip": str(pkt[IP].dst),
            "port": dst_port,
            "protocol": protocol,
            "bytes": int(len(pkt)),
            "duration": 0.01,
            "packet_count": 1,
            "timestamp": datetime.utcnow().isoformat(),
        }
        return packet

    def _is_self_traffic(self, packet: dict) -> bool:
        """Ignore local dashboard/api traffic to prevent self-feedback loops."""
        if not EXCLUDE_SELF_TRAFFIC:
            return False

        src_ip = str(packet.get("src_ip", ""))
        dst_ip = str(packet.get("dst_ip", ""))
        port = int(packet.get("port", 0) or 0)

        localhost_ips = {"127.0.0.1", "::1"}
        if src_ip in localhost_ips or dst_ip in localhost_ips:
            return True
        if port in set(SELF_TRAFFIC_PORTS):
            return True
        return False

    def _broadcast(self, packet: dict):
        self.packets_captured += 1
        self.last_packet_at = packet["timestamp"]
        for q in list(self._subscribers):
            try:
                q.put_nowait(packet)
            except asyncio.QueueFull:
                self.packets_dropped += 1
            except Exception:
                self._subscribers.discard(q)

    async def packet_stream(self):
        q = asyncio.Queue(maxsize=200)
        self._subscribers.add(q)
        try:
            while True:
                packet = await q.get()
                yield packet
        finally:
            self._subscribers.discard(q)

    def status(self) -> dict:
        return {
            "mode": "live",
            "available": self.available,
            "running": self.running,
            "interface": CAPTURE_INTERFACE,
            "resolved_interface": self._normalize_interface(CAPTURE_INTERFACE),
            "bpf_filter": CAPTURE_BPF_FILTER,
            "packets_captured": self.packets_captured,
            "packets_dropped": self.packets_dropped,
            "last_packet_at": self.last_packet_at,
            "last_error": self.last_error,
        }

    def list_interfaces(self) -> list:
        """Return interface names recognized by scapy on this host."""
        if not SCAPY_AVAILABLE or not get_if_list:
            return []
        try:
            return list(get_if_list())
        except Exception:
            return []

    def _normalize_interface(self, iface: str) -> str:
        """Normalize Windows GUID interfaces to Npcap format."""
        if not iface:
            return ""
        iface = iface.strip()
        if iface.startswith("{") and iface.endswith("}"):
            return f"\\Device\\NPF_{iface}"
        return iface


live_capture = LiveCaptureService()
