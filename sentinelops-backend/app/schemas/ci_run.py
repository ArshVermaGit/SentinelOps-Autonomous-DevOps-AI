from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CIRunBase(BaseModel):
    workflow_name: str
    status: str


class CIRunResponse(CIRunBase):
    id: int
    github_run_id: int
    repo_id: Optional[int] = None
    pr_id: Optional[int] = None
    conclusion: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_ms: int = 0
    is_anomalous_duration: bool = False
    error_block: Optional[str] = None
    failure_step: Optional[str] = None
    is_flaky: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
