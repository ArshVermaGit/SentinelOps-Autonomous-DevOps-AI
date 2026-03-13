"""
Local Development Router - Multi-repo management endpoints.
Author: Arsh Verma
"""


from app.services.local_git_service import local_git
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class LinkRepoRequest(BaseModel):
    name: str
    local_path: str
    github_url: str = ""


class CommitRequest(BaseModel):
    local_path: str
    message: str


@router.get("/repos")
async def list_repos():
    """List all linked repos with their live status."""
    return {"repos": local_git.list_linked_repos()}


@router.post("/repos/link")
async def link_repo(req: LinkRepoRequest):
    """Link a GitHub repo to a local folder."""
    success = local_git.link_repo(req.name, req.local_path, req.github_url)
    if not success:
        raise HTTPException(
            status_code=400, detail="Invalid path — no .git directory found. Make sure the folder is a git repo."
        )
    return {"status": "linked", "name": req.name, "local_path": req.local_path}


@router.delete("/repos/unlink")
async def unlink_repo(local_path: str):
    """Remove a repo from the linked list."""
    local_git.unlink_repo(local_path)
    return {"status": "unlinked"}


@router.get("/repos/status")
async def get_repo_status(local_path: str):
    """Get full status for a specific linked repo."""
    status = local_git.get_repo_status(local_path)
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    return status


@router.post("/repos/commit")
async def commit_repo(req: CommitRequest):
    """Stage all, commit, and push for a specific repo."""
    result = local_git.commit_and_push(req.local_path, req.message)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Commit failed"))
    return result


# Keep backward compat for the dashboard LocalSandbox component
@router.get("/status")
async def get_legacy_status():
    """Legacy endpoint — returns status of the first linked repo or empty."""
    repos = local_git.list_linked_repos()
    if not repos:
        return {"has_changes": False, "risk": None}
    first = repos[0]
    status = local_git.get_repo_status(first["local_path"])
    has_changes = (
        len(status.get("changed_files", {}).get("staged", [])) > 0
        or len(status.get("changed_files", {}).get("modified", [])) > 0
    )
    return {
        "has_changes": has_changes,
        "diff_summary": {
            "files_count": len(status.get("changed_files", {}).get("staged", []))
            + len(status.get("changed_files", {}).get("modified", [])),
            "max_complexity": 0,
        },
        "risk": status.get("risk"),
    }


@router.post("/commit")
async def commit_legacy(req: CommitRequest):
    """Legacy endpoint — commit first linked repo."""
    result = local_git.commit_and_push(req.local_path, req.message)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Commit failed"))
    return result
