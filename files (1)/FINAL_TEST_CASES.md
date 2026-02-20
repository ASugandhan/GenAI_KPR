# ZeroTrust AI — Final Test Cases
> Anti-gravity: Run every single test. Fill the result column. No skipping.

---

## Setup Before Testing
```powershell
# Terminal 1 — Backend
cd "E:\E\Project\prj idea-8\backend"
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd "E:\E\Project\prj idea-8\frontend"
npm run dev

# Save token for all tests below
$token = (Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -ContentType "application/json" -Body '{"username": "admin", "password": "zerotrust123"}').access_token
echo $token
```

---

## SECTION 1 — System Health

| # | Test | Command | Expected | Result |
|---|------|---------|----------|--------|
| 1.1 | Backend running | Open `http://localhost:8000/docs` | Swagger UI loads | ✅/❌ |
| 1.2 | Frontend running | Open `http://localhost:3000` | Dashboard loads | ✅/❌ |
| 1.3 | Health endpoint | `Invoke-RestMethod -Uri "http://localhost:8000/api/health"` | `{"status":"healthy"}` | ✅/❌ |
| 1.4 | No console errors | F12 → Console tab on dashboard | No red errors | ✅/❌ |
| 1.5 | MySQL connected | Backend starts with no DB errors in terminal | Clean startup logs | ✅/❌ |

---

## SECTION 2 — Authentication

| # | Test | Command | Expected | Result |
|---|------|---------|----------|--------|
| 2.1 | Valid login | `Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -ContentType "application/json" -Body '{"username":"admin","password":"zerotrust123"}'` | Returns `access_token` | ✅/❌ |
| 2.2 | Analyst login | Same but `analyst / analyst123` | Returns `access_token` | ✅/❌ |
| 2.3 | Wrong password | Same but `password:"wrongpass"` | Returns 401 | ✅/❌ |
| 2.4 | Wrong username | Same but `username:"hacker"` | Returns 401 | ✅/❌ |
| 2.5 | No token on protected route | `Invoke-RestMethod -Uri "http://localhost:8000/api/detect" -Method POST -ContentType "application/json" -Body '{}'` | Returns 401 | ✅/❌ |
| 2.6 | Invalid token | Add `-Headers @{Authorization="Bearer faketoken123"}` to any protected route | Returns 401 | ✅/❌ |
| 2.7 | Frontend login page | Open `http://localhost:3000/login` | Login page renders | ✅/❌ |
| 2.8 | Frontend login success | Login as `admin / zerotrust123` | Redirects to dashboard | ✅/❌ |
| 2.9 | Frontend login fail | Login as `admin / wrongpass` | Shows error message | ✅/❌ |
| 2.10 | /me endpoint | `Invoke-RestMethod -Uri "http://localhost:8000/api/auth/me" -Headers @{Authorization="Bearer $token"}` | Returns username + role | ✅/❌ |

---

## SECTION 3 — Threat Detection

| # | Test | Command | Expected | Result |
|---|------|---------|----------|--------|
| 3.1 | Brute force detect | `Invoke-RestMethod -Uri "http://localhost:8000/api/detect" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"src_ip":"192.168.1.45","dst_ip":"10.0.0.1","port":22,"protocol":"TCP","bytes":8420,"duration":0.3,"packet_count":847}'` | Returns `attack_type` + `confidence` | ✅/❌ |
| 3.2 | Normal traffic | Same but `port:80, bytes:1200, packet_count:3` | Returns low threat / normal | ✅/❌ |
| 3.3 | DDoS pattern | Same but `bytes:1500000, packet_count:9999, duration:0.1` | Returns ddos classification | ✅/❌ |
| 3.4 | Port scan | Same but `port:4444, packet_count:500, duration:0.5` | Returns port_scan | ✅/❌ |
| 3.5 | Confidence score | Any detect call | `confidence` between 0 and 1 | ✅/❌ |
| 3.6 | Response time | Any detect call | Response under 3 seconds | ✅/❌ |

---

## SECTION 4 — Trust Scores

| # | Test | Command | Expected | Result |
|---|------|---------|----------|--------|
| 4.1 | Get all scores | `Invoke-RestMethod -Uri "http://localhost:8000/api/trust" -Headers @{Authorization="Bearer $token"}` | Returns list of devices | ✅/❌ |
| 4.2 | Get single IP | `Invoke-RestMethod -Uri "http://localhost:8000/api/trust/192.168.1.45" -Headers @{Authorization="Bearer $token"}` | Returns score for that IP | ✅/❌ |
| 4.3 | Score dropped | After Section 3 tests, check 192.168.1.45 | Score below 100 | ✅/❌ |
| 4.4 | Critical IP blocked | IP with score below 20 | Status shows blocked | ✅/❌ |

---

## SECTION 5 — Firewall Rules

| # | Test | Command | Expected | Result |
|---|------|---------|----------|--------|
| 5.1 | Get all rules | `Invoke-RestMethod -Uri "http://localhost:8000/api/rules" -Headers @{Authorization="Bearer $token"}` | Returns rules list | ✅/❌ |
| 5.2 | Rules generated | After Section 3 tests | At least 1 rule exists | ✅/❌ |
| 5.3 | Rule has iptables command | Check any rule object | Contains `iptables_cmd` field | ✅/❌ |
| 5.4 | Rule has expiry | Check any rule object | Contains `expires_at` field | ✅/❌ |
| 5.5 | No token on rules | Without Authorization header | Returns 401 | ✅/❌ |

---

## SECTION 6 — Live Traffic Stream

| # | Test | Command | Expected | Result |
|---|------|---------|----------|--------|
| 6.1 | SSE stream active | Open `http://localhost:8000/api/traffic/stream` in browser | Continuous data flowing | ✅/❌ |
| 6.2 | Packets have required fields | Check stream output | `src_ip, dst_ip, port, protocol, bytes` all present | ✅/❌ |
| 6.3 | Mix of traffic | Watch stream for 30 seconds | Both normal and attack packets appear | ✅/❌ |
| 6.4 | Frontend live feed | Dashboard LiveFeed component | Packets updating in real time | ✅/❌ |

---

## SECTION 7 — Analyst & Self-Heal

| # | Test | Command | Expected | Result |
|---|------|---------|----------|--------|
| 7.1 | Summarize | `Invoke-RestMethod -Uri "http://localhost:8000/api/summarize" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"time_window":"1h","format":"analyst"}'` | Returns LLM summary text | ✅/❌ |
| 7.2 | Summary has threat count | Check response | Contains `threat_count` field | ✅/❌ |
| 7.3 | Self-heal trigger | `Invoke-RestMethod -Uri "http://localhost:8000/api/selfheal" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"incident_id":"test-001","severity":"HIGH"}'` | Returns recommendations | ✅/❌ |
| 7.4 | Health score updates | After self-heal | `health_score_after` higher than `health_score_before` | ✅/❌ |
| 7.5 | Analyst chat UI | Dashboard AnalystChat component | Sends message, gets LLM response | ✅/❌ |

---

## SECTION 8 — Logs & Audit

| # | Test | Command | Expected | Result |
|---|------|---------|----------|--------|
| 8.1 | Get logs | `Invoke-RestMethod -Uri "http://localhost:8000/api/logs" -Headers @{Authorization="Bearer $token"}` | Returns paginated events | ✅/❌ |
| 8.2 | Logs have events | After all Section 3 tests | At least 4 events in log | ✅/❌ |
| 8.3 | Filter by severity | `http://localhost:8000/api/logs?severity=HIGH` | Returns only HIGH events | ✅/❌ |
| 8.4 | Events have timestamps | Check any log entry | `timestamp` field present and valid | ✅/❌ |

---

## SECTION 9 — Rate Limiting

| # | Test | Command | Expected | Result |
|---|------|---------|----------|--------|
| 9.1 | Normal requests pass | Run detect 5 times normally | All return 200 | ✅/❌ |
| 9.2 | Rate limit active | Run this: `1..110 \| ForEach-Object { Invoke-RestMethod -Uri "http://localhost:8000/api/detect" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"src_ip":"1.1.1.1","dst_ip":"10.0.0.1","port":80,"protocol":"TCP","bytes":100,"duration":0.1,"packet_count":1}' }` | After 100 requests returns 429 | ✅/❌ |

---

## SECTION 10 — MySQL Verification

| # | Test | Command | Expected | Result |
|---|------|---------|----------|--------|
| 10.1 | Tables exist | `mysql -u root -p -e "USE zerotrust_ai; SHOW TABLES;"` | Lists all tables | ✅/❌ |
| 10.2 | Data persists | Restart backend, check logs endpoint | Previous events still there | ✅/❌ |
| 10.3 | Events writing | `mysql -u root -p -e "USE zerotrust_ai; SELECT COUNT(*) FROM events;"` | Count increases after detect calls | ✅/❌ |
| 10.4 | Rules writing | `mysql -u root -p -e "USE zerotrust_ai; SELECT COUNT(*) FROM rules;"` | Count increases after detect calls | ✅/❌ |

---

## SECTION 11 — Scapy Verification

| # | Test | Command | Expected | Result |
|---|------|---------|----------|--------|
| 11.1 | Scapy installed | `pip show scapy` | Shows scapy version | ✅/❌ |
| 11.2 | Simulator still works | `PACKET_SOURCE=simulator` in .env, restart backend | Traffic stream works normally | ✅/❌ |
| 11.3 | No import errors | Backend starts with no scapy errors | Clean startup | ✅/❌ |

---

## SECTION 12 — End to End Demo Flow

Run this exactly as you will in front of judges:

| # | Step | Action | Expected | Result |
|---|------|--------|----------|--------|
| 12.1 | Open login | Go to `localhost:3000/login` | Login page loads | ✅/❌ |
| 12.2 | Login | Enter `admin / zerotrust123` | Redirects to dashboard | ✅/❌ |
| 12.3 | Live feed | Watch dashboard | Packets streaming in real time | ✅/❌ |
| 12.4 | Trigger threat | Run brute force detect call from Section 3.1 | Threat appears in ThreatPanel | ✅/❌ |
| 12.5 | Trust drops | Check TrustScores panel | 192.168.1.45 score dropped | ✅/❌ |
| 12.6 | Rule generated | Check RuleEngine panel | New rule appears | ✅/❌ |
| 12.7 | Self heal | Run selfheal call from Section 7.3 | Health score updates on dashboard | ✅/❌ |
| 12.8 | Analyst chat | Type "What happened in the last hour?" in chat | LLM responds with summary | ✅/❌ |
| 12.9 | Full flow time | Time the entire demo | Under 3 minutes | ✅/❌ |

---

## Final Score

Count your results:

- **40+ green** → Production ready. Stop coding. Go rehearse.
- **35-39 green** → Fix the red ones. Should take under 30 mins.
- **Below 35** → Report every red item with exact error message.

---

## If Anything is Red
Report back with:
1. Section number and test number (e.g. "3.3 failed")
2. Exact error message
3. What the terminal shows at that moment

Do NOT try to fix blindly. Report first.
