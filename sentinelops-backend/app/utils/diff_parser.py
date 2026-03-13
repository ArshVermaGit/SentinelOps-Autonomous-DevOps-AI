"""
Advanced Git diff parsing utilities for SentinelOps.
Extracts filename-level changes, line counts, and calculates complexity deltas.
"""

import re
from typing import Any, Dict, List


def parse_unified_diff(diff_text: str) -> Dict[str, Any]:
    """
    Parse a unified diff into structured data with complexity heuristics.

    Returns: {
        "files": [
            {
                "path": str,
                "additions": int,
                "deletions": int,
                "complexity_delta": float,
                "is_config": bool,
                "is_test": bool,
                "is_dep": bool
            }, ...
        ],
        "total_additions": int,
        "total_deletions": int,
        "total_files": int,
        "max_complexity_delta": float
    }
    """
    files = []
    current_file = None

    # Heuristic for complexity: search for control flow keywords in added lines
    complexity_keywords = [
        r"\bif\b",
        r"\bfor\b",
        r"\bwhile\b",
        r"\bswitch\b",
        r"\bcase\b",
        r"\btry\b",
        r"\bcatch\b",
        r"\bawait\b",
        r"\basync\b",
        r"\bdef\b",
        r"\bfunction\b",
    ]
    complexity_regex = re.compile("|".join(complexity_keywords))

    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            if current_file:
                files.append(current_file)

            # Extract path (handling a/ and b/ prefixes)
            match = re.search(r"diff --git a/(.+?) b/", line)
            path = match.group(1) if match else "unknown"

            current_file = {
                "path": path,
                "additions": 0,
                "deletions": 0,
                "complexity_delta": 0.0,
                "is_config": _is_config(path),
                "is_test": _is_test(path),
                "is_dep": _is_dep(path),
            }

        elif current_file:
            if line.startswith("+") and not line.startswith("+++"):
                current_file["additions"] += 1
                # Increase complexity if keyword found in added line
                if complexity_regex.search(line):
                    current_file["complexity_delta"] += 1.0
            elif line.startswith("-") and not line.startswith("---"):
                current_file["deletions"] += 1

    if current_file:
        files.append(current_file)

    max_comp = max((f["complexity_delta"] for f in files), default=0.0)
    return {
        "files": files,
        "total_additions": sum(f["additions"] for f in files),
        "total_deletions": sum(f["deletions"] for f in files),
        "total_files": len(files),
        "max_complexity_delta": max_comp,
    }


def _is_config(path: str) -> bool:
    """Check if file is a configuration file."""
    from app.utils.log_parser import is_config_file

    return is_config_file(path)


def _is_test(path: str) -> bool:
    """Check if file is a test file."""
    from app.utils.log_parser import is_test_file

    return is_test_file(path)


def _is_dep(path: str) -> bool:
    """Check if file is a dependency manifest."""
    from app.utils.log_parser import is_dependency_file

    return is_dependency_file(path)


def extract_changed_filenames(diff_text: str) -> List[str]:
    """Simple helper to get filenames from diff."""
    return [f["path"] for f in parse_unified_diff(diff_text)["files"]]
