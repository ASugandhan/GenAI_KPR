"""
ZeroTrust AI — ORM Models
All 6 database tables as SQLAlchemy models.
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from core.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime, default=func.now())
    src_ip = Column(String(45))
    dst_ip = Column(String(45))
    port = Column(Integer)
    protocol = Column(String(10))
    attack_type = Column(String(50))
    confidence = Column(Float)
    severity = Column(String(20))
    agent = Column(String(30))
    reasoning = Column(Text)
    resolved = Column(Boolean, default=False)


class Rule(Base):
    __tablename__ = "rules"

    id = Column(String(36), primary_key=True)
    event_id = Column(String(36), ForeignKey("events.id"))
    action = Column(String(30))
    rule_text = Column(Text)
    iptables_cmd = Column(Text)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)
    human_approved = Column(Boolean, nullable=True)


class TrustScore(Base):
    __tablename__ = "trust_scores"

    device_id = Column(String(36), primary_key=True)
    ip_address = Column(String(45))
    trust_score = Column(Float, default=100.0)
    anomaly_count = Column(Integer, default=0)
    last_threat = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=func.now())


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True)
    generated_at = Column(DateTime, default=func.now())
    time_window = Column(String(50))
    summary = Column(Text)
    correlations = Column(Text)
    predicted_next = Column(Text)


class SelfHealLog(Base):
    __tablename__ = "selfheal_log"

    id = Column(String(36), primary_key=True)
    incident_id = Column(String(36))
    triggered_at = Column(DateTime, default=func.now())
    health_score_before = Column(Float)
    health_score_after = Column(Float)
    permanent_rules = Column(Text)
    lessons_learned = Column(Text)
    hardening_recommendations = Column(Text)


class SystemHealth(Base):
    __tablename__ = "system_health"

    id = Column(Integer, primary_key=True, default=1)
    health_score = Column(Float, default=100.0)
    last_updated = Column(DateTime, default=func.now())
    total_healed = Column(Integer, default=0)
