"""
Embedding service for log similarity search.
Uses SentenceTransformers to embed CI logs and find similar incidents.
"""
import numpy as np

# Lazy-load model to avoid import errors if not installed
_model = None

def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            print("WARNING: sentence-transformers not installed. Using mock embeddings.")
            _model = "mock"
    return _model

_embedding_cache = {}

def embed_log(log_text: str) -> list[float]:
    """Create embedding vector for log text with local caching."""
    clean_log = log_text[-2000:]
    if clean_log in _embedding_cache:
        return _embedding_cache[clean_log]
    
    model = _get_model()
    if model == "mock":
        embedding = np.random.rand(384).tolist()
    else:
        embedding = model.encode(clean_log, convert_to_numpy=True).tolist()
    
    if len(_embedding_cache) < 100:
        _embedding_cache[clean_log] = embedding
    return embedding

def cosine_similarity(a: list, b: list) -> float:
    """Calculate cosine similarity between two embedding vectors."""
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

async def find_similar_incidents(
    db,
    log_text: str,
    threshold: float = 0.7,
    limit: int = 3
) -> list[dict]:
    """Find similar past incidents using embedding similarity."""
    from sqlalchemy import select
    from app.models.log_embedding import LogEmbedding
    
    new_embedding = embed_log(log_text)
    
    # Fetch all stored embeddings
    result = await db.execute(select(LogEmbedding))
    stored = result.scalars().all()
    
    # Calculate similarities
    similarities = []
    for stored_emb in stored:
        sim = cosine_similarity(new_embedding, stored_emb.embedding_vector)
        if sim >= threshold:
            similarities.append({
                "embedding_id": stored_emb.id,
                "ci_run_id": stored_emb.ci_run_id,
                "similarity_score": sim
            })
    
    # Sort by similarity descending
    similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
    return similarities[:limit]
