"""
SentinelOps Background Worker Tasks
Author: Arsh Verma
"""

import asyncio
import logging

from app.core.config import settings
from app.services.embedding_service import embed_log, find_similar_incidents
from app.services.github_service import GitHubService
from app.services.llm_service import analyze_failure
from app.services.risk_analyzer import RiskAnalyzer
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def analyze_pull_request_task(self, pr_id: int, repo_full_name: str):
    """Analyze a PR for risk when it's opened or updated."""
    try:
        asyncio.run(_analyze_pr(pr_id, repo_full_name))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(bind=True, max_retries=3)
def analyze_ci_run_task(self, run_id: int, repo_full_name: str):
    """Analyze completed CI run — trigger LLM if failure."""
    try:
        asyncio.run(_analyze_ci_run(run_id, repo_full_name))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


@celery_app.task
def run_periodic_repo_health_task():
    """Run every 5 minutes to update repo health metrics."""
    asyncio.run(_update_all_repo_health())


async def _analyze_pr(pr_id: int, repo_full_name: str):
    """Analyze a PR for risk using real diff data and author stats."""
    from app.core.database import AsyncSessionLocal
    from app.models.pull_request import PullRequest
    from app.utils.diff_parser import parse_unified_diff
    from sqlalchemy import select

    gh = GitHubService()
    analyzer = RiskAnalyzer()

    async with AsyncSessionLocal() as db:
        # Fetch PR metadata and diff from GitHub
        pr_data = await gh.get_pull_request(repo_full_name, pr_id)
        head_sha = pr_data["head"]["sha"]

        # 1. Set status to PENDING immediately
        await gh.create_commit_status(
            repo_full_name,
            head_sha,
            "pending",
            "SentinelOps is calculating merge risk...",
            target_url=f"{settings.FRONTEND_URL}/dashboard",
        )

        diff_text = await gh.get_pr_diff(repo_full_name, pr_id)
        author_stats = await gh.get_author_stats(repo_full_name, pr_data["user"]["login"])

        # Parse diff for advanced features
        diff_info = parse_unified_diff(diff_text)

        # Aggregate flags from all files in the diff
        has_config = any(f["is_config"] for f in diff_info["files"])
        has_dep = any(f["is_dep"] for f in diff_info["files"])
        has_test = any(f["is_test"] for f in diff_info["files"])

        # Analyze risk with real features
        result = analyzer.analyze_pr(
            {
                "lines_added": pr_data.get("additions", 0),
                "lines_deleted": pr_data.get("deletions", 0),
                "files_changed": pr_data.get("changed_files", 0),
                "has_config_changes": has_config,
                "has_dependency_changes": has_dep,
                "has_test_changes": has_test,
                "complexity_delta": diff_info["max_complexity_delta"],
            },
            author_stats,
        )

        # 2. Report FINAL status based on risk level
        state = "success" if result["risk_level"] != "high" else "failure"
        description = "Merge risk is low/moderate." if state == "success" else "High risk detected! Review analysis."

        await gh.create_commit_status(
            repo_full_name, head_sha, state, description, target_url=f"{settings.FRONTEND_URL}/dashboard"
        )

        # 3. Post humanized PR comment for transparency
        comment_body = gh.format_pr_risk_comment(result)
        await gh.create_pr_comment(repo_full_name, pr_id, comment_body)

        # Store or update PR in DB
        res = await db.execute(select(PullRequest).where(PullRequest.github_pr_number == pr_id))
        db_pr = res.scalar_one_or_none()

        if not db_pr:
            # Default to repo 1 for demo
            db_pr = PullRequest(github_pr_number=pr_id, repo_id=1)
            db.add(db_pr)

        db_pr.title = pr_data.get("title", "")
        db_pr.author = pr_data["user"]["login"]
        db_pr.head_branch = pr_data["head"]["ref"]
        db_pr.lines_added = pr_data.get("additions", 0)
        db_pr.lines_deleted = pr_data.get("deletions", 0)
        db_pr.files_changed = pr_data.get("changed_files", 0)
        db_pr.has_config_changes = has_config
        db_pr.has_dependency_changes = has_dep
        db_pr.has_test_changes = has_test
        db_pr.risk_probability = result["risk_probability"]
        db_pr.risk_level = result["risk_level"]
        db_pr.risk_factors = result["risk_factors"]

        await db.commit()


async def _analyze_ci_run(run_id: int, repo_full_name: str):
    from app.core.database import AsyncSessionLocal
    from app.models.ci_run import CIRun
    from app.models.incident import Incident
    from app.models.log_embedding import LogEmbedding
    from app.utils.log_parser import extract_error_block
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        # Fetch CI run metadata
        res = await db.execute(select(CIRun).where(CIRun.github_run_id == run_id))
        ci_run = res.scalar_one_or_none()

        if not ci_run or ci_run.status != "failure":
            return

        # Fetch log from GitHub
        gh = GitHubService()
        log_text = await gh.get_run_logs(repo_full_name, run_id)
        ci_run.log_text = log_text
        ci_run.error_block = extract_error_block(log_text)

        # Find similar incidents using vector search
        similar = await find_similar_incidents(db, log_text)

        # LLM analysis for root cause and fix suggestion
        diff = ""
        if ci_run.pr_id:
            diff = await gh.get_pr_diff(repo_full_name, ci_run.pr_id)

        analysis = await analyze_failure(ci_run.error_block, diff, similar)

        # Store incident
        incident = Incident(
            ci_run_id=ci_run.id,
            root_cause=analysis["root_cause"],
            responsible_files=analysis["responsible_files"],
            error_category=analysis["error_category"],
            llm_confidence=analysis["confidence"],
            suggested_fix=analysis["suggested_fix"],
            fix_diff=analysis["fix_diff"],
            estimated_fix_time=analysis["estimated_fix_time"],
            risk_if_unresolved=analysis["risk_if_unresolved"],
        )
        db.add(incident)

        # Store log embedding for future similarity searches
        embedding = LogEmbedding(ci_run_id=ci_run.id, embedding_vector=embed_log(log_text))
        db.add(embedding)

        await db.commit()

        # Broadcast to dashboard via WebSocket for real-time update
        from app.services.websocket_service import broadcast_new_incident

        await broadcast_new_incident(incident.id)


async def _update_all_repo_health():
    """Aggregate CI performance metrics across all repositories."""
    from app.core.database import AsyncSessionLocal
    from app.models.ci_run import CIRun
    from app.models.repository import Repository
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Repository))
        repos = result.scalars().all()

        for repo in repos:
            # Query recent CI runs for this repo
            runs_query = select(CIRun).where(CIRun.repo_id == repo.id).order_by(CIRun.created_at.desc()).limit(100)
            res = await db.execute(runs_query)
            runs = res.scalars().all()

            if not runs:
                continue

            # Calculate failure rate
            total = len(runs)
            failures = sum(1 for r in runs if r.status == "failure")
            repo.failure_rate = failures / total

            # Calculate avg build time
            durations = [r.duration_ms for r in runs if r.duration_ms]
            if durations:
                repo.avg_build_time_ms = int(sum(durations) / len(durations))

            # Composite risk score (simplified)
            repo.risk_score = min(1.0, (repo.failure_rate * 2.0) + (repo.avg_build_time_ms / 600000))
            repo.deployment_stability = 1.0 - repo.failure_rate

        await db.commit()
