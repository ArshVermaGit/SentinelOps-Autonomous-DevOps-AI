from datetime import datetime

from app.core.database import Base
from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


class CIRun(Base):
    __tablename__ = "ci_runs"

    id = Column(Integer, primary_key=True, index=True)
    github_run_id = Column(Integer, unique=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"))
    pr_id = Column(Integer, ForeignKey("pull_requests.id"), nullable=True)

    # Run metadata
    workflow_name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # "success" | "failure" | "running" | "cancelled"
    conclusion = Column(String, nullable=True)

    # Timing
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    duration_ms = Column(Integer, default=0)
    is_anomalous_duration = Column(Boolean, default=False)

    # Log analysis
    log_text = Column(Text, nullable=True)  # Raw log (truncated to last 200 lines)
    error_block = Column(Text, nullable=True)  # Extracted error section
    failure_step = Column(String, nullable=True)  # Which step failed

    # Pattern analysis
    cluster_id = Column(Integer, nullable=True)  # Log embedding cluster
    is_flaky = Column(Boolean, default=False)
    anomaly_flags = Column(JSON, default=list)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    repository = relationship("Repository", back_populates="ci_runs")
    pull_request = relationship("PullRequest", back_populates="ci_runs")
    incident = relationship("Incident", back_populates="ci_run", uselist=False)
