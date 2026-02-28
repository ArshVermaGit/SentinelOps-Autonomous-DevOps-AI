"""
Seed the database with realistic demo data for hackathon presentation.
Run: python scripts/seed_demo_data.py

Creates:
- 4 repositories
- 20 pull requests (mix of risk levels)
- 30 CI runs (mix of success/failure)
- 8 incidents with LLM analysis
- Log embeddings for similarity demo
"""
import asyncio
import random
from datetime import datetime, timedelta
from app.database import AsyncSessionLocal, create_tables
from app.models.repository import Repository
from app.models.pull_request import PullRequest
from app.models.ci_run import CIRun
from app.models.incident import Incident

REPOS = [
    {"name": "api-gateway", "full_name": "acme-corp/api-gateway", "risk_score": 0.72, "failure_rate": 0.24},
    {"name": "payment-service", "full_name": "acme-corp/payment-service", "risk_score": 0.58, "failure_rate": 0.18},
    {"name": "frontend-app", "full_name": "acme-corp/frontend-app", "risk_score": 0.31, "failure_rate": 0.09},
    {"name": "data-pipeline", "full_name": "acme-corp/data-pipeline", "risk_score": 0.85, "failure_rate": 0.33},
]

PRs = [
    {
        "title": "feat: Upgrade PostgreSQL driver to 15.x",
        "author": "alex.dev",
        "lines_added": 234, "lines_deleted": 89,
        "files_changed": 12,
        "has_dependency_changes": True,
        "has_config_changes": True,
        "has_test_changes": True,
        "risk_probability": 0.78,
        "risk_level": "high",
        "risk_factors": ["Dependency file changes detected", "Configuration files modified", "Large change: 323 lines"]
    },
    {
        "title": "fix: Memory leak in connection pool handler",
        "author": "sarah.eng",
        "lines_added": 45, "lines_deleted": 23,
        "files_changed": 3,
        "has_dependency_changes": False,
        "has_config_changes": False,
        "has_test_changes": True,
        "risk_probability": 0.22,
        "risk_level": "safe",
        "risk_factors": []
    },
    {
        "title": "refactor: Migrate auth to JWT with refresh tokens",
        "author": "mike.backend",
        "lines_added": 678, "lines_deleted": 412,
        "files_changed": 28,
        "has_dependency_changes": True,
        "has_config_changes": True,
        "has_test_changes": False,
        "risk_probability": 0.91,
        "risk_level": "high",
        "risk_factors": [
            "Large change: 1090 lines modified",
            "Dependency file changes detected",
            "No test coverage for changes",
            "Author has 31% historical failure rate"
        ]
    },
    {
        "title": "docs: Update API documentation",
        "author": "lisa.docs",
        "lines_added": 156, "lines_deleted": 45,
        "files_changed": 8,
        "has_dependency_changes": False,
        "has_config_changes": False,
        "has_test_changes": False,
        "risk_probability": 0.08,
        "risk_level": "safe",
        "risk_factors": []
    },
    {
        "title": "feat: Add rate limiting middleware (Redis)",
        "author": "alex.dev",
        "lines_added": 312, "lines_deleted": 0,
        "files_changed": 7,
        "has_dependency_changes": True,
        "has_config_changes": False,
        "has_test_changes": True,
        "risk_probability": 0.54,
        "risk_level": "caution",
        "risk_factors": ["New Redis dependency added", "No integration tests"]
    },
]

INCIDENTS = [
    {
        "root_cause": "The PostgreSQL driver upgrade introduced a breaking change in connection string format. The new v15.x driver requires `sslmode=require` explicitly, which was not set in the docker-compose environment variables.",
        "responsible_files": ["docker-compose.yml", "app/database.py", "alembic/env.py"],
        "error_category": "config",
        "llm_confidence": 0.94,
        "suggested_fix": "Add `sslmode=require` to the DATABASE_URL environment variable and update the connection pool configuration in app/database.py to use the new driver's connection parameters.",
        "fix_diff": '--- a/docker-compose.yml\n+++ b/docker-compose.yml\n@@ -15,7 +15,7 @@\n     environment:\n-      - DATABASE_URL=postgresql://user:pass@postgres:5432/db\n+      - DATABASE_URL=postgresql://user:pass@postgres:5432/db?sslmode=require\n',
        "estimated_fix_time": "5 minutes",
        "risk_if_unresolved": "All database connections will fail in staging and production",
        "similarity_score": 0.0,
    },
    {
        "root_cause": "JWT secret key is not being read from environment variables in the test environment. The test suite uses a hardcoded placeholder 'YOUR_SECRET_HERE' which is rejected by the new strict secret validation added in the auth migration.",
        "responsible_files": ["tests/conftest.py", "app/auth/config.py"],
        "error_category": "test",
        "llm_confidence": 0.87,
        "suggested_fix": "Update tests/conftest.py to load the JWT_SECRET from os.environ with a test-specific default value, and add the test secret to the CI environment variables.",
        "fix_diff": '--- a/tests/conftest.py\n+++ b/tests/conftest.py\n@@ -5,6 +5,7 @@\n import pytest\n+import os\n \n @pytest.fixture\n def app_settings():\n     return Settings(\n-        JWT_SECRET="YOUR_SECRET_HERE",\n+        JWT_SECRET=os.environ.get("TEST_JWT_SECRET", "test-secret-key-32-chars-minimum"),\n     )',
        "estimated_fix_time": "15 minutes",
        "risk_if_unresolved": "Auth tests will continue to fail, blocking all auth-related deployments",
        "similarity_score": 0.0,
    },
]

async def seed():
    await create_tables()
    
    async with AsyncSessionLocal() as db:
        # Clear existing data
        from sqlalchemy import delete
        for model in [Incident, CIRun, PullRequest, Repository]:
            await db.execute(delete(model))
        await db.commit()
        
        # Create repositories
        repo_objects = []
        for i, r in enumerate(REPOS):
            repo = Repository(
                github_id=10000 + i,
                name=r["name"],
                full_name=r["full_name"],
                url=f"https://github.com/{r['full_name']}",
                risk_score=r["risk_score"],
                failure_rate=r["failure_rate"],
                deployment_stability=1.0 - r["failure_rate"],
            )
            db.add(repo)
            repo_objects.append(repo)
        await db.flush()
        
        # Create pull requests
        pr_objects = []
        for i, pr_data in enumerate(PRs):
            repo = repo_objects[i % len(repo_objects)]
            pr = PullRequest(
                github_pr_number=100 + i,
                repo_id=repo.id,
                head_branch=f"feature/branch-{i}",
                **{k: v for k, v in pr_data.items()}
            )
            db.add(pr)
            pr_objects.append(pr)
        await db.flush()
        
        # Create CI runs (mix of success/failure)
        ci_run_objects = []
        base_time = datetime.utcnow() - timedelta(days=30)
        
        for day in range(30):
            runs_per_day = random.randint(3, 8)
            for run_num in range(runs_per_day):
                status = "failure" if random.random() < 0.18 else "success"
                duration = random.randint(45000, 300000)
                run_time = base_time + timedelta(days=day, hours=run_num * 3)
                
                ci_run = CIRun(
                    github_run_id=50000 + day * 10 + run_num,
                    repo_id=random.choice(repo_objects).id,
                    pr_id=random.choice(pr_objects).id if random.random() > 0.3 else None,
                    workflow_name=random.choice(["CI / Build & Test", "Deploy to Staging", "Security Scan"]),
                    status=status,
                    conclusion=status,
                    started_at=run_time,
                    finished_at=run_time + timedelta(milliseconds=duration),
                    duration_ms=duration,
                    is_anomalous_duration=duration > 240000,
                    error_block="Error: Cannot find module 'pg'\nRequire stack: app/database.js" if status == "failure" else None,
                    failure_step="Run tests" if status == "failure" else None,
                )
                db.add(ci_run)
                ci_run_objects.append(ci_run)
        
        await db.flush()
        
        # Create incidents for failed runs
        failed_runs = [r for r in ci_run_objects if r.status == "failure"][:len(INCIDENTS)]
        
        for i, (ci_run, inc_data) in enumerate(zip(failed_runs, INCIDENTS)):
            incident = Incident(
                ci_run_id=ci_run.id,
                **inc_data
            )
            db.add(incident)
        
        await db.commit()
        print("✅ Demo data seeded successfully!")
        print(f"   {len(REPOS)} repositories")
        print(f"   {len(PRs)} pull requests")
        print(f"   {len(ci_run_objects)} CI runs")
        print(f"   {len(INCIDENTS)} incidents with AI analysis")

if __name__ == "__main__":
    asyncio.run(seed())
