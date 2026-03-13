from datetime import datetime

from app.core.database import Base
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer


class LogEmbedding(Base):
    __tablename__ = "log_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    ci_run_id = Column(Integer, ForeignKey("ci_runs.id"), unique=True)
    embedding_vector = Column(JSON, nullable=False)  # Store as JSON array
    cluster_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
