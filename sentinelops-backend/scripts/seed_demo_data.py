"""
SentinelOps Demo Data Seeder
Author: Arsh Verma
Populates the database with realistic data for a perfect dashboard experience.
"""

import asyncio
import os
import random
import sys
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# sys.path manipulation must happen before app imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings  # noqa: E402
from app.database import Base  # noqa: E402
from app.models.ci_run import CIRun  # noqa: E402
from app.models.incident import Incident  # noqa: E402
from app.models.log_embedding import LogEmbedding  # noqa: E402
from app.models.pull_request import PullRequest  # noqa: E402
from app.models.repository import Repository  # noqa: E402
from app.services.embedding_service import embed_log  # noqa: E402


async def seed():
    # Use the async driver directly if it's already aiosqlite
    db_url = settings.DATABASE_URL
    if "sqlite" in db_url and "aiosqlite" not in db_url:
        db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://")

    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        print("🌱 Seeding Repositories...")
        repos = [
            Repository(
                name="sentinel-core",
                full_name="ArshVermaGit/sentinel-core",
                url="https://github.com/ArshVermaGit/sentinel-core",
                github_id=9001,
                risk_score=0.42,
                failure_rate=0.15,
            ),
            Repository(
                name="api-gateway",
                full_name="ArshVermaGit/api-gateway",
                url="https://github.com/ArshVermaGit/api-gateway",
                github_id=9002,
                risk_score=0.78,
                failure_rate=0.28,
            ),
            Repository(
                name="data-pipeline",
                full_name="ArshVermaGit/data-pipeline",
                url="https://github.com/ArshVermaGit/data-pipeline",
                github_id=9003,
                risk_score=0.85,
                failure_rate=0.35,
            ),
            Repository(
                name="frontend-app",
                full_name="ArshVermaGit/frontend-app",
                url="https://github.com/ArshVermaGit/frontend-app",
                github_id=9004,
                risk_score=0.25,
                failure_rate=0.08,
            ),
        ]
        db.add_all(repos)
        await db.commit()

        print("🌱 Seeding Pull Requests...")
        pr_titles = [
            "feat: add distributed tracing",
            "fix: memory leak in worker",
            "refactor: optimize db queries",
            "docs: update api spec",
            "chore: upgrade dependencies",
            "feat: implement mfa support",
        ]
        authors = ["arshverma", "dev-wizard", "infra-expert", "code-ninja"]

        for repo in repos:
            for i in range(3):
                pr = PullRequest(
                    repo_id=repo.id,
                    github_pr_number=100 + i,
                    title=random.choice(pr_titles),
                    author=random.choice(authors),
                    head_branch=f"feature/demo-{i}",
                    status="open",
                    risk_level=(
                        "high"
                        if random.random() > 0.7
                        else "caution" if random.random() > 0.4 else "safe"
                    ),
                    risk_probability=random.uniform(0.1, 0.9),
                    risk_factors=(
                        ["Large diff", "Complex logic"]
                        if random.random() > 0.5
                        else ["Author history"]
                    ),
                    created_at=(
                        datetime.utcnow() - timedelta(days=random.randint(1, 5))
                    ),
                )
                db.add(pr)
        await db.commit()

        print("🌱 Seeding CI Runs (30 days of data)...")
        now = datetime.utcnow()
        for day in range(30):
            date = now - timedelta(days=day)
            for _ in range(random.randint(3, 8)):
                status = "success" if random.random() > 0.2 else "failure"
                run = CIRun(
                    repo_id=random.choice(repos).id,
                    github_run_id=random.randint(1000000, 9999999),
                    workflow_name="CI Pipeline",
                    status=status,
                    duration_ms=random.randint(120000, 480000),
                    started_at=date - timedelta(hours=random.randint(0, 23)),
                )
                db.add(run)
        await db.commit()

        print("🌱 Seeding Incidents & Log Embeddings...")
        causes = [
            "Flaky network during npm install",
            "Database lock contention during migrations",
            "Missing environment variable",
            "Race condition in async worker",
        ]

        for i in range(5):
            inc = Incident(
                ci_run_id=i + 1,  # Use sequential IDs for simplicity in demo
                status="resolved" if random.random() > 0.3 else "open",
                error_category=random.choice(
                    ["dependency", "syntax", "test", "config", "net", "runtime"]
                ),
                root_cause=random.choice(causes),
                suggested_fix="Check resource limits or increase timeout.",
                created_at=(datetime.utcnow() - timedelta(days=random.randint(1, 10))),
            )
            db.add(inc)
            await db.flush()  # Get ID

            # Add embedding for similarity search demo
            log_text = f"ERROR: {inc.root_cause} at {datetime.utcnow()}"
            vector = embed_log(log_text)
            emb = LogEmbedding(ci_run_id=inc.ci_run_id, embedding_vector=vector)
            db.add(emb)

        await db.commit()
        print("✅ Demo data seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
