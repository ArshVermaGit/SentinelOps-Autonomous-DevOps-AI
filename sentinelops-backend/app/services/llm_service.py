from openai import AsyncOpenAI
from app.config import settings
import json
import re

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

LLM_SYSTEM_PROMPT = """You are SentinelOps, an expert DevOps root cause analyzer. 
You analyze CI/CD failures and provide structured, actionable insights.
Always respond with valid JSON only. No markdown, no preamble."""

LLM_USER_TEMPLATE = """A CI pipeline has failed. Analyze and respond in JSON only.

## Failed CI Log (last 50 lines):
{error_log}

## Code Diff (files changed in this PR):
{code_diff}

## Similar Past Incidents:
{similar_incidents}

## Required JSON Response:
{{
  "root_cause": "string - what caused this failure",
  "responsible_files": ["file1.py"],
  "error_category": "dependency|syntax|test|config|runtime|network",
  "llm_confidence": 0.0,
  "suggested_fix": "string - specific actionable fix",
  "fix_diff": "string - unified diff format patch",
  "risk_if_unresolved": "string - consequences",
  "estimated_fix_time": "5 minutes|1 hour|half day|full day"
}}"""

async def analyze_failure(error_log: str, code_diff: str, similar_incidents: list) -> dict:
    """Call OpenAI to analyze CI failure and return structured root cause."""
    
    similar_text = "\n".join([
        f"- Incident #{inc['id']}: {inc['root_cause']} (similarity: {inc['similarity_score']:.0%})"
        for inc in similar_incidents[:3]
    ]) or "No similar incidents found."
    
    user_message = LLM_USER_TEMPLATE.format(
        error_log=error_log[-3000:],      # Last 3000 chars of log
        code_diff=code_diff[:2000],        # First 2000 chars of diff
        similar_incidents=similar_text
    )
    
    if not client:
        return await analyze_failure_mock(error_log)
    
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": LLM_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.1,  # Low temperature for deterministic analysis
        max_tokens=1500,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    return json.loads(content)


async def analyze_failure_mock(error_log: str) -> dict:
    """Mock LLM response for demo without API key."""
    return {
        "root_cause": "Import error in database connection module caused by missing environment variable DB_HOST",
        "responsible_files": ["app/database.py", "docker compose.yml"],
        "error_category": "logic",
        "llm_confidence": 0.85,
        "suggested_fix": "Add DB_HOST=postgres to environment variables to ensure the app can reach the database container.",
        "fix_diff": "--- a/docker compose.yml\n+++ b/docker compose.yml\n@@ -10,6 +10,7 @@\n     environment:\n       - DB_NAME=myapp\n       - DB_USER=postgres\n+      - DB_HOST=postgres\n       - DB_PASSWORD=secret",
        "risk_if_unresolved": "All database operations will fail in CI and production",
        "estimated_fix_time": "5 minutes",
        "is_mock": True
    }
