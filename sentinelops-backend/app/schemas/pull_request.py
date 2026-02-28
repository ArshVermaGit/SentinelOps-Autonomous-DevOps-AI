from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PullRequestBase(BaseModel):
    title: str
    author: str
    head_branch: str

class PullRequestResponse(PullRequestBase):
    id: int
    github_pr_number: int
    repo_id: Optional[int] = None
    base_branch: str = "main"
    lines_added: int = 0
    lines_deleted: int = 0
    files_changed: int = 0
    file_types: List[str] = []
    has_config_changes: bool = False
    has_test_changes: bool = False
    has_dependency_changes: bool = False
    risk_probability: float = 0.0
    risk_level: str = "unknown"
    risk_factors: List[str] = []
    status: str = "open"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PRRiskAnalysisRequest(BaseModel):
    title: str
    lines_added: int = 0
    lines_deleted: int = 0
    files_changed: int = 1
    has_config_changes: bool = False
    has_test_changes: bool = True
    has_dependency_changes: bool = False
    author_failure_rate: float = 0.15
    complexity_delta: float = 0.0

class PRRiskAnalysisResponse(BaseModel):
    risk_probability: float
    risk_level: str
    risk_factors: List[str]
    ml_score: float
    rule_score: float
    component_scores: dict
