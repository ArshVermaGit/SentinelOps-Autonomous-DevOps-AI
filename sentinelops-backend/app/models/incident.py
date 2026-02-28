from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    ci_run_id = Column(Integer, ForeignKey("ci_runs.id"), unique=True)
    
    # LLM Root Cause Analysis
    root_cause = Column(Text, nullable=True)
    responsible_files = Column(JSON, default=list)
    error_category = Column(String, nullable=True)   # "dependency|syntax|test|config|runtime|network"
    llm_confidence = Column(Float, default=0.0)
    
    # Fix suggestion
    suggested_fix = Column(Text, nullable=True)
    fix_diff = Column(Text, nullable=True)           # Unified diff format
    estimated_fix_time = Column(String, nullable=True)
    risk_if_unresolved = Column(Text, nullable=True)
    
    # Similarity
    similar_incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    similarity_score = Column(Float, default=0.0)    # 0.0 - 1.0
    
    # Resolution
    status = Column(String, default="open")          # "open" | "simulated" | "resolved"
    simulation_result = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ci_run = relationship("CIRun", back_populates="incident")
