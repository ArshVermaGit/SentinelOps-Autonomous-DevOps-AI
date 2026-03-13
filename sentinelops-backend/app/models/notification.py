"""
SentinelOps Notification Model
Author: Arsh Verma
"""

from datetime import datetime

from app.core.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # "incident" | "ci_failure" | "pr_risk" | "system"
    severity = Column(String, default="info")  # "info" | "warning" | "critical"
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)

    # Optional link to related entity
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    ci_run_id = Column(Integer, ForeignKey("ci_runs.id"), nullable=True)
    pr_id = Column(Integer, ForeignKey("pull_requests.id"), nullable=True)

    # Status
    is_read = Column(String, default="unread")  # "unread" | "read" | "dismissed"
    created_at = Column(DateTime, default=datetime.utcnow)
