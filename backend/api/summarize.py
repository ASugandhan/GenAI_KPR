"""
ZeroTrust AI — Summarize API
POST /api/summarize — Trigger Analyst Agent to generate LLM report.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from agents.analyst_agent import analyst

router = APIRouter(prefix="/api", tags=["Analyst"])


@router.post("/summarize")
async def summarize(db: Session = Depends(get_db)):
    """Trigger the Analyst Agent to generate an intelligence report."""
    result = await analyst.process(db=db)
    return result
