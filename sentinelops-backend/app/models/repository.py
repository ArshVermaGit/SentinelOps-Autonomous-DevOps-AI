from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, index=True)
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)  # "owner/repo"
    url = Column(String, nullable=False)
    
    # Risk metrics
    risk_score = Column(Float, default=0.0)        # 0.0 - 1.0
    failure_rate = Column(Float, default=0.0)      # Historical failure rate
    avg_build_time_ms = Column(Integer, default=0)
    deployment_stability = Column(Float, default=1.0)  # 0.0 - 1.0
    
    # Tracking
    last_analyzed = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pull_requests = relationship("PullRequest", back_populates="repository")
    ci_runs = relationship("CIRun", back_populates="repository")
