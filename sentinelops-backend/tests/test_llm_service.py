import pytest
from app.services.llm_service import analyze_failure_mock

@pytest.mark.asyncio
async def test_analyze_failure_mock():
    log_text = "Error: Connection refused to port 5432"
    result = await analyze_failure_mock(log_text)
    
    assert "root_cause" in result
    assert "suggested_fix" in result
    assert result["confidence"] > 0.5
    # The mock returns common failure messages, verify it returns a string with some length
    assert len(result["root_cause"]) > 10
