import pytest
from app.services.ci_analyzer import CIAnalyzer


@pytest.fixture
def analyzer():
    return CIAnalyzer()


def test_analyze_build_time_normal(analyzer):
    historical = [120000, 125000, 118000, 122000, 121000]
    result = analyzer.analyze_build_time(123000, historical)
    assert result["is_anomalous"] is False


def test_analyze_build_time_anomalous(analyzer):
    historical = [120000, 125000, 118000, 122000, 121000]
    result = analyzer.analyze_build_time(300000, historical)  # Much higher
    assert result["is_anomalous"] is True
    assert "Build time is" in result["reason"]


def test_detect_flaky_tests(analyzer):
    logs = [
        "PASSED tests/test_auth.py\nFAILED tests/test_db.py",
        "PASSED tests/test_auth.py\nPASSED tests/test_db.py",  # test_db passed
    ]
    flaky = analyzer.detect_flaky_tests(logs)
    assert "tests/test_db.py" in flaky
    assert "tests/test_auth.py" not in flaky
