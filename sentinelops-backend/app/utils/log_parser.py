"""
Utilities for parsing CI/CD log output.
"""

import re

# Common error patterns across CI providers
ERROR_PATTERNS = [
    r"ERROR:.*",
    r"Error:.*",
    r"FAILED.*",
    r"Traceback \(most recent call last\):",
    r"Exception:.*",
    r"AssertionError:.*",
    r"ModuleNotFoundError:.*",
    r"ImportError:.*",
    r"SyntaxError:.*",
    r"npm ERR!.*",
    r"yarn error.*",
    r"Process completed with exit code [1-9]",
    r"make: \*\*\*.*Error",
    r"COMPILATION ERROR",
    r"Build FAILED",
    r"Tests failed:",
    r"✗ FAIL",
    r"FAILURE: Build failed",
]

STEP_PATTERN = re.compile(r"^##\[.*?\]Run (.+)$", re.MULTILINE)


def extract_error_block(log_text: str, context_lines: int = 30) -> str:
    """
    Intelligently extract the most relevant error block from CI logs.

    Strategy:
    1. Find the last occurrence of a known error pattern
    2. Return N lines before and after for context
    """
    lines = log_text.split("\n")

    # Find lines matching error patterns
    error_line_indices = []
    for i, line in enumerate(lines):
        for pattern in ERROR_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                error_line_indices.append(i)
                break

    if not error_line_indices:
        # No errors found — return last N lines
        return "\n".join(lines[-context_lines:])

    # Use the last error occurrence as the anchor
    last_error_idx = error_line_indices[-1]

    # Also include any lines in a "block" around this error
    start = max(0, last_error_idx - 15)
    end = min(len(lines), last_error_idx + 15)

    # Expand backward to include full stack trace if applicable
    context_slice = lines[start:last_error_idx]
    if any("Traceback" in line_txt or "at " in line_txt for line_txt in context_slice):
        traceback_start = start
        lookback_limit = max(0, last_error_idx - 40)
        for i in range(last_error_idx, lookback_limit, -1):
            if "Traceback" in lines[i] or "Error in" in lines[i]:
                traceback_start = i
                break
        start = traceback_start

    return "\n".join(lines[start:end])


def detect_flaky_test(run_logs: list[str]) -> bool:
    """
    Detect if a test is flaky by comparing multiple run logs.
    Returns True if same test alternates between pass/fail.
    """
    # Simple heuristic: if failure pattern is inconsistent across runs
    failed_tests_per_run = []

    for log in run_logs:
        failed = set()
        for line in log.split("\n"):
            match = re.search(r"FAILED (tests/\S+)", line)
            if match:
                failed.add(match.group(1))
        failed_tests_per_run.append(failed)

    if len(failed_tests_per_run) < 2:
        return False

    # Flaky if tests fail in some runs but not others
    all_failed = set().union(*failed_tests_per_run)
    for test in all_failed:
        failed_in = sum(1 for run in failed_tests_per_run if test in run)
        if 0 < failed_in < len(failed_tests_per_run):
            return True

    return False


def detect_anomalous_build_time(
    current_duration_ms: int, historical_durations: list[int], std_multiplier: float = 2.0
) -> bool:
    """
    Returns True if current build time is anomalously high or low.
    Uses mean ± N standard deviations.
    """
    if len(historical_durations) < 5:
        return False  # Not enough data

    import statistics

    mean = statistics.mean(historical_durations)
    stdev = statistics.stdev(historical_durations)

    lower = mean - std_multiplier * stdev
    upper = mean + std_multiplier * stdev

    return not (lower <= current_duration_ms <= upper)


def extract_file_types(filenames: list[str]) -> list[str]:
    """Extract unique file extensions from a list of filenames."""
    import os

    extensions = set()
    for f in filenames:
        _, ext = os.path.splitext(f)
        if ext:
            extensions.add(ext.lower())
    return list(extensions)


def is_config_file(filename: str) -> bool:
    """Check if a file is a configuration file."""
    config_patterns = [
        ".yaml",
        ".yml",
        ".json",
        ".toml",
        ".ini",
        ".env",
        ".cfg",
        "dockerfile",
        "docker-compose",
        ".tf",
        ".tfvars",
        "makefile",
    ]
    lower = filename.lower()
    return any(p in lower for p in config_patterns)


def is_dependency_file(filename: str) -> bool:
    """Check if a file is a dependency manifest."""
    dep_files = [
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "requirements.txt",
        "pyproject.toml",
        "setup.py",
        "Pipfile",
        "go.mod",
        "go.sum",
        "Cargo.toml",
        "Cargo.lock",
        "pom.xml",
        "build.gradle",
        "Gemfile",
    ]
    return any(filename.endswith(d) or filename == d for d in dep_files)


def is_test_file(filename: str) -> bool:
    """Check if a file is a test file."""
    test_patterns = ["test_", "_test.", ".test.", ".spec.", "/tests/", "/test/", "__tests__"]
    lower = filename.lower()
    return any(p in lower for p in test_patterns)
