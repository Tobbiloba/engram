#!/usr/bin/env python3
"""
Git utilities for Engram - Temporal Memory support.

Extracts commit history, diffs, and file change information.
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class FileChange:
    """Represents a file change in a commit."""
    path: str
    change_type: str  # A=added, M=modified, D=deleted, R=renamed
    lines_added: int = 0
    lines_deleted: int = 0


@dataclass
class Commit:
    """Represents a git commit."""
    hash: str
    short_hash: str
    message: str
    author: str
    date: datetime
    files: List[FileChange]


def is_git_repo(path: Path) -> bool:
    """Check if path is inside a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=str(path),
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def get_repo_root(path: Path) -> Optional[Path]:
    """Get the root directory of the git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(path),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    return None


def get_recent_commits(path: Path, days: int = 7, max_commits: int = 50) -> List[Commit]:
    """
    Get recent commits from the git repository.

    Args:
        path: Path inside the git repository
        days: Number of days to look back
        max_commits: Maximum number of commits to return

    Returns:
        List of Commit objects
    """
    if not is_git_repo(path):
        return []

    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    try:
        # Get commit info with file changes
        result = subprocess.run(
            [
                "git", "log",
                f"--since={since_date}",
                f"-n{max_commits}",
                "--pretty=format:%H|%h|%s|%an|%aI",
                "--name-status"
            ],
            cwd=str(path),
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return []

        commits = []
        current_commit = None

        for line in result.stdout.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Check if this is a commit line (contains |)
            if "|" in line and line.count("|") == 4:
                # Save previous commit
                if current_commit:
                    commits.append(current_commit)

                # Parse new commit
                parts = line.split("|")
                current_commit = Commit(
                    hash=parts[0],
                    short_hash=parts[1],
                    message=parts[2],
                    author=parts[3],
                    date=datetime.fromisoformat(parts[4]),
                    files=[]
                )
            elif current_commit and "\t" in line:
                # This is a file change line
                parts = line.split("\t")
                if len(parts) >= 2:
                    change_type = parts[0][0]  # First char: A, M, D, R
                    file_path = parts[-1]  # Last part is the file path
                    current_commit.files.append(FileChange(
                        path=file_path,
                        change_type=change_type
                    ))

        # Don't forget the last commit
        if current_commit:
            commits.append(current_commit)

        return commits

    except Exception as e:
        print(f"Error getting commits: {e}")
        return []


def get_file_history(path: Path, file_path: str, max_commits: int = 10) -> List[Commit]:
    """
    Get commit history for a specific file.

    Args:
        path: Path inside the git repository
        file_path: Path to the file (relative to repo root)
        max_commits: Maximum number of commits to return

    Returns:
        List of Commit objects that touched this file
    """
    if not is_git_repo(path):
        return []

    try:
        result = subprocess.run(
            [
                "git", "log",
                f"-n{max_commits}",
                "--pretty=format:%H|%h|%s|%an|%aI",
                "--follow",
                "--", file_path
            ],
            cwd=str(path),
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return []

        commits = []
        for line in result.stdout.split("\n"):
            line = line.strip()
            if not line or "|" not in line:
                continue

            parts = line.split("|")
            if len(parts) == 5:
                commits.append(Commit(
                    hash=parts[0],
                    short_hash=parts[1],
                    message=parts[2],
                    author=parts[3],
                    date=datetime.fromisoformat(parts[4]),
                    files=[FileChange(path=file_path, change_type="M")]
                ))

        return commits

    except Exception:
        return []


def get_changed_files(path: Path, days: int = 7) -> Dict[str, List[Commit]]:
    """
    Get a mapping of changed files to their commits.

    Args:
        path: Path inside the git repository
        days: Number of days to look back

    Returns:
        Dict mapping file paths to list of commits that changed them
    """
    commits = get_recent_commits(path, days=days)

    file_commits: Dict[str, List[Commit]] = {}

    for commit in commits:
        for file_change in commit.files:
            if file_change.path not in file_commits:
                file_commits[file_change.path] = []
            file_commits[file_change.path].append(commit)

    return file_commits


def get_diff_summary(path: Path, commit_hash: str) -> str:
    """
    Get a summary of changes in a commit.

    Args:
        path: Path inside the git repository
        commit_hash: The commit hash

    Returns:
        String summary of the diff
    """
    try:
        result = subprocess.run(
            ["git", "show", "--stat", commit_hash],
            cwd=str(path),
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return result.stdout
    except Exception:
        pass

    return ""


def format_commit_summary(commits: List[Commit], include_files: bool = True) -> str:
    """
    Format commits into a human-readable summary.

    Args:
        commits: List of commits to format
        include_files: Whether to include file lists

    Returns:
        Formatted string
    """
    if not commits:
        return "No recent changes found."

    lines = []

    for commit in commits:
        # Calculate relative time
        delta = datetime.now() - commit.date.replace(tzinfo=None)
        if delta.days > 0:
            time_str = f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            time_str = f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            minutes = delta.seconds // 60
            time_str = f"{minutes} minute{'s' if minutes > 1 else ''} ago"

        lines.append(f"• {commit.message} ({time_str})")
        lines.append(f"  by {commit.author} [{commit.short_hash}]")

        if include_files and commit.files:
            for f in commit.files[:5]:  # Limit to 5 files
                change_symbol = {"A": "+", "M": "~", "D": "-", "R": "→"}.get(f.change_type, "?")
                lines.append(f"    {change_symbol} {f.path}")
            if len(commit.files) > 5:
                lines.append(f"    ... and {len(commit.files) - 5} more files")

        lines.append("")

    return "\n".join(lines)


def get_activity_summary(path: Path, days: int = 7) -> str:
    """
    Get a summary of recent repository activity.

    Args:
        path: Path inside the git repository
        days: Number of days to look back

    Returns:
        Human-readable activity summary
    """
    if not is_git_repo(path):
        return "Not a git repository."

    commits = get_recent_commits(path, days=days)

    if not commits:
        return f"No commits in the last {days} days."

    # Count stats
    total_commits = len(commits)
    authors = set(c.author for c in commits)
    all_files = set()
    for c in commits:
        for f in c.files:
            all_files.add(f.path)

    summary = [
        f"Activity in the last {days} days:",
        f"  • {total_commits} commit{'s' if total_commits > 1 else ''}",
        f"  • {len(all_files)} file{'s' if len(all_files) > 1 else ''} changed",
        f"  • {len(authors)} contributor{'s' if len(authors) > 1 else ''}",
        "",
        "Recent commits:",
        format_commit_summary(commits[:10], include_files=True)
    ]

    return "\n".join(summary)


if __name__ == "__main__":
    # Test the module
    import sys

    test_path = Path.cwd()
    if len(sys.argv) > 1:
        test_path = Path(sys.argv[1])

    print(f"Testing git utils on: {test_path}\n")
    print(get_activity_summary(test_path, days=7))
