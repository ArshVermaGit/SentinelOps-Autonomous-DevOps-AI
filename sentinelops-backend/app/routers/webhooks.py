"""
SentinelOps GitHub Webhook Router
Author: Arsh Verma
"""
from fastapi import APIRouter, Request, Header, HTTPException
import hmac
import hashlib
from app.core.config import settings
from app.workers.tasks import analyze_pull_request_task, analyze_ci_run_task

router = APIRouter()

def verify_github_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature."""
    expected = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

@router.post("/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    payload = await request.body()
    
    # Verify signature (skip in dev mode)
    if not settings.DEBUG:
        if not verify_github_signature(payload, x_hub_signature_256 or ""):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    data = await request.json()
    repo_full_name = data.get("repository", {}).get("full_name", "")
    
    if x_github_event == "pull_request":
        action = data.get("action")
        if action in ["opened", "synchronize", "reopened"]:
            pr_number = data["pull_request"]["number"]
            analyze_pull_request_task.delay(pr_number, repo_full_name)
    
    elif x_github_event == "workflow_run":
        action = data.get("action")
        if action == "completed":
            run_id = data["workflow_run"]["id"]
            analyze_ci_run_task.delay(run_id, repo_full_name)
    
    return {"status": "accepted"}
