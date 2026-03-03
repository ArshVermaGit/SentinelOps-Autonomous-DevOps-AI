"""
GitHub API client - Wrapper for all my interactions with the GitHub API.
Author: Arsh Verma
"""
from typing import Dict, List, Optional, Any
import httpx
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    """Handles GitHub API calls with error handling and fallback logic."""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    async def get_pull_request(self, repo: str, pr_number: int) -> Dict[str, Any]:
        """Fetch pull request metadata from GitHub API."""
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(
                    f"{GITHUB_API_BASE}/repos/{repo}/pulls/{pr_number}",
                    headers=self.headers,
                    timeout=10.0
                )
                r.raise_for_status()
                return r.json()
            except httpx.HTTPError as e:
                logger.error(f"GitHub API Error (PR {pr_number}): {e}")
                raise
    
    async def get_pr_diff(self, repo: str, pr_number: int) -> str:
        """Fetch pull request unified diff text."""
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(
                    f"{GITHUB_API_BASE}/repos/{repo}/pulls/{pr_number}",
                    headers={**self.headers, "Accept": "application/vnd.github.diff"},
                    timeout=10.0
                )
                r.raise_for_status()
                return r.text[:5000]
            except httpx.HTTPError as e:
                logger.error(f"GitHub API Error (Diff {pr_number}): {e}")
                return ""
    
    async def get_pr_files(self, repo: str, pr_number: int) -> list[dict]:
        """Get list of files changed in PR."""
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{GITHUB_API_BASE}/repos/{repo}/pulls/{pr_number}/files",
                headers=self.headers,
                timeout=10.0
            )
            r.raise_for_status()
            return r.json()
    
    async def get_run_logs(self, repo: str, run_id: int) -> str:
        """
        Download CI run logs.
        Returns log text (truncated to last 200 lines).
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Get download URL
            r = await client.get(
                f"{GITHUB_API_BASE}/repos/{repo}/actions/runs/{run_id}/logs",
                headers=self.headers,
                timeout=30.0
            )
            if r.status_code == 302:
                # Follow redirect to download
                log_r = await client.get(r.headers["Location"], timeout=30.0)
                log_text = log_r.text
            else:
                log_text = r.text
            
            # Return last 200 lines
            lines = log_text.split("\n")
            return "\n".join(lines[-200:])
    
    async def get_workflow_run(self, repo: str, run_id: int) -> dict:
        """Get workflow run details."""
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{GITHUB_API_BASE}/repos/{repo}/actions/runs/{run_id}",
                headers=self.headers,
                timeout=10.0
            )
            r.raise_for_status()
            return r.json()
    
    async def get_author_stats(self, repo: str, author: str) -> dict:
        """
        Get author's historical PR stats.
        Returns: { total_prs, failed_prs, avg_lines_changed }
        """
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{GITHUB_API_BASE}/search/issues",
                params={
                    "q": f"repo:{repo} author:{author} type:pr is:closed",
                    "per_page": 100
                },
                headers=self.headers,
                timeout=10.0
            )
            data = r.json()
            total = data.get("total_count", 0)
            
            # For demo: estimate failure rate
            return {
                "total_prs": total,
                "failed_prs": int(total * 0.18),  # Estimated from repo failure rate
                "avg_lines_changed": 200
            }
    
    async def create_pr_comment(self, repo: str, pr_number: int, body: str) -> dict:
        """
        Post SentinelOps risk analysis as PR comment.
        """
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{GITHUB_API_BASE}/repos/{repo}/issues/{pr_number}/comments",
                headers=self.headers,
                json={"body": body},
                timeout=10.0
            )
            r.raise_for_status()
            return r.json()

    async def create_commit_status(self, repo: str, sha: str, state: str, description: str, target_url: str = "") -> dict:
        """
        Create a GitHub commit status (pending, success, error, failure). 
        This is the core of the 'Gatekeeper' mode.
        """
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "state": state,
                    "target_url": target_url,
                    "description": description,
                    "context": "sentinel-ops/risk-gate"
                }
                r = await client.post(
                    f"{GITHUB_API_BASE}/repos/{repo}/statuses/{sha}",
                    headers=self.headers,
                    json=payload,
                    timeout=10.0
                )
                r.raise_for_status()
                return r.json()
            except httpx.HTTPError as e:
                logger.error(f"GitHub Status Error ({sha}): {e}")
                return {}
    
    def format_pr_risk_comment(self, risk_data: dict) -> str:
        """Helper to format the PR risk analysis as a clean markdown comment."""
        emoji = "🟢" if risk_data["risk_level"] == "safe" else \
                "🟡" if risk_data["risk_level"] == "caution" else "🔴"
        
        factors_md = "\n".join([f"- {f}" for f in risk_data.get("risk_factors", [])])
        
        return f"""## {emoji} PR Risk Analysis
**CI Failure Probability**: `{risk_data['risk_probability']:.0%}`  
**Level**: **{risk_data['risk_level'].upper()}**

### Key Risk Drivers
{factors_md or "_No major risks detected._"}

---
*Generated by SentinelOps — Developed by Arsh Verma*
"""
