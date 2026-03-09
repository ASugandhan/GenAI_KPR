from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from utils.auth import hash_password, verify_password, create_token, get_current_user

router = APIRouter()

# Demo users with hashed passwords (replace with DB-backed users in production)
USERS = {
    "admin": hash_password("zerotrust123"),
    "analyst": hash_password("analyst123"),
}

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(req: LoginRequest):
    password_hash = USERS.get(req.username)
    if not password_hash or not verify_password(req.password, password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": req.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def me(user: str = Depends(get_current_user)):
    return {"username": user, "role": "admin" if user == "admin" else "analyst"}
