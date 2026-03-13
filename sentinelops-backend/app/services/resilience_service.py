"""
System Resilience Engine - Calculates the 'Pulse' of the infra.
Author: Arsh Verma
"""

from datetime import datetime, timedelta
from typing import Any, Dict

from app.models.ci_run import CIRun
from app.models.incident import Incident
from app.models.pull_request import PullRequest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ResilienceEngine:
    async def calculate_pulse(self, db: AsyncSession) -> Dict[str, Any]:
        """
        The main calculation for the aggregate pulse score.
        Formula: 0.4 * Stability + 0.3 * Recovery + 0.3 * RiskControl
        """
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        # 1. Stability (CI Success Rate)
        runs_query = await db.execute(select(CIRun).where(CIRun.started_at >= thirty_days_ago))
        runs = runs_query.scalars().all()
        total_runs = len(runs)
        success_runs = sum(1 for r in runs if r.status == "success")
        stability_score = (success_runs / total_runs * 100) if total_runs > 0 else 100

        # 2. Recovery (MTTR)
        # Simplified MTTR score: Higher if more resolved, lower if many open high-severity
        open_query = await db.execute(select(Incident).where(Incident.status == "open"))
        open_incidents = len(open_query.scalars().all())
        recovery_score = max(0, 100 - (open_incidents * 15))  # Penalty for open incidents

        # 3. Risk Control (PR Risk Velocity)
        pr_query = await db.execute(select(PullRequest).where(PullRequest.status == "open"))
        open_prs = pr_query.scalars().all()
        high_risk_prs = sum(1 for pr in open_prs if pr.risk_level == "high")
        risk_score = max(0, 100 - (high_risk_prs * 20))  # Penalty for unaddressed high risk

        aggregate = (stability_score * 0.4) + (recovery_score * 0.3) + (risk_score * 0.3)

        return {
            "pulse_score": round(aggregate, 1),
            "status": "EXCELLENT" if aggregate > 85 else "STABLE" if aggregate > 65 else "CRITICAL",
            "metrics": {
                "stability": round(stability_score, 1),
                "recovery": round(recovery_score, 1),
                "risk_control": round(risk_score, 1),
            },
            "last_updated": datetime.utcnow().isoformat(),
        }


resilience_engine = ResilienceEngine()
