"""
Autonomous multi-agent runtime for ZeroTrust AI.
Pipeline:
  packet -> detector -> judge -> defender -> healer
"""
import asyncio
from datetime import datetime, timedelta

from agents.analyst_agent import analyst
from agents.judge_agent import judge
from agents.selfheal_agent import selfheal
from agents.sentinel_agent import sentinel
from agents.tactician_agent import tactician
from config import ANALYST_COOLDOWN_SECONDS, SELFHEAL_COOLDOWN_SECONDS
from core.database import SessionLocal


class AutonomousRuntime:
    """In-process event-driven orchestrator for the 4-agent pipeline."""

    def __init__(self):
        self.packet_queue = asyncio.Queue(maxsize=5000)
        self.judge_queue = asyncio.Queue(maxsize=5000)
        self.defend_queue = asyncio.Queue(maxsize=5000)
        self.heal_queue = asyncio.Queue(maxsize=5000)

        self._tasks = []
        self._running = False
        self._incident_seq = 0
        self._incident_lock = asyncio.Lock()
        self._incidents = {}
        self._pending_results = {}
        self._last_analyst_at = None
        self._last_selfheal_at = None

    async def start(self):
        if self._running:
            return
        self._running = True
        self._tasks = [
            asyncio.create_task(self._detector_loop(), name="detector_loop"),
            asyncio.create_task(self._judge_loop(), name="judge_loop"),
            asyncio.create_task(self._defender_loop(), name="defender_loop"),
            asyncio.create_task(self._healer_loop(), name="healer_loop"),
        ]

    async def stop(self):
        self._running = False
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks = []

    async def submit_packet(self, packet: dict, wait_for_result: bool = True, timeout_seconds: float = 5.0) -> dict:
        incident_id = await self._next_incident_id()
        now = datetime.utcnow().isoformat()
        self._incidents[incident_id] = {
            "incident_id": incident_id,
            "state": "INGESTED",
            "created_at": now,
            "updated_at": now,
            "packet": packet,
            "threat": None,
            "response": None,
            "analysis": None,
            "healed": False,
        }

        future = None
        if wait_for_result:
            future = asyncio.get_running_loop().create_future()
            self._pending_results[incident_id] = future

        await self.packet_queue.put({"incident_id": incident_id, "packet": packet})

        if not wait_for_result:
            return {"incident_id": incident_id, "accepted": True}

        try:
            result = await asyncio.wait_for(future, timeout=timeout_seconds)
            return result
        except asyncio.TimeoutError:
            return {
                "incident_id": incident_id,
                "status": "processing",
                "message": "Pipeline still processing. Query incident status later.",
            }
        finally:
            self._pending_results.pop(incident_id, None)

    def get_incident(self, incident_id: str):
        return self._incidents.get(incident_id)

    def list_recent_incidents(self, limit: int = 20):
        values = list(self._incidents.values())
        values.sort(key=lambda x: x["updated_at"], reverse=True)
        return values[:limit]

    async def _next_incident_id(self) -> str:
        async with self._incident_lock:
            self._incident_seq += 1
            return f"inc-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{self._incident_seq:06d}"

    def _set_state(self, incident_id: str, state: str, extra: dict = None):
        incident = self._incidents.get(incident_id)
        if not incident:
            return
        incident["state"] = state
        incident["updated_at"] = datetime.utcnow().isoformat()
        if extra:
            incident.update(extra)

    def _resolve_pending(self, incident_id: str, result: dict):
        future = self._pending_results.get(incident_id)
        if future and not future.done():
            future.set_result(result)

    async def _detector_loop(self):
        while self._running:
            payload = await self.packet_queue.get()
            incident_id = payload["incident_id"]
            packet = payload["packet"]
            try:
                verdict = await sentinel.process(packet)
                self._set_state(incident_id, "DETECTED", {"threat": verdict})
                await self.judge_queue.put(
                    {"incident_id": incident_id, "packet": packet, "verdict": verdict}
                )
            except Exception as exc:
                self._set_state(incident_id, "FAILED_DETECT", {"error": str(exc)})
                self._resolve_pending(
                    incident_id,
                    {"incident_id": incident_id, "status": "error", "stage": "detect", "error": str(exc)},
                )
            finally:
                self.packet_queue.task_done()

    async def _judge_loop(self):
        while self._running:
            payload = await self.judge_queue.get()
            incident_id = payload["incident_id"]
            packet = payload["packet"]
            verdict = payload["verdict"]
            try:
                judged = await judge.process(verdict)
                self._set_state(incident_id, "JUDGED", {"threat": judged})
                await self.defend_queue.put(
                    {"incident_id": incident_id, "packet": packet, "judged": judged}
                )
            except Exception as exc:
                self._set_state(incident_id, "FAILED_JUDGE", {"error": str(exc)})
                self._resolve_pending(
                    incident_id,
                    {"incident_id": incident_id, "status": "error", "stage": "judge", "error": str(exc)},
                )
            finally:
                self.judge_queue.task_done()

    async def _defender_loop(self):
        while self._running:
            payload = await self.defend_queue.get()
            incident_id = payload["incident_id"]
            packet = payload["packet"]
            judged = payload["judged"]
            db = SessionLocal()
            try:
                if judged.get("is_threat"):
                    response = await tactician.process(judged, db=db, packet=packet)
                    now = datetime.utcnow()
                    if (
                        self._last_analyst_at is None
                        or now - self._last_analyst_at >= timedelta(seconds=ANALYST_COOLDOWN_SECONDS)
                    ):
                        analysis = await analyst.process(db=db)
                        self._last_analyst_at = now
                    else:
                        analysis = {"summary": "Analyst throttled by cooldown window."}
                    state = "MITIGATED"
                else:
                    response = {"action": "monitor", "reason": "Benign traffic"}
                    analysis = {"summary": "No mitigation required for benign event."}
                    state = "MONITORED"

                self._set_state(
                    incident_id,
                    state,
                    {
                        "response": response,
                        "analysis": analysis,
                    },
                )

                result = {
                    "incident_id": incident_id,
                    "status": state.lower(),
                    **judged,
                    "rule_generated": response.get("rule_generated"),
                    "trust_score_after": response.get("trust_score_after"),
                    "action": response.get("action", "monitor"),
                    "priority": judged.get("priority"),
                    "category": judged.get("category"),
                }
                self._resolve_pending(incident_id, result)

                if judged.get("is_threat") and judged.get("severity") in ("CRITICAL", "HIGH"):
                    now = datetime.utcnow()
                    if (
                        self._last_selfheal_at is None
                        or now - self._last_selfheal_at >= timedelta(seconds=SELFHEAL_COOLDOWN_SECONDS)
                    ):
                        await self.heal_queue.put({"incident_id": incident_id})
                        self._last_selfheal_at = now
            except Exception as exc:
                self._set_state(incident_id, "FAILED_DEFEND", {"error": str(exc)})
                self._resolve_pending(
                    incident_id,
                    {"incident_id": incident_id, "status": "error", "stage": "defend", "error": str(exc)},
                )
            finally:
                db.close()
                self.defend_queue.task_done()

    async def _healer_loop(self):
        while self._running:
            payload = await self.heal_queue.get()
            incident_id = payload["incident_id"]
            db = SessionLocal()
            try:
                heal_result = await selfheal.process(db=db)
                self._set_state(
                    incident_id,
                    "HEALED",
                    {"healed": True, "heal_result": heal_result},
                )
            except Exception as exc:
                self._set_state(incident_id, "FAILED_HEAL", {"error": str(exc)})
            finally:
                db.close()
                self.heal_queue.task_done()


runtime = AutonomousRuntime()
