"""
Similarity search service.
Wraps embedding service for higher-level incident similarity operations.
"""

from app.services.embedding_service import find_similar_incidents


async def search_similar(db, log_text: str, limit: int = 3) -> list[dict]:
    """Find similar incidents for a given log text."""
    return await find_similar_incidents(db, log_text, threshold=0.7, limit=limit)
