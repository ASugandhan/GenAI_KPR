"""
ZeroTrust AI — Rules API
GET /api/rules — Fetch active firewall rules.
POST /api/rules/override — Human override (approve/reject).
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.database import get_db
from core.rule_engine import get_active_rules, override_rule

router = APIRouter(prefix="/api/rules", tags=["Rules"])


class OverrideInput(BaseModel):
    rule_id: str
    approved: bool


from utils.auth import get_current_user

@router.get("")
async def list_rules(user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all active firewall rules."""
    return {"rules": get_active_rules(db)}


@router.post("/override")
async def override(data: OverrideInput, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Human override — approve or reject a rule."""
    result = override_rule(db, data.rule_id, data.approved)
    return result
