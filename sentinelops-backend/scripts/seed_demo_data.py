"""
Seed the database with realistic demo data for hackathon presentation.
Author: Arsh Verma
Run: python3 scripts/seed_demo_data.py

Creates:
- 4 repositories
- 20 pull requests (mix of risk levels)
- 150+ CI runs (mix of success/failure)
- 8 incidents with LLM analysis
- Log embeddings for similarity demo
- Notifications for recent events
- Incident timeline events
"""
import asyncio
import random
import numpy as np
from datetime import datetime, timedelta
from app.database import AsyncSessionLocal, create_tables
from app.models.repository import Repository
from app.models.pull_request import PullRequest
from app.models.ci_run import CIRun
from app.models.incident import Incident
from app.models.log_embedding import LogEmbedding
from app.models.notification import Notification
from app.models.incident_event import IncidentEvent

REPOS = [
    {"name": "api-gateway", "full_name": "acme-corp/api-gateway", "risk_score": 0.72, "failure_rate": 0.24},
    {"name": "payment-service", "full_name": "acme-corp/payment-service", "risk_score": 0.58, "failure_rate": 0.18},
    {"name": "frontend-app", "full_name": "acme-corp/frontend-app", "risk_score": 0.31, "failure_rate": 0.09},
    {"name": "data-pipeline", "full_name": "acme-corp/data-pipeline", "risk_score": 0.85, "failure_rate": 0.33},
]

PR_TEMPLATES = [
    {
        "title": "feat: Upgrade PostgreSQL driver to 15.x",
        "author": "arsh.verma",
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
        "author": "arsh.verma",
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

INCIDENTS_DATA = [
    {
        "root_cause": "The PostgreSQL driver upgrade introduced a breaking change in connection string format. The new v15.x driver requires `sslmode=require` explicitly, which was not set in the docker-compose environment variables.",
        "responsible_files": ["docker compose.yml", "app/database.py", "alembic/env.py"],
        "error_category": "config",
        "llm_confidence": 0.94,
        "suggested_fix": "Add `sslmode=require` to the DATABASE_URL environment variable and update the connection pool configuration in app/database.py to use the new driver's connection parameters.",
        "fix_diff": '--- a/docker compose.yml\n+++ b/docker compose.yml\n@@ -15,7 +15,7 @@\n     environment:\n-      - DATABASE_URL=postgresql://user:pass@postgres:5432/db\n+      - DATABASE_URL=postgresql://user:pass@postgres:5432/db?sslmode=require\n',
        "estimated_fix_time": "5 minutes",
        "risk_if_unresolved": "All database connections will fail in staging and production",
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
    },
    {
        "root_cause": "Redis connection timeout due to DNS resolution failure in the data-pipeline environment. The new rate-limiter service is trying to connect to 'redis-master.internal' which is not mapped in the internal k8s DNS for the data-pipeline namespace.",
        "responsible_files": ["infra/k8s/data-pipeline/deployment.yaml"],
        "error_category": "infra",
        "llm_confidence": 0.91,
        "suggested_fix": "Update the Redis host to Use the fully qualified service name 'redis-master.shared-services.svc.cluster.local' in the data-pipeline deployment configuration.",
        "fix_diff": "--- a/infra/k8s/data-pipeline/deployment.yaml\n+++ b/infra/k8s/data-pipeline/deployment.yaml\n@@ -42,1 +42,1 @@\n- REDIS_HOST: 'redis-master.internal'\n+ REDIS_HOST: 'redis-master.shared-services.svc.cluster.local'",
        "estimated_fix_time": "10 minutes",
        "risk_if_unresolved": "Data pipeline will stay stalled due to rate-limit check failures",
    },
    {
        "root_cause": "Circular dependency introduced between 'auth-service' and 'api-gateway' after the latest JWT migration. The auth-service now depends on the gateway for health checks, while the gateway depends on auth for request validation.",
        "responsible_files": ["services/auth/main.py", "services/gateway/middleware.py"],
        "error_category": "logic",
        "llm_confidence": 0.82,
        "suggested_fix": "Remove the gateway health check dependency from the auth service and implement a direct database health check instead.",
        "fix_diff": "--- a/services/auth/main.py\n+++ b/services/auth/main.py\n@@ -12,1 +12,1 @@\n- HEALTH_CHECK_URL = 'http://api-gateway/health'\n+ HEALTH_CHECK_URL = 'http://localhost:8000/db-health'",
        "estimated_fix_time": "30 minutes",
        "risk_if_unresolved": "Intermittent service crashes during high load as services wait for each other",
    },
    {
        "root_cause": "Missing environment variable 'STRIPE_WEBHOOK_SECRET' in the payment-service production environment after the v2.4.1 deployment. Stripe events are being rejected with 401 Unauthorized.",
        "responsible_files": ["app/services/payment/stripe_client.py"],
        "error_category": "config",
        "llm_confidence": 0.98,
        "suggested_fix": "Add the 'STRIPE_WEBHOOK_SECRET' to the payment-service secrets in the CI/CD pipeline and re-deploy.",
        "fix_diff": "--- a/app/services/payment/stripe_client.py\n+++ b/app/services/payment/stripe_client.py\n@@ -5,1 +5,1 @@\n- secret = os.getenv('STRIPE_SECRET')\n+ secret = os.getenv('STRIPE_WEBHOOK_SECRET')",
        "estimated_fix_time": "2 minutes",
        "risk_if_unresolved": "Payments will not be processed, leading to customer churn",
    },
    {
        "root_cause": "OutOfMemory error in frontent-app build step. The new image processing library 'sharp' consumes more memory than allocated in the GitHub Actions runner (2GB limit reached).",
        "responsible_files": ["package.json", ".github/workflows/ci.yml"],
        "error_category": "infra",
        "llm_confidence": 0.89,
        "suggested_fix": "Increase the memory limit for the Node process in the CI workflow by setting NODE_OPTIONS='--max-old-space-size=4096'.",
        "fix_diff": "--- a/.github/workflows/ci.yml\n+++ b/.github/workflows/ci.yml\n@@ -25,1 +25,2 @@\n-      run: npm run build\n+      env:\n+        NODE_OPTIONS: '--max-old-space-size=4096'\n+      run: npm run build",
        "estimated_fix_time": "5 minutes",
        "risk_if_unresolved": "Frontend deployments are blocked",
    },
    {
        "root_cause": "Database migration failure: column 'user_preference' already exists in table 'users'. This happened because a manual hotfix was applied to production without updating the Alembic history.",
        "responsible_files": ["alembic/versions/3a2b1c_add_user_pref.py"],
        "error_category": "config",
        "llm_confidence": 0.95,
        "suggested_fix": "Modify the Alembic migration to use 'if_not_exists' logic or skip the column creation if it's already present.",
        "fix_diff": "--- a/alembic/versions/3a2b1c_add_user_pref.py\n+++ b/alembic/versions/3a2b1c_add_user_pref.py\n@@ -10,1 +10,1 @@\n-    op.add_column('users', sa.Column('user_preference', sa.JSON()))\n+    # skip as already exists in prod",
        "estimated_fix_time": "10 minutes",
        "risk_if_unresolved": "CI pipeline blocked at migration step",
    },
    {
        "root_cause": "Unexpected NullPointerException in api-gateway request logger. The logger assumes the 'X-Request-ID' header is always present, but some legacy clients have started bypassing the first-stage proxy.",
        "responsible_files": ["app/middleware/logger.py"],
        "error_category": "logic",
        "llm_confidence": 0.85,
        "suggested_fix": "Add a null-check and default value for the request ID header in the logging middleware.",
        "fix_diff": "--- a/app/middleware/logger.py\n+++ b/app/middleware/logger.py\n@@ -8,1 +8,1 @@\n- rid = request.headers['X-Request-ID']\n+ rid = request.headers.get('X-Request-ID', 'gen-' + str(uuid.uuid4()))",
        "estimated_fix_time": "15 minutes",
        "risk_if_unresolved": "Intermittent 500 errors for legacy clients",
    },
]

async def seed():
    await create_tables()
    
    async with AsyncSessionLocal() as db:
        # Clear existing data
        from sqlalchemy import delete
        for model in [IncidentEvent, Notification, LogEmbedding, Incident, CIRun, PullRequest, Repository]:
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
        for i in range(20):
            repo = repo_objects[i % len(repo_objects)]
            template = PR_TEMPLATES[i % len(PR_TEMPLATES)]
            pr = PullRequest(
                github_pr_number=100 + i,
                repo_id=repo.id,
                head_branch=f"feature/branch-{i}",
                title=f"{template['title']} #{i}",
                author=template['author'],
                lines_added=template['lines_added'],
                lines_deleted=template['lines_deleted'],
                files_changed=template['files_changed'],
                has_dependency_changes=template['has_dependency_changes'],
                has_config_changes=template['has_config_changes'],
                has_test_changes=template['has_test_changes'],
                risk_probability=template['risk_probability'],
                risk_level=template['risk_level'],
                risk_factors=template['risk_factors']
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
        failed_runs = [r for r in ci_run_objects if r.status == "failure"]
        random.shuffle(failed_runs)
        
        incident_objects = []
        for i, inc_data in enumerate(INCIDENTS_DATA):
            if i >= len(failed_runs): break
            ci_run = failed_runs[i]
            incident = Incident(
                ci_run_id=ci_run.id,
                **inc_data
            )
            # Add similarity links between some incidents
            if i >= 2 and random.random() > 0.5:
                incident.similar_incident_id = incident_objects[random.randint(0, len(incident_objects) - 1)].id if incident_objects else None
                incident.similarity_score = round(random.uniform(0.72, 0.96), 2)
            db.add(incident)
            await db.flush()
            incident_objects.append(incident)
            
            # Create random embedding for each incident
            # Using 384-dimensional vector (typical for all-MiniLM-L6-v2)
            embedding_vector = np.random.normal(0, 0.1, 384).tolist()
            log_emb = LogEmbedding(
                ci_run_id=ci_run.id,
                embedding_vector=embedding_vector,
                cluster_id=random.randint(1, 5)
            )
            db.add(log_emb)

        await db.flush()

        # Create incident timeline events for each incident
        event_templates = [
            ("created", "Incident detected", "CI failure detected and logged by monitoring system.", "system"),
            ("analyzed", "AI root cause analysis complete", "LLM analyzed the failure log and identified the root cause.", "ai"),
            ("similar_found", "Similar incident found", "Embedding similarity search matched a historical incident.", "ai"),
            ("fix_suggested", "Fix suggestion generated", "AI generated a patch diff to resolve the issue.", "ai"),
        ]

        for inc in incident_objects:
            evt_time = inc.created_at or datetime.utcnow()
            for j, (etype, title, desc, actor) in enumerate(event_templates):
                event = IncidentEvent(
                    incident_id=inc.id,
                    event_type=etype,
                    title=title,
                    description=desc,
                    actor=actor,
                    created_at=evt_time + timedelta(minutes=j * 2),
                )
                db.add(event)

        # Create notifications for recent events
        notif_templates = [
            ("incident", "critical", "New CI Failure Detected", "CI pipeline failed in api-gateway — AI analysis started."),
            ("pr_risk", "warning", "High-Risk PR Opened", "PR #103 'Migrate auth to JWT' scored 91% failure risk."),
            ("ci_failure", "critical", "Build Failure", "CI Build & Test failed in data-pipeline after 4m 32s."),
            ("incident", "info", "Incident Auto-Resolved", "Incident #5 was auto-analyzed — fix estimated at 2 minutes."),
            ("system", "info", "ML Model Retrained", "CI failure prediction model retrained with 200 new data points."),
            ("pr_risk", "warning", "Dependency Change Detected", "PR #100 modifies package.json and requirements.txt."),
            ("ci_failure", "critical", "Security Scan Failed", "Security scan found 2 critical vulnerabilities in payment-service."),
            ("incident", "info", "Similar Incident Found", "New failure in api-gateway is 94% similar to Incident #1."),
        ]

        for i, (ntype, severity, title, message) in enumerate(notif_templates):
            notif = Notification(
                type=ntype,
                severity=severity,
                title=title,
                message=message,
                incident_id=incident_objects[i % len(incident_objects)].id if incident_objects else None,
                is_read="unread" if i < 4 else "read",
                created_at=datetime.utcnow() - timedelta(hours=i * 2),
            )
            db.add(notif)

        await db.commit()
        print("✅ Demo data seeded successfully!")
        print(f"   {len(REPOS)} repositories")
        print(f"   {len(pr_objects)} pull requests")
        print(f"   {len(ci_run_objects)} CI runs")
        print(f"   {len(incident_objects)} incidents with AI analysis and log embeddings")
        print(f"   {len(incident_objects) * len(event_templates)} incident timeline events")
        print(f"   {len(notif_templates)} notifications")

if __name__ == "__main__":
    asyncio.run(seed())
