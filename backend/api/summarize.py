"""
ZeroTrust AI — Summarize API
POST /api/summarize — Trigger Analyst Agent to generate LLM report.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from agents.analyst_agent import analyst
from utils.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Analyst"])


@router.post("/summarize")
async def summarize(user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Trigger the Analyst Agent to generate an intelligence report."""
    result = await analyst.process(db=db)
    return result
