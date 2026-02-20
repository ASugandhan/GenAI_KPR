from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from utils.auth import hash_password, verify_password, create_token, get_current_user

router = APIRouter()

# Demo users — hardcoded, no DB needed
USERS = {
    "admin": "zerotrust123",
    "analyst": "analyst123"
}

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(req: LoginRequest):
    password = USERS.get(req.username)
    if not password or req.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": req.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def me(user: str = Depends(get_current_user)):
    return {"username": user, "role": "admin" if user == "admin" else "analyst"}
