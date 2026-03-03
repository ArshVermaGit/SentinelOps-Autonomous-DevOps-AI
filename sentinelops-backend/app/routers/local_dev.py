"""
Local Development Router - Endpoints for the Sandbox feature.
Author: Arsh Verma
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.local_git_service import local_git_service

router = APIRouter()

class CommitRequest(BaseModel):
    message: str

@router.get("/status")
async def get_local_status():
    """Returns the current staged risk profile."""
    return local_git_service.get_staged_status()

@router.post("/commit")
async def commit_local_changes(req: CommitRequest):
    """Triggers the git commit & push flow."""
    success = local_git_service.commit_and_push(req.message)
    if not success:
        raise HTTPException(status_code=500, detail="Git commit or push failed. Check your local state.")
    return {"status": "success", "message": "Changes pushed to GitHub!"}
