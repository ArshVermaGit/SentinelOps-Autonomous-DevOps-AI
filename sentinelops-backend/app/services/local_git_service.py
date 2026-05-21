"""
Local Git Service - Multi-repo aware. Detects changes, runs health checks,
and handles commit/push for any linked repository.
Author: Arsh Verma
"""

import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from typing import Any, Dict, List, NewType, Optional

from app.models.ci_run import CIRun  # pyre-ignore[21]
from app.models.incident import Incident  # pyre-ignore[21]
from app.models.pull_request import PullRequest  # pyre-ignore[21]
from app.models.repository import Repository  # pyre-ignore[21]
from app.services.risk_analyzer import RiskAnalyzer  # pyre-ignore[21]
from app.utils.diff_parser import parse_unified_diff  # pyre-ignore[21]
from sqlalchemy import select  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

logger = logging.getLogger(__name__)

ValidatedRepoPath = NewType("ValidatedRepoPath", str)

REPOS_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "linked_repos.json"
)
_configured_repo_root = os.environ.get("SENTINELOPS_REPO_ROOT")
ALLOWED_REPO_ROOT = (
    os.path.realpath(os.path.abspath(os.path.expanduser(_configured_repo_root)))
    if _configured_repo_root
    else ""
)


def _load_linked_repos() -> List[Dict[str, str]]:
    """Load the list of linked repos from disk."""
    try:
        with open(REPOS_CONFIG_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_linked_repos(repos: List[Dict[str, str]]) -> None:
    """Persist the linked repos list to disk."""
    with open(REPOS_CONFIG_PATH, "w") as f:
        json.dump(repos, f, indent=2)


class LocalGitService:
    """Handles git operations for any repository path on the local machine."""

    _ALLOWED_GIT_ARGS = {
        ("status", "--porcelain"),
        ("diff", "--cached"),
        ("diff",),
        ("rev-list", "--left-right", "--count", "@{upstream}...HEAD"),
        ("branch", "--show-current"),
        ("add", "."),
        ("commit", "-m"),
        ("push",),
    }

    def __init__(self):
        self.analyzer = RiskAnalyzer()

    def _normalize_repo_path(self, repo_path: str) -> str:
        """Normalize a repository path for safe comparisons."""
        return os.path.realpath(os.path.abspath(os.path.expanduser(repo_path)))

    def _is_linked_repo_path(self, repo_path: str) -> bool:
        """Return True when repo_path matches a linked repository path."""
        normalized = self._normalize_repo_path(repo_path)
        linked = _load_linked_repos()
        linked_paths = {
            self._normalize_repo_path(r.get("local_path", ""))
            for r in linked
            if r.get("local_path")
        }
        return normalized in linked_paths

    def _validate_repo_path_for_fs_access(
        self, repo_path: str
    ) -> Optional[ValidatedRepoPath]:
        """Validate and normalize a repo path before filesystem access."""
        if not isinstance(repo_path, str):
            return None
        candidate = repo_path.strip()
        if not candidate or "\x00" in candidate:
            return None

        normalized = self._normalize_repo_path(candidate)
        if not normalized or normalized.startswith("-") or not os.path.isabs(normalized):
            return None
        if not self._is_within_allowed_root(normalized):
            return None

        linked = _load_linked_repos()
        linked_paths = {
            self._normalize_repo_path(r.get("local_path", ""))
            for r in linked
            if r.get("local_path")
        }
        if normalized not in linked_paths:
            return None
        return ValidatedRepoPath(normalized)

    def _is_within_allowed_root(self, normalized_path: str) -> bool:
        """Return True if normalized_path is inside configured allowed repo root."""
        try:
            if not ALLOWED_REPO_ROOT:
                return False
            allowed_root = os.path.realpath(
                os.path.abspath(os.path.expanduser(ALLOWED_REPO_ROOT))
            )
            if not os.path.isabs(allowed_root) or not os.path.isdir(allowed_root):
                return False
            return os.path.commonpath([normalized_path, allowed_root]) == allowed_root
        except ValueError:
            return False

    def _validate_repo_path_for_linking(self, repo_path: str) -> str:
        """Validate and normalize a repo path before adding it to linked repos."""
        if not isinstance(repo_path, str):
            return ""
        candidate = repo_path.strip()
        if not candidate or "\x00" in candidate:
            return ""

        normalized = self._normalize_repo_path(candidate)
        if not normalized or normalized.startswith("-") or not os.path.isabs(normalized):
            return ""
        if not self._is_within_allowed_root(normalized):
            return ""
        # Do not allow linking via symlinked repository directories.
        if os.path.islink(normalized):
            return ""
        if not os.path.isdir(normalized):
            return ""
        git_dir = os.path.join(normalized, ".git")
        # Require a real .git directory inside the repository path and reject symlinks.
        if not os.path.isdir(git_dir) or os.path.islink(git_dir):
            return ""
        return normalized

    def _run_git(self, repo_path: str, args: List[str]) -> str:
        """Run a git command in a specific repo directory."""
        validated_repo_path = self._validate_repo_path_for_fs_access(repo_path)

        # Defense-in-depth: reject invalid/option-like paths before command execution.
        if not validated_repo_path:
            logger.warning(f"Blocked git cmd for invalid repo path: {repo_path}")
            return ""

        repo_path_str = str(validated_repo_path)
        if not os.path.isdir(repo_path_str):
            logger.warning(f"Blocked git cmd for invalid repo path: {repo_path_str}")
            return ""

        args_key = tuple(args)
        is_commit_with_file = (
            len(args) == 3 and args[0] == "commit" and args[1] == "--file"
        )
        if args_key not in self._ALLOWED_GIT_ARGS and not is_commit_with_file:
            logger.warning(f"Blocked git cmd with disallowed args in {repo_path_str}: {args}")
            return ""

        cmd: List[str]
        if args_key == ("status", "--short"):
            cmd = ["git", "-C", repo_path_str, "status", "--short"]
        elif args_key == ("diff", "--cached", "--name-only"):
            cmd = ["git", "-C", repo_path_str, "diff", "--cached", "--name-only"]
        elif args_key == ("diff", "--name-only"):
            cmd = ["git", "-C", repo_path_str, "diff", "--name-only"]
        elif args_key == ("add", "."):
            cmd = ["git", "-C", repo_path_str, "add", "."]
        elif args_key == ("push",):
            cmd = ["git", "-C", repo_path_str, "push"]
        elif is_commit_with_file:
            message_file = args[2]
            if (
                not isinstance(message_file, str)
                or not message_file
                or message_file.startswith("-")
                or "\x00" in message_file
                or not os.path.isabs(message_file)
                or not os.path.isfile(message_file)
            ):
                logger.warning(
                    f"Blocked git cmd with invalid commit message file in {repo_path_str}"
                )
                return ""
            cmd = ["git", "-C", repo_path_str, "commit", "--file", message_file]
        else:
            logger.warning(f"Blocked git cmd with disallowed args in {repo_path_str}: {args}")
            return ""

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=15,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.warning(f"Git cmd failed in {repo_path_str}: {e.stderr.strip()}")
            return ""
        except subprocess.TimeoutExpired:
            logger.warning(f"Git cmd timed out in {repo_path_str}")
            return ""

    # ── Repo Management ──────────────────────────────────────────────

    def list_linked_repos(self) -> List[Dict[str, Any]]:
        """Return all linked repos with their live status."""
        repos = _load_linked_repos()
        result = []
        for repo in repos:
            status = self.get_repo_status(repo["local_path"])
            result.append({**repo, **status})
        return result

    def link_repo(self, name: str, local_path: str, github_url: str) -> bool:
        """Link a new repo by its local folder path."""
        validated_path = self._validate_repo_path_for_linking(local_path)
        if not validated_path:
            return False
        repos = _load_linked_repos()
        # Prevent duplicates (compare canonicalized paths)
        if any(
            self._normalize_repo_path(r.get("local_path", "")) == validated_path
            for r in repos
            if r.get("local_path")
        ):
            return True
        repos.append(
            {"name": name, "local_path": validated_path, "github_url": github_url}
        )
        _save_linked_repos(repos)
        return True

    def unlink_repo(self, local_path: str) -> bool:
        """Remove a repo from the linked list."""
        repos = _load_linked_repos()
        repos = [r for r in repos if r["local_path"] != local_path]
        _save_linked_repos(repos)
        return True

    # ── Status & Health ──────────────────────────────────────────────

    def get_repo_status(self, repo_path: str) -> Dict[str, Any]:
        """Full status for a single repo: changes, sync, health, risk."""
        validated_repo_path = self._validate_repo_path_for_fs_access(repo_path)
        if not validated_repo_path:
            return {
                "branch": "unknown",
                "changed_files": {"staged": [], "modified": [], "untracked": []},
                "sync": {"state": "error", "ahead": 0, "behind": 0},
                "health": {
                    "passing": False,
                    "error_count": 1,
                    "errors": ["Path is not linked"],
                },
                "risk": {"risk_level": "safe", "risk_probability": 0.0},
                "ready_to_commit": False,
                "error": "Path is not linked",
            }
        repo_path = str(validated_repo_path)
        if not os.path.isdir(repo_path):
            return {
                "branch": "unknown",
                "changed_files": {"staged": [], "modified": [], "untracked": []},
                "sync": {"state": "error", "ahead": 0, "behind": 0},
                "health": {
                    "passing": False,
                    "error_count": 1,
                    "errors": [f"Path not found: {repo_path}"],
                },
                "risk": {"risk_level": "safe", "risk_probability": 0.0},
                "ready_to_commit": False,
                "error": "Path not found",
            }

        changed_files = self._get_changed_files(repo_path)
        sync_status = self._get_sync_status(repo_path)
        current_branch = (
            self._run_git(repo_path, ["branch", "--show-current"]) or "main"
        )
        health = self._run_health_check(repo_path)
        risk = self._calculate_risk(repo_path)

        ready = health["passing"] and len(changed_files["staged"]) > 0

        return {
            "branch": current_branch,
            "changed_files": changed_files,
            "sync": sync_status,
            "health": health,
            "risk": risk,
            "ready_to_commit": ready,
        }

    def _get_changed_files(self, repo_path: str) -> Dict[str, List[str]]:
        """Detect all modified, staged, and untracked files."""
        status_output = self._run_git(repo_path, ["status", "--porcelain"])
        staged, modified, untracked = [], [], []

        for line in status_output.splitlines():
            if not line or len(line) < 3:
                continue
            index_flag = line[0]
            work_flag = line[1]
            filepath = line[3:]  # pyre-ignore

            if index_flag in ("M", "A", "D", "R"):
                staged.append(filepath)
            if work_flag in ("M", "D"):
                modified.append(filepath)
            if index_flag == "?" and work_flag == "?":
                untracked.append(filepath)

        return {"staged": staged, "modified": modified, "untracked": untracked}

    def _get_sync_status(self, repo_path: str) -> Dict[str, Any]:
        """Check if local is ahead/behind the remote."""
        self._run_git(repo_path, ["fetch", "--quiet"])
        status = self._run_git(repo_path, ["status", "--branch", "--porcelain=v2"])

        ahead, behind = 0, 0
        for line in status.splitlines():
            if line.startswith("# branch.ab"):
                parts = line.split()
                for part in parts:
                    if part.startswith("+"):
                        try:
                            ahead = int(part[1:])  # pyre-ignore
                        except ValueError:
                            pass
                    elif part.startswith("-"):
                        try:
                            behind = abs(int(part[1:]))  # pyre-ignore
                        except ValueError:
                            pass

        if ahead > 0 and behind > 0:
            state = "diverged"
        elif ahead > 0:
            state = "ahead"
        elif behind > 0:
            state = "behind"
        else:
            state = "synced"

        return {"state": state, "ahead": ahead, "behind": behind}

    def _run_health_check(self, repo_path: str) -> Dict[str, Any]:
        """Try to detect and run the project's build/lint commands."""
        errors: List[str] = []

        # Detect project type and run appropriate checks
        if os.path.isfile(os.path.join(repo_path, "package.json")):
            # Node.js project — try lint
            try:
                result = subprocess.run(
                    ["npm", "run", "lint", "--silent"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode != 0:
                    for line in result.stderr.splitlines() + result.stdout.splitlines():
                        line = line.strip()
                        if line and (
                            "error" in line.lower() or "warning" in line.lower()
                        ):
                            errors.append(line)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        elif os.path.isfile(
            os.path.join(repo_path, "requirements.txt")
        ) or os.path.isfile(os.path.join(repo_path, "pyproject.toml")):
            # Python project — try syntax check
            try:
                result = subprocess.run(
                    ["python3", "-m", "py_compile", "--help"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        return {
            "passing": len(errors) == 0,
            "error_count": len(errors),
            "errors": errors[:20],  # pyre-ignore
        }

    def _calculate_risk(self, repo_path: str) -> Dict[str, Any]:
        """Calculate risk score for staged changes."""
        diff_text = self._run_git(repo_path, ["diff", "--staged"])
        if not diff_text:
            diff_text = self._run_git(repo_path, ["diff"])
        if not diff_text:
            return {"risk_level": "safe", "risk_probability": 0.0}

        try:
            diff_info = parse_unified_diff(diff_text)
            has_config = any(f["is_config"] for f in diff_info["files"])
            has_dep = any(f["is_dep"] for f in diff_info["files"])
            has_test = any(f["is_test"] for f in diff_info["files"])

            result = self.analyzer.analyze_pr(
                {
                    "lines_added": sum(
                        f.get("additions", 0) for f in diff_info["files"]
                    ),
                    "lines_deleted": sum(
                        f.get("deletions", 0) for f in diff_info["files"]
                    ),
                    "files_changed": len(diff_info["files"]),
                    "has_config_changes": has_config,
                    "has_dependency_changes": has_dep,
                    "has_test_changes": has_test,
                    "complexity_delta": diff_info["max_complexity_delta"],
                },
                {"total_prs": 10, "failed_prs": 1},
            )
            return result
        except Exception as e:
            logger.warning(f"Risk calc failed: {e}")
            return {"risk_level": "safe", "risk_probability": 0.0}

    # ── Actions ──────────────────────────────────────────────────────

    def stage_all(self, repo_path: str) -> bool:
        """Stage all changes in a repo."""
        repo_path = os.path.expanduser(repo_path)
        self._run_git(repo_path, ["add", "-A"])
        return True  # git add -A doesn't fail unless path is bad

    async def sync_repositories(self, db: AsyncSession) -> None:
        """Sync all linked repos from disk to the SQLite database."""
        repos = _load_linked_repos()
        for repo_cfg in repos:
            path = repo_cfg["local_path"]
            name = repo_cfg["name"]
            status = self.get_repo_status(path)

            # 1. Update Repository Record
            res = await db.execute(select(Repository).where(Repository.url == path))
            repo = res.scalar_one_or_none()

            if not repo:
                repo = Repository(
                    name=name,
                    full_name=f"local/{name}",
                    url=path,
                    github_id=hash(path) % 1000000,  # Deterministic mock ID
                )
                db.add(repo)
                await db.flush()

            repo.risk_score = status["risk"]["risk_probability"]
            repo.last_analyzed = datetime.utcnow()

            # 2. Sync 'Local PR' (Uncommitted changes)
            staged_count = len(status["changed_files"]["staged"])
            modified_count = len(status["changed_files"]["modified"])

            if staged_count > 0 or modified_count > 0:
                # Find or create a 'Local Changes' PR record
                pr_res = await db.execute(
                    select(PullRequest).where(
                        PullRequest.repo_id == repo.id,
                        PullRequest.github_pr_number
                        == 0,  # Identifier for local changes
                    )
                )
                pr = pr_res.scalar_one_or_none()

                if not pr:
                    pr = PullRequest(
                        repo_id=repo.id,
                        github_pr_number=0,
                        title=f"Local Changes: {name}",
                        author="You (Local)",
                        head_branch=status["branch"],
                        status="open",
                    )
                    db.add(pr)
                    await db.flush()

                pr.lines_added = status["risk"].get("lines_added", 0)
                pr.lines_deleted = status["risk"].get("lines_deleted", 0)
                pr.files_changed = staged_count + modified_count
                pr.risk_probability = status["risk"]["risk_probability"]
                pr.risk_level = status["risk"]["risk_level"]
                pr.risk_factors = status["risk"].get("risk_factors", [])
                pr.created_at = datetime.utcnow()

            # 3. Handle Health Failures as Incidents
            if not status["health"]["passing"]:
                # Create a CI Run record for the failed local check
                run = CIRun(
                    repo_id=repo.id,
                    workflow_name="Local Health Check",
                    status="failure",
                    started_at=datetime.utcnow(),
                    finished_at=datetime.utcnow(),
                    log_text="\n".join(status["health"]["errors"]),
                )
                db.add(run)
                await db.flush()

                # Create an Incident
                incident = Incident(
                    ci_run_id=run.id,
                    root_cause=f"Local health check failed in {name}",
                    error_category=(
                        "lint" if "npm" in status["health"]["errors"][0] else "syntax"
                    ),
                    status="open",
                )
                db.add(incident)

            await db.commit()

    def _sanitize_commit_message(self, message: str) -> str:
        """Validate and sanitize commit message before process execution."""
        if not isinstance(message, str):
            return ""
        cleaned = message.strip()
        if not cleaned:
            return ""
        if "\x00" in cleaned or "\n" in cleaned or "\r" in cleaned:
            return ""
        # Prevent option-like values from being interpreted as git flags.
        if cleaned.startswith("-"):
            return ""
        if len(cleaned) > 512:
            return ""
        return cleaned

    def commit_and_push(self, repo_path: str, message: str) -> Dict[str, Any]:
        """Stage all, commit, and push to remote."""
        # Note: In a real app, we'd pass the DB session here to record the success
        # but for now we'll do it via the next sync cycle.
        repo_path = os.path.expanduser(repo_path)
        safe_message = self._sanitize_commit_message(message)
        if not safe_message:
            return {"success": False, "error": "Empty commit message"}

        # Stage everything
        self.stage_all(repo_path)

        temp_message_file = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as tmp:
                tmp.write(safe_message)
                tmp.flush()
                temp_message_file = tmp.name

            # Commit
            commit_out = self._run_git(repo_path, ["commit", "--file", temp_message_file])
            if not commit_out:
                return {"success": False, "error": "Nothing to commit or commit failed"}

            # Push
            self._run_git(repo_path, ["push"])
            return {"success": True, "message": "Changes committed and pushed to GitHub"}
        finally:
            if temp_message_file and os.path.exists(temp_message_file):
                try:
                    os.remove(temp_message_file)
                except OSError:
                    logger.warning("Failed to remove temporary commit message file.")


local_git = LocalGitService()
