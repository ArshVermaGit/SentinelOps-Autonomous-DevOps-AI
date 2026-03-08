from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class PullRequest(Base):
    __tablename__ = "pull_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    github_pr_number = Column(Integer, nullable=False)
    repo_id = Column(Integer, ForeignKey("repositories.id"))
    
    # PR metadata
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    base_branch = Column(String, default="main")
    head_branch = Column(String, nullable=False)
    
    # Risk analysis inputs
    lines_added = Column(Integer, default=0)
    lines_deleted = Column(Integer, default=0)
    files_changed = Column(Integer, default=0)
    file_types = Column(JSON, default=list)           # [".py", ".js", ...]
    has_config_changes = Column(Boolean, default=False)
    has_test_changes = Column(Boolean, default=False)
    has_dependency_changes = Column(Boolean, default=False)
    
    # Risk analysis outputs
    risk_probability = Column(Float, default=0.0)    # 0.0 - 1.0
    risk_level = Column(String, default="unknown")   # "safe" | "caution" | "high"
    risk_factors = Column(JSON, default=list)         # List of contributing factors
    
    # Status
    status = Column(String, default="open")          # "open" | "merged" | "closed"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="pull_requests")
    ci_runs = relationship("CIRun", back_populates="pull_request")
