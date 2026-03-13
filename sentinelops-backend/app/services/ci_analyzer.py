"""
CI pattern analysis service.
Detects anomalies in CI pipeline runs.
"""


class CIAnalyzer:
    """Analyze CI run patterns for anomalies."""

    def analyze_build_time(self, current_ms: int, historical: list[int]) -> dict:
        """Check if build time is anomalous."""
        if len(historical) < 5:
            return {"is_anomalous": False, "reason": "Insufficient data"}

        import statistics

        mean = statistics.mean(historical)
        stdev = statistics.stdev(historical)

        z_score = (current_ms - mean) / max(stdev, 1)
        is_anomalous = abs(z_score) > 2.0

        return {
            "is_anomalous": is_anomalous,
            "z_score": round(z_score, 2),
            "mean_ms": int(mean),
            "stdev_ms": int(stdev),
            "reason": (
                f"Build time is {abs(z_score):.1f} std deviations from mean" if is_anomalous else "Within normal range"
            ),
        }

    def detect_flaky_tests(self, run_logs: list[str]) -> list[str]:
        """Detect tests that pass/fail non-deterministically."""
        import re

        test_results = {}  # test_name -> set of results

        for log in run_logs:
            for line in log.split("\n"):
                # Match common test result patterns
                pass_match = re.search(r"PASSED (tests/\S+)", line)
                fail_match = re.search(r"FAILED (tests/\S+)", line)

                if pass_match:
                    name = pass_match.group(1)
                    test_results.setdefault(name, set()).add("pass")
                elif fail_match:
                    name = fail_match.group(1)
                    test_results.setdefault(name, set()).add("fail")

        # Flaky = has both pass and fail results
        flaky = [name for name, results in test_results.items() if len(results) > 1]
        return flaky
