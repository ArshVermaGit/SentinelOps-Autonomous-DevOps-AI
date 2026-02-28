"""
Manual analysis trigger endpoints — for demo button clicks.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.services.risk_analyzer import RiskAnalyzer
from app.services.ml_predictor import predict_failure_probability, normalize_pr_features
from app.services.llm_service import analyze_failure, analyze_failure_mock
from app.config import settings

router = APIRouter()
risk_analyzer = RiskAnalyzer()

class PRAnalysisRequest(BaseModel):
    title: str
    lines_added: int = 0
    lines_deleted: int = 0
    files_changed: int = 1
    has_config_changes: bool = False
    has_test_changes: bool = True
    has_dependency_changes: bool = False
    author_failure_rate: float = 0.15
    pr_age_hours: float = 24
    complexity_delta: float = 0.0

@router.post("/analyze-pr")
async def analyze_pr_manual(req: PRAnalysisRequest):
    """
    Manually trigger PR risk analysis.
    Used for demo mode — input a PR's details and get risk score back.
    """
    # pr_data automatically includes complexity_delta from the Pydantic model
    pr_data = req.dict()
    
    # Rule-based risk analysis
    rule_result = risk_analyzer.analyze_pr(pr_data, {
        "total_prs": 50,
        "failed_prs": int(req.author_failure_rate * 50),
        "avg_lines_changed": 200
    })
    
    # ML model prediction
    normalized = normalize_pr_features(pr_data)
    ml_probability = predict_failure_probability(normalized)
    
    # Blend: 60% ML, 40% rule-based
    final_probability = 0.6 * ml_probability + 0.4 * rule_result["risk_probability"]
    
    risk_level = "safe" if final_probability < 0.35 else "caution" if final_probability < 0.65 else "high"
    
    return {
        "risk_probability": round(final_probability, 3),
        "risk_level": risk_level,
        "risk_factors": rule_result["risk_factors"],
        "ml_score": ml_probability,
        "rule_score": rule_result["risk_probability"],
        "component_scores": rule_result["component_scores"]
    }

class LogAnalysisRequest(BaseModel):
    log_text: str
    code_diff: str = ""

@router.post("/analyze-log")
async def analyze_log_manual(req: LogAnalysisRequest):
    """
    Manually trigger LLM root cause analysis on a log snippet.
    Demo endpoint — paste any log and get AI analysis.
    """
    if len(req.log_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Log text too short")
    
    try:
        result = await analyze_failure(req.log_text, req.code_diff, [])
    except Exception:
        # Fallback to mock for demo if API key not configured
        result = await analyze_failure_mock(req.log_text)
    
    return result
