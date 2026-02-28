from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RepositoryBase(BaseModel):
    name: str
    full_name: str
    url: str

class RepositoryResponse(RepositoryBase):
    id: int
    github_id: int
    risk_score: float
    failure_rate: float
    avg_build_time_ms: int
    deployment_stability: float
    last_analyzed: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
