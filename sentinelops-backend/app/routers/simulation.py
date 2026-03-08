from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.incident import Incident
from sqlalchemy import select
import asyncio
import random

router = APIRouter()

@router.post("/{incident_id}/apply-fix")
async def simulate_fix(incident_id: int, db: AsyncSession = Depends(get_db)):
    """
    Simulate applying the AI-suggested fix.
    Runs a mock test suite and returns predicted outcome.
    """
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    if not incident.suggested_fix:
        raise HTTPException(status_code=400, detail="No fix available for this incident")
    
    # Simulate processing time (makes demo feel real)
    await asyncio.sleep(2)
    
    # Simulation result based on LLM confidence (deterministic seed)
    random.seed(incident_id) # Ensure same incident always gives same simulation result
    
    success_probability = incident.llm_confidence if incident.llm_confidence else 0.75
    success = random.random() < success_probability
    
    # Dynamic Step Generation based on Incident Data
    steps = [
        {"step": f"Apply generated patch to {len(incident.responsible_files)} files", "status": "success", "duration_ms": 350},
        {"step": "Install repository dependencies", "status": "success", "duration_ms": 4200}
    ]
    
    # Determine test suites dynamically
    workflow = incident.ci_run.workflow_name.lower() if incident.ci_run else "default"
    if "ui" in workflow or "frontend" in workflow:
        test_steps = [("Run component tests", 8000), ("Run e2e (Cypress)", 15000)]
    elif "api" in workflow or "backend" in workflow:
        test_steps = [("Run unit tests (pytest)", 5000), ("Run integration DB tests", 12000)]
    else:
        test_steps = [("Run standard test suite", 10000)]
        
    for name, base_duration in test_steps:
        # If failure is predicted, fail on the last test step
        is_last_test = name == test_steps[-1][0]
        if not success and is_last_test:
            steps.append({"step": name, "status": "failure", "duration_ms": base_duration})
            break
        steps.append({"step": name, "status": "success", "duration_ms": base_duration})
        
    if success:
        steps.append({"step": "Build verified Docker image", "status": "success", "duration_ms": 18000})
        
    simulation_result = {
        "success": success,
        "steps": steps,
        "predicted_outcome": "CI pipeline would PASS" if success else "CI pipeline would still FAIL — additional fix required",
        "confidence": f"{int(success_probability * 100)}%",
        "tests_passed": 142 if success else 24, # Deterministic based on outcome
        "tests_failed": 0 if success else 3,
        "is_mock": True # Flag for UI transparency
    }
    
    # Update incident status
    incident.status = "simulated"
    incident.simulation_result = simulation_result
    await db.commit()
    
    return simulation_result
