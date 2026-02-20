# ZeroTrust AI — Production Upgrades
> Hand this to anti-gravity. Implement in order. Do not skip steps.

---

## ⏱ Time: 2 hrs 56 mins remaining
## Priority: Do in this exact order. Stop at whatever is done by 4:15.

---

## Upgrade 1 — JWT Authentication (Priority: CRITICAL)
**Time estimate: 60 mins**

### Install
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

### File 1 — Create `backend/utils/auth.py`
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "zerotrust-secret-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({**data, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### File 2 — Create `backend/api/auth.py`
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.auth import hash_password, verify_password, create_token

router = APIRouter()

# Demo users — hardcoded, no DB needed
USERS = {
    "admin": hash_password("zerotrust123"),
    "analyst": hash_password("analyst123")
}

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(req: LoginRequest):
    hashed = USERS.get(req.username)
    if not hashed or not verify_password(req.password, hashed):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": req.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def me(user: str = Depends(get_current_user)):
    return {"username": user, "role": "admin" if user == "admin" else "analyst"}
```

### File 3 — Edit `backend/main.py` (add these lines)
```python
from api.auth import router as auth_router
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
```

### File 4 — Protect these 2 routes only
In `backend/api/detect.py`:
```python
from utils.auth import get_current_user
from fastapi import Depends

@router.post("/detect")
async def detect(packet: dict, user=Depends(get_current_user)):
    ...  # existing code unchanged
```

In `backend/api/rules.py`:
```python
from utils.auth import get_current_user
from fastapi import Depends

@router.get("/rules")
async def get_rules(user=Depends(get_current_user)):
    ...  # existing code unchanged
```

### Frontend — Add Login Page
Create `frontend/app/login/page.tsx`:
```tsx
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleLogin = async () => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (res.ok) {
      const data = await res.json();
      localStorage.setItem("token", data.access_token);
      router.push("/");
    } else {
      setError("Invalid credentials");
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="bg-gray-900 border border-green-500 rounded-lg p-8 w-96">
        <h1 className="text-green-400 text-2xl font-bold mb-2">🛡️ ZeroTrust AI</h1>
        <p className="text-gray-400 text-sm mb-6">Secure Authentication Required</p>
        <input
          className="w-full bg-gray-800 text-white border border-gray-600 rounded p-2 mb-3"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          className="w-full bg-gray-800 text-white border border-gray-600 rounded p-2 mb-4"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p className="text-red-400 text-sm mb-3">{error}</p>}
        <button
          onClick={handleLogin}
          className="w-full bg-green-600 hover:bg-green-500 text-white rounded p-2 font-bold"
        >
          LOGIN
        </button>
        <p className="text-gray-600 text-xs mt-4 text-center">
          Demo: admin / zerotrust123
        </p>
      </div>
    </div>
  );
}
```

### Test Auth Works
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "zerotrust123"}'

# Should return: {"access_token": "eyJ...", "token_type": "bearer"}
```

---

## Upgrade 2 — Rate Limiting (Priority: HIGH)
**Time estimate: 20 mins**

### Install
```bash
pip install slowapi
```

### Edit `backend/main.py`
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### Add to `backend/api/detect.py`
```python
from main import limiter
from fastapi import Request

@router.post("/detect")
@limiter.limit("100/minute")
async def detect(request: Request, packet: dict, user=Depends(get_current_user)):
    ...  # existing code unchanged
```

---

## Upgrade 3 — MySQL Migration (Priority: MEDIUM)
**Time estimate: 30 mins**
**Only do this if Upgrades 1 and 2 are done and time remains**

### Install
```bash
pip install pymysql cryptography alembic
```

### Create database
```sql
CREATE DATABASE zerotrust_ai;
```

### Update `.env`
```env
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/zerotrust_ai
```

### Run migrations
```bash
cd backend
alembic init alembic
alembic revision --autogenerate -m "init"
alembic upgrade head
```

No code changes needed — SQLAlchemy handles the rest.

---

## Upgrade 4 — Real Packet Capture (Priority: LOW)
**Time estimate: 30 mins**
**Only do this if all above are done**

### Install
```bash
pip install scapy
```

### Edit `backend/ml/simulator.py` — add at top
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

### Toggle in `.env`
```env
# Keep as simulator for demo safety
PACKET_SOURCE=simulator

# Switch to live on real network
# PACKET_SOURCE=live
# CAPTURE_INTERFACE=eth0
```

---

## Demo Credentials (Tell Judges)
| Username | Password | Role |
|----------|----------|------|
| admin | zerotrust123 | Full access |
| analyst | analyst123 | Read-only |

---

## Stop Coding at 4:15
Last 15 minutes = demo rehearsal only.
Run through the full flow 2 times:
1. Open login page → login as admin
2. Watch live feed populate
3. Trigger a threat via Swagger
4. Watch rule generate + trust score drop
5. Watch self-heal fire

That's your demo. Don't add anything else.
