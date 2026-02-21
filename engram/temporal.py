#!/usr/bin/env python3
"""
Temporal Memory for Engram - Smart time-aware search.

Combines semantic search with git history for context-aware results.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from engram.git_utils import (
    is_git_repo,
    get_repo_root,
    get_recent_commits,
    get_changed_files,
    get_activity_summary,
    format_commit_summary,
    Commit
)


@dataclass
class TemporalResult:
    """A search result with temporal context."""
    content: str
    source_file: str
    relevance_score: float
    last_modified: Optional[datetime] = None
    recent_commits: List[Commit] = None
    is_recently_changed: bool = False

    def __post_init__(self):
        if self.recent_commits is None:
            self.recent_commits = []


class TemporalMemory:
    """
    Temporal Memory layer for Engram.

    Adds time-awareness to semantic search by integrating
    git history and file modification times.
    """

    def __init__(self, engram_path: Path, repo_path: Optional[Path] = None):
        """
        Initialize Temporal Memory.

        Args:
            engram_path: Path to the engram index
            repo_path: Path to the git repository (auto-detected if None)
        """
        self.engram_path = Path(engram_path)
        self.repo_path = repo_path
        self.registry_path = self.engram_path / "registry.json"
        self.registry = self._load_registry()

        # Auto-detect repo path from indexed files
        if self.repo_path is None:
            self.repo_path = self._detect_repo_path()

    def _load_registry(self) -> Dict:
        """Load the file registry."""
        if self.registry_path.exists():
            try:
                return json.loads(self.registry_path.read_text())
            except Exception:
                pass
        return {}

    def _detect_repo_path(self) -> Optional[Path]:
        """Try to detect the git repo from indexed files."""
        for file_path in list(self.registry.keys())[:10]:
            path = Path(file_path)
            if path.exists():
                root = get_repo_root(path.parent)
                if root:
                    return root
        return None

    def get_recently_changed_files(self, days: int = 7) -> Dict[str, List[Commit]]:
        """
        Get files that changed recently with their commit info.

        Args:
            days: Number of days to look back

        Returns:
            Dict mapping file paths to their commits
        """
        if not self.repo_path or not is_git_repo(self.repo_path):
            return {}

        return get_changed_files(self.repo_path, days=days)

    def query_recent(
        self,
        query: str,
        vector_store,
        days: int = 7,
        k: int = 5
    ) -> List[TemporalResult]:
        """
        Search with time awareness - prioritizes recently changed files.

        Args:
            query: The search query
            vector_store: The FAISS vector store
            days: Number of days to look back for "recent"
            k: Number of results to return

        Returns:
            List of TemporalResult objects
        """
        # Get semantic search results
        results = vector_store.similarity_search_with_score(query, k=k * 2)

        # Get recently changed files
        recent_changes = self.get_recently_changed_files(days=days)

        temporal_results = []

        for doc, score in results:
            source_file = doc.metadata.get("source_file", "")
            source_path = Path(source_file)

            # Check if file was recently changed
            relative_path = None
            commits = []

            if self.repo_path and source_path.exists():
                try:
                    relative_path = str(source_path.relative_to(self.repo_path))
                    commits = recent_changes.get(relative_path, [])
                except ValueError:
                    pass

            # Get file modification time
            last_modified = None
            if source_path.exists():
                last_modified = datetime.fromtimestamp(source_path.stat().st_mtime)

            temporal_results.append(TemporalResult(
                content=doc.page_content,
                source_file=source_file,
                relevance_score=float(score),
                last_modified=last_modified,
                recent_commits=commits,
                is_recently_changed=len(commits) > 0
            ))

        # Sort by: recently changed first, then by relevance
        temporal_results.sort(
            key=lambda r: (
                -int(r.is_recently_changed),  # Recently changed first
                r.relevance_score  # Then by relevance (lower is better for FAISS)
            )
        )

        return temporal_results[:k]

    def whats_changed(self, days: int = 7) -> str:
        """
        Get a summary of what changed recently.

        Args:
            days: Number of days to look back

        Returns:
            Human-readable summary
        """
        if not self.repo_path or not is_git_repo(self.repo_path):
            return "No git repository detected. Cannot track changes."

        return get_activity_summary(self.repo_path, days=days)

    def explain_file(self, file_path: str) -> str:
        """
        Explain the recent history of a file.

        Args:
            file_path: Path to the file

        Returns:
            Human-readable explanation
        """
        path = Path(file_path)

        if not path.exists():
            return f"File not found: {file_path}"

        if not self.repo_path or not is_git_repo(self.repo_path):
            # Just return basic file info
            stat = path.stat()
            modified = datetime.fromtimestamp(stat.st_mtime)
            return f"File: {path.name}\nLast modified: {modified.strftime('%Y-%m-%d %H:%M')}\nSize: {stat.st_size} bytes"

        # Get git history
        from engram.git_utils import get_file_history

        try:
            relative_path = str(path.relative_to(self.repo_path))
        except ValueError:
            relative_path = str(path)

        commits = get_file_history(self.repo_path, relative_path, max_commits=10)

        if not commits:
            return f"File: {path.name}\nNo git history found."

        lines = [
            f"File: {path.name}",
            f"Path: {relative_path}",
            "",
            "Recent changes:",
            format_commit_summary(commits, include_files=False)
        ]

        return "\n".join(lines)


def format_temporal_results(results: List[TemporalResult]) -> str:
    """
    Format temporal results for display.

    Args:
        results: List of TemporalResult objects

    Returns:
        Formatted string
    """
    if not results:
        return "No results found."

    lines = []

    for i, result in enumerate(results, 1):
        source_name = Path(result.source_file).name

        # Header
        if result.is_recently_changed:
            lines.append(f"[{i}] {source_name} (recently changed)")
        else:
            lines.append(f"[{i}] {source_name}")

        # Content preview
        content = result.content[:300].replace("\n", " ")
        if len(result.content) > 300:
            content += "..."
        lines.append(f"    {content}")

        # Recent commits
        if result.recent_commits:
            lines.append("")
            lines.append("    Recent changes:")
            for commit in result.recent_commits[:3]:
                delta = datetime.now() - commit.date.replace(tzinfo=None)
                if delta.days > 0:
                    time_str = f"{delta.days}d ago"
                else:
                    hours = delta.seconds // 3600
                    time_str = f"{hours}h ago" if hours > 0 else "just now"
                lines.append(f"      • {commit.message} ({time_str})")

        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    # Test the module
    import sys

    if len(sys.argv) < 2:
        print("Usage: python temporal.py <engram_path> [query]")
        sys.exit(1)

    engram_path = Path(sys.argv[1])

    tm = TemporalMemory(engram_path)

    if len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        print(f"Query: {query}\n")
        # Would need vector store to actually search
        print("(Semantic search requires vector store)")
    else:
        print(tm.whats_changed(days=7))
