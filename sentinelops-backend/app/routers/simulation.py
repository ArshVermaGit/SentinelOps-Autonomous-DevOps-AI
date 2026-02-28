from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
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
    
    # Simulation result based on LLM confidence
    success_probability = incident.llm_confidence if incident.llm_confidence else 0.75
    success = random.random() < success_probability
    
    simulation_result = {
        "success": success,
        "steps": [
            {"step": "Apply patch", "status": "success", "duration_ms": 234},
            {"step": "Install dependencies", "status": "success", "duration_ms": 4521},
            {"step": "Run unit tests", "status": "success" if success else "failure", "duration_ms": 12043},
            {"step": "Run integration tests", "status": "success" if success else "skipped", "duration_ms": 8932 if success else 0},
            {"step": "Build Docker image", "status": "success" if success else "skipped", "duration_ms": 23100 if success else 0},
        ],
        "predicted_outcome": "CI pipeline would PASS" if success else "CI pipeline would still FAIL — additional fix required",
        "confidence": f"{int(success_probability * 100)}%",
        "tests_passed": 47 if success else 31,
        "tests_failed": 0 if success else 16,
    }
    
    # Update incident status
    incident.status = "simulated"
    incident.simulation_result = simulation_result
    await db.commit()
    
    return simulation_result
