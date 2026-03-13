from typing import List

from pydantic import BaseModel


class RepoSummary(BaseModel):
    total: int
    high_risk: int
    avg_risk_score: float


class CISummary(BaseModel):
    total_runs_30d: int
    failed_runs_30d: int
    success_rate: float
    avg_build_time_ms: int


class IncidentSummary(BaseModel):
    open: int
    total_30d: int


class RepoListItem(BaseModel):
    id: int
    name: str
    risk_score: float
    failure_rate: float


class DashboardSummaryResponse(BaseModel):
    repos: RepoSummary
    ci: CISummary
    incidents: IncidentSummary
    repos_list: List[RepoListItem]


class CIHealthDataPoint(BaseModel):
    date: str
    success: int
    failure: int
    total: int
    avg_duration: int


class CIHealthResponse(BaseModel):
    data: List[CIHealthDataPoint]


class RiskHeatmapRepo(BaseModel):
    id: int
    name: str
    risk_score: float
    risk_level: str


class RiskHeatmapPR(BaseModel):
    id: int
    title: str
    author: str
    risk_probability: float
    risk_level: str
    risk_factors: List[str] = []


class RiskHeatmapResponse(BaseModel):
    repositories: List[RiskHeatmapRepo]
    pull_requests: List[RiskHeatmapPR]
