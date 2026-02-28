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
