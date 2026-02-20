# ZeroTrust AI — Complete System Test Checklist
> Anti-gravity: Run every check. Report exact error if anything fails.

---

## Pre-Flight (Run First)
```powershell
# Terminal 1 — Start Backend
cd "E:\E\Project\prj idea-8\backend"
uvicorn main:app --reload --port 8000

# Terminal 2 — Start Frontend
cd "E:\E\Project\prj idea-8\frontend"
npm run dev
```
- [ ] Backend starts with no red errors
- [ ] Frontend starts with no red errors
- [ ] `http://localhost:8000/docs` loads Swagger UI
- [ ] `http://localhost:3000` loads dashboard

---

## 1. Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method GET
```
- [ ] Returns `{"status": "healthy"}`

---

## 2. Authentication
```powershell
# Login
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -ContentType "application/json" -Body '{"username": "admin", "password": "zerotrust123"}'
```
- [ ] Returns `access_token`
- [ ] Wrong password returns 401

Save the token:
```powershell
$token = (Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -ContentType "application/json" -Body '{"username": "admin", "password": "zerotrust123"}').access_token
```

---

## 3. Threat Detection
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/detect" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"src_ip":"192.168.1.45","dst_ip":"10.0.0.1","port":22,"protocol":"TCP","bytes":8420,"duration":0.3,"packet_count":847}'
```
- [ ] Returns threat classification
- [ ] Returns `attack_type` field
- [ ] Returns `confidence` score
- [ ] Without token returns 401

---

## 4. Trust Scores
```powershell
# All devices
Invoke-RestMethod -Uri "http://localhost:8000/api/trust" -Method GET -Headers @{Authorization="Bearer $token"}

# Single device
Invoke-RestMethod -Uri "http://localhost:8000/api/trust/192.168.1.45" -Method GET -Headers @{Authorization="Bearer $token"}
```
- [ ] Returns trust scores list
- [ ] `192.168.1.45` score is below 100 (dropped after detect test above)

---

## 5. Firewall Rules
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/rules" -Method GET -Headers @{Authorization="Bearer $token"}
```
- [ ] Returns list of generated rules
- [ ] At least 1 rule exists after detect test above
- [ ] Without token returns 401

---

## 6. Live Traffic Stream
Open browser: `http://localhost:8000/api/traffic/stream`
- [ ] Page shows continuous streaming data
- [ ] New packets appear every 500ms
- [ ] Mix of normal and attack packets visible

---

## 7. Analyst Summarize
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/summarize" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"time_window": "1h", "format": "analyst"}'
```
- [ ] Returns LLM-generated summary
- [ ] Contains `threat_count` field
- [ ] Contains `recommended_actions`

---

## 8. Self-Heal
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/selfheal" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"incident_id": "test-001", "severity": "HIGH"}'
```
- [ ] Returns hardening recommendations
- [ ] Returns updated health score
- [ ] Health score is above previous value

---

## 9. Logs
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/logs" -Method GET -Headers @{Authorization="Bearer $token"}
```
- [ ] Returns paginated event list
- [ ] Events from detect test appear here
- [ ] Timestamps are correct

---

## 10. Rate Limiting
```powershell
# Run this 5 times fast to confirm rate limiter is active
1..5 | ForEach-Object {
    Invoke-RestMethod -Uri "http://localhost:8000/api/detect" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"src_ip":"1.1.1.1","dst_ip":"10.0.0.1","port":80,"protocol":"TCP","bytes":100,"duration":0.1,"packet_count":1}'
}
```
- [ ] First requests succeed
- [ ] After 100/min limit → returns 429 Too Many Requests

---

## 11. Frontend Pages
Open browser and check each:

- [ ] `http://localhost:3000/login` — Login page loads
- [ ] Login with `admin / zerotrust123` → redirects to dashboard
- [ ] Dashboard shows live packet feed updating in real time
- [ ] ThreatPanel shows detected threats
- [ ] RuleEngine shows generated firewall rules
- [ ] TrustScores shows per-IP scores
- [ ] AnalystChat returns response when queried
- [ ] Health score widget visible on dashboard
- [ ] No red errors in browser console (F12 → Console tab)

---

## 12. End-to-End Flow
Do this manually as a full demo run:
1. [ ] Open `localhost:3000/login` → login as admin
2. [ ] Dashboard loads → packets streaming in LiveFeed
3. [ ] Run detect API call → threat appears in ThreatPanel
4. [ ] Check trust score dropped for that IP in TrustScores
5. [ ] Check firewall rule appeared in RuleEngine
6. [ ] Run selfheal → health score updates on dashboard
7. [ ] Open AnalystChat → ask "What happened in the last hour?" → LLM responds

---

## 13. MySQL Connection (If Migrated)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method GET
```
- [ ] Server starts without DB connection errors
- [ ] Data persists after restarting backend
- [ ] Events from before restart still appear in logs

---

## Results Summary
Fill this before reporting back:

| Check | Status | Error (if any) |
|-------|--------|----------------|
| Health | ✅/❌ | |
| Auth Login | ✅/❌ | |
| Threat Detect | ✅/❌ | |
| Trust Scores | ✅/❌ | |
| Firewall Rules | ✅/❌ | |
| Traffic Stream | ✅/❌ | |
| Summarize | ✅/❌ | |
| Self-Heal | ✅/❌ | |
| Logs | ✅/❌ | |
| Rate Limiting | ✅/❌ | |
| Frontend Pages | ✅/❌ | |
| End-to-End Flow | ✅/❌ | |
| MySQL | ✅/❌ | |

---

## All Green?
**Stop coding. Start rehearsing the demo.**

## Something Red?
Report back with:
- Which check number failed
- Exact error message shown
- What the terminal says at that moment
