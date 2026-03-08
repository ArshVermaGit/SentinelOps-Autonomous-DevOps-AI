"""
SentinelOps Incident Event Model — Timeline tracking for incident lifecycle.
Author: Arsh Verma
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from datetime import datetime
from app.core.database import Base

class IncidentEvent(Base):
    __tablename__ = "incident_events"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    
    # Event metadata
    event_type = Column(String, nullable=False)       # "created" | "analyzed" | "similar_found" | "fix_suggested" | "simulated" | "resolved"
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    event_data = Column(JSON, default=dict)           # Extra context per event type
    
    # Actor
    actor = Column(String, default="system")          # "system" | "ai" | "user"
    
    created_at = Column(DateTime, default=datetime.utcnow)
