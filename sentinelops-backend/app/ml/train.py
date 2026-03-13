"""
Train the CI failure prediction model.
Author: Arsh Verma
Run: python -m app.ml.train
"""

import pickle
from pathlib import Path

from app.ml.synthetic_data import generate_training_data
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_COLS = [
    "lines_changed",
    "num_files_changed",
    "has_config_changes",
    "has_test_changes",
    "author_failure_rate",
    "pr_age_hours",
    "is_large_pr",
    "dependency_changes",
    "complexity_score",
    "time_since_last_deploy",
]
TARGET_COL = "ci_failed"
MODEL_PATH = Path(__file__).parent / "model.pkl"


def train():
    print("Generating training data...")
    df = generate_training_data(n=1000)  # More data = better model

    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Build pipeline: scaler + logistic regression
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000, C=1.0, class_weight="balanced", random_state=42  # Handle class imbalance
                ),
            ),
        ]
    )

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
