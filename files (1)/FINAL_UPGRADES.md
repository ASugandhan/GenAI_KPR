# ZeroTrust AI — Final Two Upgrades
> Anti-gravity: Do both in parallel. Hard stop at 4:00.

---

## Person 1 — MySQL Migration (30 mins)

### Step 1 — Create Database
```sql
mysql -u root -p
CREATE DATABASE IF NOT EXISTS zerotrust_ai;
exit;
```

### Step 2 — Run Migrations
```powershell
cd "E:\E\Project\prj idea-8\backend"
alembic revision --autogenerate -m "init"
alembic upgrade head
```

If you see `Target database is not up to date`:
```powershell
alembic stamp head
alembic upgrade head
```

### Step 3 — Restart Backend
```powershell
uvicorn main:app --reload --port 8000
```

### Step 4 — Verify
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method GET
```
Expected: `{"status": "healthy"}`

Then login and trigger a detect call. Check MySQL directly:
```sql
USE zerotrust_ai;
SHOW TABLES;
SELECT * FROM events LIMIT 5;
```
Expected: Tables exist, events are being written.

---

## Person 2 — Scapy Real Packet Capture (20 mins)

### Step 1 — Install
```powershell
pip install scapy
```

### Step 2 — Edit `backend/ml/simulator.py`
Add this block at the very top of the file, before anything else:
```python
import os
PACKET_SOURCE = os.getenv("PACKET_SOURCE", "simulator")

if PACKET_SOURCE == "live":
    from scapy.all import sniff, IP, TCP, UDP

    def capture_live(interface="eth0", callback=None):
        def process(pkt):
            if IP in pkt:
                data = {
                    "src_ip": pkt[IP].src,
                    "dst_ip": pkt[IP].dst,
                    "port": pkt[TCP].dport if TCP in pkt else (pkt[UDP].dport if UDP in pkt else 0),
                    "protocol": "TCP" if TCP in pkt else "UDP",
                    "bytes": len(pkt),
                    "duration": 0.1,
                    "packet_count": 1
                }
                if callback:
                    callback(data)
        sniff(iface=interface, prn=process, store=False)
```

### Step 3 — Add to `.env`
```env
# Keep as simulator for demo safety
PACKET_SOURCE=simulator

# Uncomment below for real network capture
# PACKET_SOURCE=live
# CAPTURE_INTERFACE=eth0
```

### Step 4 — Verify No Breakage
```powershell
uvicorn main:app --reload --port 8000
```
- Server must start with no errors
- `/api/traffic/stream` must still work
- If anything breaks → git reset immediately

---

## Both Done — Final Check
```powershell
# Health
Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method GET

# Login
$token = (Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -ContentType "application/json" -Body '{"username": "admin", "password": "zerotrust123"}').access_token

# Detect
Invoke-RestMethod -Uri "http://localhost:8000/api/detect" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"src_ip":"192.168.1.45","dst_ip":"10.0.0.1","port":22,"protocol":"TCP","bytes":8420,"duration":0.3,"packet_count":847}'
```

All green → you're done.
Any red → git reset, report the error.

---

## Hard Stop 4:00
Demo rehearsal starts at 4:00 no matter what.
