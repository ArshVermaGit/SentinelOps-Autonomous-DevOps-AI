"""Tests for risk analyzer."""

import pytest
from app.services.risk_analyzer import RiskAnalyzer


@pytest.fixture
def analyzer():
    return RiskAnalyzer()


def test_analyze_pr_safe(analyzer):
    pr_data = {
        "lines_added": 10,
        "lines_deleted": 5,
        "files_changed": 1,
        "has_config_changes": False,
        "has_dependency_changes": False,
        "has_test_changes": True,
        "complexity_delta": 0.0,
    }
    author_stats = {"total_prs": 100, "failed_prs": 5, "avg_lines_changed": 50}

    result = analyzer.analyze_pr(pr_data, author_stats)
    assert result["risk_level"] == "safe"


def test_high_risk_pr():
    analyzer = RiskAnalyzer()
    result = analyzer.analyze_pr(
        {
            "lines_added": 800,
            "lines_deleted": 400,
            "files_changed": 30,
            "has_dependency_changes": True,
            "has_config_changes": True,
        },
        {"total_prs": 20, "failed_prs": 10, "avg_lines_changed": 100},
    )
    assert result["risk_level"] == "high"
    assert result["risk_probability"] > 0.65
