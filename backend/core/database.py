"""
ZeroTrust AI — Database Setup
SQLAlchemy engine + session factory (SQLite).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import DATABASE_URL

# MySQL/General engine creation
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    from core.models import Event, Rule, TrustScore, Report, SelfHealLog, SystemHealth  # noqa
    Base.metadata.create_all(bind=engine)
