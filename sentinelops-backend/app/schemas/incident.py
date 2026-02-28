from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class IncidentBase(BaseModel):
    root_cause: Optional[str] = None
    error_category: Optional[str] = None

class IncidentResponse(IncidentBase):
    id: int
    ci_run_id: int
    responsible_files: List[str] = []
    llm_confidence: float = 0.0
    suggested_fix: Optional[str] = None
    fix_diff: Optional[str] = None
    estimated_fix_time: Optional[str] = None
    risk_if_unresolved: Optional[str] = None
    similar_incident_id: Optional[int] = None
    similarity_score: float = 0.0
    status: str = "open"
    simulation_result: Optional[dict] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SimulationStep(BaseModel):
    step: str
    status: str  # "success" | "failure" | "skipped" | "running"
    duration_ms: int

class SimulationResult(BaseModel):
    success: bool
    steps: List[SimulationStep]
    predicted_outcome: str
    confidence: str
    tests_passed: int
    tests_failed: int
