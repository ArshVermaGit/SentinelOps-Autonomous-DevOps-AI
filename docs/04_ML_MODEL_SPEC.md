# SentinelOps — ML Model Specification

## Overview

SentinelOps uses a **Logistic Regression classifier** to predict CI failure probability per pull request. The model is intentionally simple — the value is in the **feature engineering** and **system integration**, not model complexity.

---

## Feature Engineering

### Input Features (10 features)

| Feature | Type | Description |
|---------|------|-------------|
| `lines_changed` | float (normalized) | Total lines added + deleted, normalized 0-1 |
| `num_files_changed` | float (normalized) | Number of files changed, normalized 0-1 |
| `has_config_changes` | int (0/1) | Any .yaml, .json, .toml, .env file changed |
| `has_test_changes` | int (0/1) | Any test file changed (negative risk indicator) |
| `author_failure_rate` | float | Author's historical CI failure rate (0.0-1.0) |
| `pr_age_hours` | float (normalized) | How old the PR is when merged |
| `is_large_pr` | int (0/1) | 1 if lines_changed > 500 |
| `dependency_changes` | int (0/1) | package.json, requirements.txt, go.mod changed |
| `complexity_score` | float | Code complexity delta (approximated) |
| `time_since_last_deploy` | float (normalized) | Hours since last successful deploy |

### Target Variable
- `ci_failed`: 0 = success, 1 = failure

---

## app/ml/synthetic_data.py

```python
"""
Generate synthetic training data for the CI failure predictor.
500 realistic PRs with outcomes based on engineered rules + noise.
"""
import numpy as np
import pandas as pd
import json
from pathlib import Path

np.random.seed(42)
N = 500

def generate_training_data(n: int = N) -> pd.DataFrame:
    """Generate realistic synthetic PR data with CI outcomes."""
    
    data = []
    
    for i in range(n):
        # Generate raw features
        lines_changed = np.random.exponential(scale=200)  # Most PRs are small
        lines_changed = min(lines_changed, 2000)
        
        num_files = max(1, int(np.random.exponential(scale=5)))
        num_files = min(num_files, 50)
        
        has_config = np.random.choice([0, 1], p=[0.75, 0.25])
        has_tests = np.random.choice([0, 1], p=[0.40, 0.60])  # Most PRs have tests
        author_failure_rate = np.random.beta(2, 5)  # Right-skewed: most authors reliable
        pr_age_hours = np.random.exponential(scale=24)
        is_large = 1 if lines_changed > 500 else 0
        has_deps = np.random.choice([0, 1], p=[0.70, 0.30])
        complexity_score = np.random.uniform(0, 1)
        time_since_deploy = np.random.exponential(scale=48)
        
        # Calculate base failure probability from domain rules
        base_p = (
            0.15 +  # baseline failure rate
            (lines_changed / 2000) * 0.30 +          # large changes = more risk
            has_config * 0.20 +                        # config changes risky
            has_deps * 0.25 +                          # dep changes very risky
            author_failure_rate * 0.20 +               # author history
            is_large * 0.10 +                          # large PR penalty
            (complexity_score > 0.8) * 0.15 -          # high complexity
            has_tests * 0.10                            # tests reduce risk
        )
        base_p = min(max(base_p, 0.05), 0.95)
        
        # Add noise (real systems are not perfectly predictable)
        noise = np.random.normal(0, 0.05)
        p = min(max(base_p + noise, 0.0), 1.0)
        
        # Outcome
        failed = 1 if np.random.random() < p else 0
        
        data.append({
            "lines_changed": lines_changed / 2000,              # normalize
            "num_files_changed": num_files / 50,                # normalize
            "has_config_changes": has_config,
            "has_test_changes": has_tests,
            "author_failure_rate": author_failure_rate,
            "pr_age_hours": min(pr_age_hours / 168, 1.0),       # normalize to 1 week
            "is_large_pr": is_large,
            "dependency_changes": has_deps,
            "complexity_score": complexity_score,
            "time_since_last_deploy": min(time_since_deploy / 168, 1.0),
            "ci_failed": failed
        })
    
    return pd.DataFrame(data)


if __name__ == "__main__":
    df = generate_training_data()
    output_path = Path(__file__).parent / "training_data.csv"
    df.to_csv(output_path, index=False)
    
    print(f"Generated {len(df)} training samples")
    print(f"Failure rate: {df['ci_failed'].mean():.1%}")
    print(f"Saved to {output_path}")
```

---

## app/ml/train.py

```python
"""
Train the CI failure prediction model.
Run: python -m app.ml.train
"""
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from app.ml.synthetic_data import generate_training_data

FEATURE_COLS = [
    "lines_changed", "num_files_changed", "has_config_changes",
    "has_test_changes", "author_failure_rate", "pr_age_hours",
    "is_large_pr", "dependency_changes", "complexity_score",
    "time_since_last_deploy"
]
TARGET_COL = "ci_failed"
MODEL_PATH = Path(__file__).parent / "model.pkl"

def train():
    print("Generating training data...")
    df = generate_training_data(n=1000)  # More data = better model
    
    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Build pipeline: scaler + logistic regression
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(
            max_iter=1000,
            C=1.0,
            class_weight="balanced",  # Handle class imbalance
            random_state=42
        ))
    ])
    
    print("Training model...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    
    print("\n=== Model Evaluation ===")
    print(classification_report(y_test, y_pred, target_names=["Success", "Failure"]))
    print(f"AUC-ROC: {roc_auc_score(y_test, y_proba):.3f}")
    
    # Cross-validation
    cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring="roc_auc")
    print(f"Cross-val AUC: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    
    # Feature importance (coefficients)
    coefs = pipeline.named_steps["classifier"].coef_[0]
    feature_importance = sorted(zip(FEATURE_COLS, coefs), key=lambda x: abs(x[1]), reverse=True)
    print("\n=== Feature Importance ===")
    for feat, coef in feature_importance:
        print(f"  {feat:35s}: {coef:+.3f}")
    
    # Save model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"pipeline": pipeline, "features": FEATURE_COLS}, f)
    
    print(f"\nModel saved to {MODEL_PATH}")
    return pipeline

if __name__ == "__main__":
    train()
```

---

## app/services/ml_predictor.py

```python
import pickle
import numpy as np
from pathlib import Path
from app.config import settings

# Load model at startup
_model_cache = None

def get_model():
    global _model_cache
    if _model_cache is None:
        model_path = Path(settings.MODEL_PATH)
        if model_path.exists():
            with open(model_path, "rb") as f:
                _model_cache = pickle.load(f)
        else:
            print("WARNING: Model not found. Run app/ml/train.py first. Using rule-based fallback.")
            _model_cache = None
    return _model_cache

def predict_failure_probability(pr_features: dict) -> float:
    """
    Predict CI failure probability for a PR.
    
    pr_features: {
        lines_changed, num_files_changed, has_config_changes,
        has_test_changes, author_failure_rate, pr_age_hours,
        is_large_pr, dependency_changes, complexity_score,
        time_since_last_deploy
    }
    
    Returns: probability of failure (0.0 - 1.0)
    """
    model_data = get_model()
    
    if model_data is None:
        # Rule-based fallback
        return _rule_based_prediction(pr_features)
    
    pipeline = model_data["pipeline"]
    features = model_data["features"]
    
    # Build feature vector in correct order
    x = np.array([[pr_features.get(f, 0.0) for f in features]])
    
    probability = pipeline.predict_proba(x)[0][1]
    return float(round(probability, 3))

def _rule_based_prediction(pr_features: dict) -> float:
    """Simple rule-based fallback when model is not available."""
    risk = 0.15  # baseline
    
    lines = pr_features.get("lines_changed", 0)
    risk += min(lines / 2000, 1.0) * 0.30
    
    if pr_features.get("has_config_changes"):
        risk += 0.20
    if pr_features.get("dependency_changes"):
        risk += 0.25
    if pr_features.get("has_test_changes"):
        risk -= 0.10
    
    risk += pr_features.get("author_failure_rate", 0.3) * 0.20
    
    return float(round(min(max(risk, 0.0), 1.0), 3))


def normalize_pr_features(raw: dict) -> dict:
    """Normalize raw PR data to model input features."""
    total_lines = raw.get("lines_added", 0) + raw.get("lines_deleted", 0)
    
    return {
        "lines_changed": min(total_lines / 2000, 1.0),
        "num_files_changed": min(raw.get("files_changed", 0) / 50, 1.0),
        "has_config_changes": int(raw.get("has_config_changes", False)),
        "has_test_changes": int(raw.get("has_test_changes", False)),
        "author_failure_rate": raw.get("author_failure_rate", 0.3),
        "pr_age_hours": min(raw.get("pr_age_hours", 24) / 168, 1.0),
        "is_large_pr": int(total_lines > 500),
        "dependency_changes": int(raw.get("has_dependency_changes", False)),
        "complexity_score": raw.get("complexity_score", 0.5),
        "time_since_last_deploy": min(raw.get("time_since_last_deploy_hours", 48) / 168, 1.0),
    }
```

---

## scripts/seed_demo_data.py

```python
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
```
