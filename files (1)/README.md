# 🛡️ ZeroTrust AI — Next-Generation AI-Powered Firewall
> Hackathon Project | Problem Statement 17 | Multi-Agent Cybersecurity System

---

## 🧠 What This Is

A **Multi-Agent AI Firewall** that detects, classifies, and responds to network threats in real time using three autonomous AI agents operating within a Zero Trust architecture. No device is ever implicitly trusted. Every packet is evaluated. Every decision is explainable.

---

## 🏗️ System Architecture

```
Network Traffic (Simulated)
         ↓
  ┌──────────────┐
  │   SENTINEL   │  ← Detects + Classifies threats (ML + LLM reasoning)
  │    AGENT     │
  └──────┬───────┘
         ↓ (escalates upward)
  ┌──────────────┐
  │  TACTICIAN   │  ← Generates adaptive firewall rules + proportional response
  │    AGENT     │
  └──────┬───────┘
         ↓ (escalates upward)
  ┌──────────────┐
  │   ANALYST    │  ← Correlates patterns, predicts attack chains, MITRE mapping
  │    AGENT     │
  └──────┬───────┘
         ↓
  ┌──────────────┐
  │   FASTAPI    │  ← REST API Backend
  │   BACKEND    │
  └──────┬───────┘
         ↓
  ┌──────────────┐
  │  NEXT.JS     │  ← Real-time Dashboard (React frontend)
  │  FRONTEND    │
  └──────────────┘
```

---

## 🗂️ Folder Structure

```
zerotrust-ai/
│
├── backend/                          # Python FastAPI backend
│   ├── main.py                       # FastAPI app entry point
│   ├── config.py                     # Environment variables + constants
│   │
│   ├── api/                          # All route handlers
│   │   ├── __init__.py
│   │   ├── traffic.py                # GET /api/traffic/stream (SSE)
│   │   ├── detect.py                 # POST /api/detect
│   │   ├── rules.py                  # GET/POST /api/rules
│   │   ├── trust.py                  # GET /api/trust
│   │   ├── summarize.py              # POST /api/summarize (Gemini)
│   │   ├── selfheal.py               # POST /api/selfheal (Gemini)
│   │   └── logs.py                   # GET /api/logs
│   │
│   ├── agents/                       # The 4 AI Agents
│   │   ├── __init__.py
│   │   ├── base_agent.py             # Base Agent class
│   │   ├── sentinel_agent.py         # Detection + Classification
│   │   ├── tactician_agent.py        # Rule Generation + Response
│   │   ├── analyst_agent.py          # Correlation + MITRE mapping
│   │   └── selfheal_agent.py         # Post-incident hardening (Gemini)
│   │
│   ├── ml/                           # Machine Learning
│   │   ├── train.py                  # Training script (run once)
│   │   ├── predict.py                # Inference wrapper
│   │   ├── simulator.py              # Fake traffic packet generator
│   │   └── models/                   # Saved model files
│   │       ├── xgboost_clf.pkl
│   │       ├── iso_forest.pkl
│   │       ├── scaler.pkl
│   │       └── label_encoder.pkl
│   │
│   ├── core/                         # Core business logic
│   │   ├── database.py               # SQLAlchemy + SQLite setup
│   │   ├── models.py                 # DB ORM schemas
│   │   ├── rule_engine.py            # Safe rule generation (intent → command)
│   │   ├── trust_engine.py           # Zero Trust score management
│   │   └── safety_guard.py           # LLM output validation layer
│   │
│   └── utils/
│       ├── logger.py                 # Structured event logging
│       └── llm.py                    # Claude API wrapper + fallback
│
├── frontend/                         # Next.js 14 + React frontend
│   ├── package.json
│   ├── next.config.js
│   ├── .env.local                    # NEXT_PUBLIC_API_URL
│   │
│   ├── app/                          # Next.js 14 App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx                  # Dashboard home
│   │   └── globals.css
│   │
│   ├── components/
│   │   ├── LiveFeed.tsx              # Real-time packet stream (SSE)
│   │   ├── ThreatPanel.tsx           # Classified threats table
│   │   ├── RuleEngine.tsx            # Generated firewall rules
│   │   ├── TrustScores.tsx           # Per-device Zero Trust scores
│   │   ├── AnalystChat.tsx           # LLM analyst chat interface
│   │   ├── AttackChain.tsx           # MITRE ATT&CK chain visualization
│   │   └── charts/
│   │       ├── ThreatTimeline.tsx    # Recharts timeline
│   │       ├── TrustGauge.tsx        # Trust score gauge
│   │       └── TrafficHeatmap.tsx    # Traffic volume heatmap
│   │
│   └── lib/
│       ├── api.ts                    # API call wrappers
│       ├── types.ts                  # TypeScript interfaces
│       └── useSSE.ts                 # Server-Sent Events hook
│
├── data/
│   └── UNSW_NB15_sample.csv          # Training dataset (download separately)
│
├── .env                              # Backend environment variables
├── requirements.txt                  # Python dependencies
├── run.sh                            # Start everything with one command
└── README.md
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/traffic/stream` | SSE stream of live packets (1/500ms) |
| `POST` | `/api/detect` | Run packet through Sentinel Agent |
| `GET` | `/api/rules` | Fetch all active firewall rules |
| `POST` | `/api/rules/override` | Human override a rule (approve/reject) |
| `GET` | `/api/trust` | All device trust scores |
| `GET` | `/api/trust/{device_id}` | Single device trust score |
| `POST` | `/api/summarize` | Trigger Analyst Agent LLM report |
| `POST` | `/api/selfheal` | Trigger Self-Healing Agent post-incident |
| `GET` | `/api/health-score` | Get current system health score |
| `GET` | `/api/logs` | Paginated threat event logs |
| `GET` | `/api/health` | System health check |

### Sample Request/Response

**POST `/api/detect`**
```json
// Request
{
  "src_ip": "192.168.1.45",
  "dst_ip": "10.0.0.1",
  "port": 22,
  "protocol": "TCP",
  "bytes": 8420,
  "duration": 0.3,
  "packet_count": 847
}

// Response
{
  "threat_id": "uuid-here",
  "is_threat": true,
  "attack_type": "brute_force",
  "confidence": 0.91,
  "reasoning": "847 packets in 0.3s to port 22 from internal IP...",
  "agent": "sentinel",
  "rule_generated": {
    "action": "rate_limit",
    "rule_text": "Rate limit 192.168.1.45 to 10 req/s on port 22",
    "iptables_cmd": "iptables -A INPUT -s 192.168.1.45 -p tcp --dport 22 -m limit --limit 10/s -j ACCEPT"
  },
  "trust_score_after": 55.0
}
```

---

## 🤖 Agent Behavior

### Sentinel Agent
- Runs ML model (XGBoost) on every packet
- If confidence 0.4–0.8 → calls LLM for contextual reasoning
- If confidence > 0.8 → auto-classifies without LLM (speed)
- Outputs: `{verdict, attack_type, confidence, reasoning}`

### Tactician Agent
- Receives Sentinel verdict
- Decides proportional response: `monitor → rate_limit → block_temp → block_perm`
- Trust score < 20 required for permanent block
- Never blocks internal gateway IPs (hardcoded safety constraint)
- Outputs: `{action, rule_text, iptables_cmd, severity, justification}`

### Analyst Agent
- Runs every 60 seconds OR on-demand
- Correlates events across all devices in time window
- Maps to 5 MITRE ATT&CK patterns: T1046, T1110, T1021, T1059, T1190
- Predicts next-stage attack based on current pattern
- Outputs: `{insights, correlations, predicted_next_attack, recommended_escalations}`

### Self-Healing Agent (Post-Incident)
- Triggers automatically after every CRITICAL or HIGH incident is resolved
- Calls Gemini with: incident summary + actions taken + outcome
- Asks Gemini: "Was response optimal? What rules should be permanent? What patterns to watch next?"
- Writes permanent rules back to rule store
- Updates system health score on dashboard (starts 100, improves after each healed incident)
- Outputs: `{permanent_rules, hardening_recommendations, health_score_delta, lessons_learned}`

---

## 🔐 Zero Trust Logic

```
Trust Score: 0 → 100 (starts at 100 for all devices)

Decay rules:
- Critical threat detected    → -30 points
- High threat detected        → -15 points  
- Medium threat detected      → -8 points
- Low/suspicious activity     → -3 points

Recovery:
- +1 point per clean minute (max 100)

Action thresholds:
- Score 70–100  → Monitor only
- Score 40–69   → Rate limit + alert
- Score 20–39   → Temporary block (5 min TTL)
- Score 0–19    → Hard block + human escalation required
```

---

## 🧱 Database Schema

```sql
CREATE TABLE events (
    id          TEXT PRIMARY KEY,
    timestamp   DATETIME,
    src_ip      TEXT,
    dst_ip      TEXT,
    port        INTEGER,
    protocol    TEXT,
    attack_type TEXT,
    confidence  REAL,
    severity    TEXT,
    agent       TEXT,
    reasoning   TEXT,
    resolved    BOOLEAN DEFAULT FALSE
);

CREATE TABLE rules (
    id              TEXT PRIMARY KEY,
    event_id        TEXT REFERENCES events(id),
    action          TEXT,
    rule_text       TEXT,
    iptables_cmd    TEXT,
    created_at      DATETIME,
    expires_at      DATETIME,
    active          BOOLEAN DEFAULT TRUE,
    human_approved  BOOLEAN DEFAULT NULL
);

CREATE TABLE trust_scores (
    device_id       TEXT PRIMARY KEY,
    ip_address      TEXT,
    trust_score     REAL DEFAULT 100.0,
    anomaly_count   INTEGER DEFAULT 0,
    last_threat     DATETIME,
    last_updated    DATETIME
);

CREATE TABLE reports (
    id              TEXT PRIMARY KEY,
    generated_at    DATETIME,
    time_window     TEXT,
    summary         TEXT,
    correlations    TEXT,
    predicted_next  TEXT
);

CREATE TABLE selfheal_log (
    id                      TEXT PRIMARY KEY,
    incident_id             TEXT,
    triggered_at            DATETIME,
    health_score_before     REAL,
    health_score_after      REAL,
    permanent_rules         TEXT,
    lessons_learned         TEXT,
    hardening_recommendations TEXT
);

CREATE TABLE system_health (
    id              INTEGER PRIMARY KEY DEFAULT 1,
    health_score    REAL DEFAULT 100.0,
    last_updated    DATETIME,
    total_healed    INTEGER DEFAULT 0
);
```

---

## 🚀 How to Run

```bash
# 1. Clone repo
git clone <repo-url>
cd zerotrust-ai

# 2. Backend setup
cd backend
pip install -r requirements.txt
python ml/train.py          # Train models once (takes ~2 mins)
uvicorn main:app --reload --port 8000

# 3. Frontend setup (new terminal)
cd frontend
npm install
npm run dev                 # Runs on localhost:3000

# OR run everything at once
chmod +x run.sh
./run.sh
```

---

## ⚡ Offline Fallback

If Claude API is unavailable during demo:
- System automatically switches to `MOCK_LLM=true` mode
- 5 pre-cached reasoning responses cover all attack types
- Zero visible difference in demo behavior
- Set `OFFLINE_MODE=true` in `.env` to force this

---

## 🎯 MITRE ATT&CK Patterns Mapped

| Pattern | Techniques | Description |
|---------|-----------|-------------|
| Reconnaissance → Exploit | T1046 → T1190 | Port scan followed by exploit attempt |
| Brute Force → Lateral Move | T1110 → T1021 | Credential attack then internal spread |
| C2 Beacon | T1059 | Command and control communication |
| DDoS Escalation | T1498 | Volumetric attack pattern |
| Insider Threat | T1078 | Anomalous internal device behavior |

---

## 👥 Team Build Split

| Person | Owns |
|--------|------|
| ML Engineer | `backend/ml/` — training, inference, simulator |
| Backend Dev | `backend/api/` + `backend/core/` — all routes + DB |
| Frontend Dev | `frontend/` — all components + SSE integration |
| Floater | `backend/agents/` — all 4 agents including selfheal + Gemini wiring |
