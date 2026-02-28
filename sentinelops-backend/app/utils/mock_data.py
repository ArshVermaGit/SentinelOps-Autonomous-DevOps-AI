"""
Demo mock data generator for when external services are unavailable.
"""
import random
from datetime import datetime, timedelta


def generate_mock_ci_health(days: int = 30) -> list[dict]:
    """Generate mock CI health data for charting."""
    data = []
    base = datetime.utcnow() - timedelta(days=days)
    
    for day in range(days):
        date = base + timedelta(days=day)
        total = random.randint(5, 15)
        failures = random.randint(0, max(1, total // 4))
        
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "success": total - failures,
            "failure": failures,
            "total": total,
            "avg_duration": random.randint(60000, 240000)
        })
    
    return data


def generate_mock_dashboard() -> dict:
    """Generate mock dashboard summary."""
    return {
        "repos": {
            "total": 4,
            "high_risk": 2,
            "avg_risk_score": 0.62
        },
        "ci": {
            "total_runs_30d": 156,
            "failed_runs_30d": 28,
            "success_rate": 82.1,
            "avg_build_time_ms": 145000
        },
        "incidents": {
            "open": 3,
            "total_30d": 8
        },
        "repos_list": [
            {"id": 1, "name": "data-pipeline", "risk_score": 0.85, "failure_rate": 0.33},
            {"id": 2, "name": "api-gateway", "risk_score": 0.72, "failure_rate": 0.24},
            {"id": 3, "name": "payment-service", "risk_score": 0.58, "failure_rate": 0.18},
            {"id": 4, "name": "frontend-app", "risk_score": 0.31, "failure_rate": 0.09},
        ]
    }
