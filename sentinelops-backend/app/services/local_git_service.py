"""
Local Git Service - Handles detection of staged changes and local commits.
Author: Arsh Verma
"""
import subprocess
import os
from typing import Dict, List, Any, Optional
from app.services.risk_analyzer import RiskAnalyzer
from app.utils.diff_parser import parse_unified_diff

class LocalGitService:
    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
        self.analyzer = RiskAnalyzer()

    def _run_git(self, args: List[str]) -> str:
        """Helper to run git commands safely."""
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path] + args,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git Error: {e.stderr}")
            return ""

    def get_staged_status(self) -> Dict[str, Any]:
        """Detects staged changes and calculates AI risk score."""
        diff_text = self._run_git(["diff", "--staged"])
        
        if not diff_text:
            return {"has_changes": False, "risk": None}

        # Parse the local staged diff
        diff_info = parse_unified_diff(diff_text)
        
        # Aggregate flags
        has_config = any(f["is_config"] for f in diff_info["files"])
        has_dep = any(f["is_dep"] for f in diff_info["files"])
        has_test = any(f["is_test"] for f in diff_info["files"])
        
        # Analyze risk (using dummy author stats for local dev)
        dummy_stats = {"total_prs": 10, "failed_prs": 1}
        
        risk_result = self.analyzer.analyze_pr({
            "lines_added": sum(f.get("additions", 0) for f in diff_info["files"]),
            "lines_deleted": sum(f.get("deletions", 0) for f in diff_info["files"]),
            "files_changed": len(diff_info["files"]),
            "file_types": [f["path"].split(".")[-1] if "." in f["path"] else "unknown" for f in diff_info["files"]],
            "has_config_changes": has_config,
            "has_dependency_changes": has_dep,
            "has_test_changes": has_test,
            "complexity_delta": diff_info["max_complexity_delta"],
        }, dummy_stats)

        return {
            "has_changes": True,
            "diff_summary": {
                "files_count": len(diff_info["files"]),
                "max_complexity": diff_info["max_complexity_delta"]
            },
            "risk": risk_result
        }

    def commit_and_push(self, message: str) -> bool:
        """Finalizes the work by committing and pushing to GitHub."""
        if not message.strip():
            return False
            
        try:
            # 1. Commit
            self._run_git(["commit", "-m", message])
            # 2. Push (Assumes upstream is set)
            self._run_git(["push"])
            return True
        except Exception:
            return False

local_git_service = LocalGitService()
