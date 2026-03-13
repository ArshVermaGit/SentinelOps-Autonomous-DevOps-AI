"""
Digital Twin Simulation Engine - My logic for predicting deployment outcomes.
Author: Arsh Verma
"""

import random
from typing import Any, Dict, List

from app.services.ml_predictor import normalize_pr_features, predict_failure_probability


class DigitalTwinEngine:
    """
    Simulates how changes might impact the system based on historical patterns.
    """

    def simulate_deployment(
        self, pr_data: Dict[str, Any], repo_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Runs a Monte Carlo simulation (1000 iterations) to estimate reliability.
        """
        # Normalize features for the ML model
        features = normalize_pr_features(
            {
                **pr_data,
                "author_failure_rate": repo_stats.get("author_failure_rate", 0.15),
                "time_since_last_deploy_hours": repo_stats.get(
                    "time_since_last_deploy", 24
                ),
            }
        )

        # Get base failure probability from ML model
        base_prob = predict_failure_probability(features)

        # Simulation parameters
        iterations = 1000
        failures = 0
        impact_scores = []

        # Run Monte Carlo
        for _ in range(iterations):
            # Add stochastic noise based on repo stability
            noise = random.uniform(-0.05, 0.05)
            if random.random() < (base_prob + noise):
                failures += 1
                # Estimate blast radius/impact if failure occurs
                if pr_data.get("has_config_changes"):
                    impact = random.uniform(0.3, 0.9)
                else:
                    impact = random.uniform(0.1, 0.5)
                impact_scores.append(impact)

        failure_rate = failures / iterations
        if impact_scores:
            avg_impact = sum(impact_scores) / len(impact_scores)
        else:
            avg_impact = 0

        # Determine confidence and verdict
        if failure_rate < 0.2:
            verdict = "GO"
        elif failure_rate < 0.5:
            verdict = "CAUTION"
        else:
            verdict = "STOP"

        return {
            "simulated_failure_rate": round(failure_rate, 3),
            "estimated_impact": round(avg_impact, 2),
            "verdict": verdict,
            "confidence_interval": [
                round(failure_rate - 0.02, 3),
                round(failure_rate + 0.02, 3),
            ],
            "simulation_iterations": iterations,
            "risk_distribution": self._generate_risk_distribution(failure_rate),
        }

    def _generate_risk_distribution(self, mean: float) -> List[float]:
        """Generates a bell-curve like distribution for visualization."""
        # Simplified for demo
        return [max(0, mean + random.uniform(-0.1, 0.1)) for _ in range(10)]


simulation_engine = DigitalTwinEngine()
