"""
Generate synthetic training data for the CI failure predictor.
500 realistic PRs with outcomes based on engineered rules + noise.
"""

from pathlib import Path

import numpy as np
import pandas as pd

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
            0.15  # baseline failure rate
            + (lines_changed / 2000) * 0.30  # large changes = more risk
            + has_config * 0.20  # config changes risky
            + has_deps * 0.25  # dep changes very risky
            + author_failure_rate * 0.20  # author history
            + is_large * 0.10  # large PR penalty
            + (complexity_score > 0.8) * 0.15  # high complexity
            - has_tests * 0.10  # tests reduce risk
        )
        base_p = min(max(base_p, 0.05), 0.95)

        # Add noise (real systems are not perfectly predictable)
        noise = np.random.normal(0, 0.05)
        p = min(max(base_p + noise, 0.0), 1.0)

        # Outcome
        failed = 1 if np.random.random() < p else 0

        data.append(
            {
                "lines_changed": lines_changed / 2000,  # normalize
                "num_files_changed": num_files / 50,  # normalize
                "has_config_changes": has_config,
                "has_test_changes": has_tests,
                "author_failure_rate": author_failure_rate,
                "pr_age_hours": min(pr_age_hours / 168, 1.0),  # normalize to 1 week
                "is_large_pr": is_large,
                "dependency_changes": has_deps,
                "complexity_score": complexity_score,
                "time_since_last_deploy": min(time_since_deploy / 168, 1.0),
                "ci_failed": failed,
            }
        )

    return pd.DataFrame(data)


if __name__ == "__main__":
    df = generate_training_data()
    output_path = Path(__file__).parent / "training_data.csv"
    df.to_csv(output_path, index=False)

    print(f"Generated {len(df)} training samples")
    print(f"Failure rate: {df['ci_failed'].mean():.1%}")
    print(f"Saved to {output_path}")
