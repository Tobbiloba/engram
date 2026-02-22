#!/usr/bin/env python3
"""
Temporal Memory for Engram - Smart time-aware search.

Works with ANY folder - git is optional enhancement.
Tracks file changes independently using modification times.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

# Git utils are optional
try:
    from engram.git_utils import (
        is_git_repo,
        get_repo_root,
        get_recent_commits,
        get_changed_files,
        get_activity_summary,
        format_commit_summary,
        Commit
    )
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    Commit = None


@dataclass
class FileChange:
    """Represents a file change."""
    path: str
    change_type: str  # 'added', 'modified', 'deleted'
    old_mtime: Optional[float] = None
    new_mtime: Optional[float] = None
    size_bytes: int = 0

    @property
    def changed_at(self) -> datetime:
        if self.new_mtime:
            return datetime.fromtimestamp(self.new_mtime)
        return datetime.now()

    @property
    def time_ago(self) -> str:
        delta = datetime.now() - self.changed_at
        if delta.days > 0:
            return f"{delta.days} days ago"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600} hours ago"
        elif delta.seconds > 60:
            return f"{delta.seconds // 60} minutes ago"
        return "just now"


@dataclass
class TemporalResult:
    """A search result with temporal context."""
    content: str
    source_file: str
    relevance_score: float
    last_modified: Optional[datetime] = None
    recent_commits: List = field(default_factory=list)
    is_recently_changed: bool = False


class FileRegistry:
    """
    Tracks file states for change detection.
    Works without git - stores modification times.
    """

    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        self.files: Dict[str, dict] = {}
        self.load()

    def load(self):
        """Load registry from disk."""
        if self.registry_path.exists():
            try:
                self.files = json.loads(self.registry_path.read_text())
            except:
                self.files = {}

    def save(self):
        """Save registry to disk."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(json.dumps(self.files, indent=2))

    def update_file(self, file_path: Path):
        """Update registry with current file state."""
        try:
            stat = file_path.stat()
            self.files[str(file_path)] = {
                "mtime": stat.st_mtime,
                "size": stat.st_size,
                "indexed_at": datetime.now().isoformat()
            }
        except:
            pass

    def get_changes(self, folder: Path, days: int = 7) -> List[FileChange]:
        """
        Find files that changed since last index.

        Returns list of FileChange objects for:
        - New files (not in registry)
        - Modified files (mtime changed)
        - Deleted files (in registry but not on disk)
        """
        changes = []
        cutoff = datetime.now() - timedelta(days=days)
        current_files = set()

        # Walk the folder
        for root, dirs, files in os.walk(folder):
            # Skip hidden and common excludes
            dirs[:] = [d for d in dirs if not d.startswith('.')
                      and d not in {'node_modules', '__pycache__', 'venv', '.venv'}]

            for filename in files:
                if filename.startswith('.'):
                    continue

                file_path = Path(root) / filename
                current_files.add(str(file_path))

                try:
                    stat = file_path.stat()
                    mtime = stat.st_mtime
                    modified_at = datetime.fromtimestamp(mtime)

                    # Skip if older than cutoff
                    if modified_at < cutoff:
                        continue

                    stored = self.files.get(str(file_path))

                    if stored is None:
                        # New file
                        changes.append(FileChange(
                            path=str(file_path),
                            change_type='added',
                            new_mtime=mtime,
                            size_bytes=stat.st_size
                        ))
                    elif stored.get('mtime', 0) < mtime:
                        # Modified file
                        changes.append(FileChange(
                            path=str(file_path),
                            change_type='modified',
                            old_mtime=stored.get('mtime'),
                            new_mtime=mtime,
                            size_bytes=stat.st_size
                        ))
                except:
                    continue

        # Check for deleted files
        for stored_path in self.files:
            if stored_path not in current_files:
                stored = self.files[stored_path]
                stored_time = datetime.fromisoformat(stored.get('indexed_at', datetime.now().isoformat()))
                if stored_time > cutoff:
                    changes.append(FileChange(
                        path=stored_path,
                        change_type='deleted',
                        old_mtime=stored.get('mtime')
                    ))

        # Sort by most recent first
        changes.sort(key=lambda c: c.new_mtime or c.old_mtime or 0, reverse=True)
        return changes


class TemporalMemory:
    """
    Temporal Memory layer for Engram.

    Tracks changes using file modification times.
    Git integration is optional - adds commit messages when available.
    """

    def __init__(self, engram_path: Path, source_path: Optional[Path] = None):
        """
        Initialize Temporal Memory.

        Args:
            engram_path: Path to the engram index folder
            source_path: Path to the original source folder (for change detection)
        """
        self.engram_path = Path(engram_path)
        self.source_path = Path(source_path) if source_path else None

        # File-based change tracking
        self.registry = FileRegistry(self.engram_path / "file_registry.json")

        # Check if git is available for this path
        self.has_git = False
        self.repo_root = None
        if GIT_AVAILABLE and self.source_path:
            self.has_git = is_git_repo(self.source_path)
            if self.has_git:
                self.repo_root = get_repo_root(self.source_path)

    def whats_changed(self, days: int = 7) -> str:
        """
        Get a summary of what changed recently.
        Works with or without git.
        """
        if not self.source_path:
            return "No source path configured for change tracking."

        lines = []
        lines.append(f"Changes in the last {days} days:\n")

        # Get file-based changes
        changes = self.registry.get_changes(self.source_path, days)

        if not changes:
            lines.append("No changes detected.")

            # If git available, also show git activity
            if self.has_git:
                git_summary = get_activity_summary(self.source_path, days)
                if git_summary:
                    lines.append(f"\nGit activity:\n{git_summary}")

            return "\n".join(lines)

        # Group by change type
        added = [c for c in changes if c.change_type == 'added']
        modified = [c for c in changes if c.change_type == 'modified']
        deleted = [c for c in changes if c.change_type == 'deleted']

        if added:
            lines.append(f"\n📁 Added ({len(added)} files):")
            for c in added[:10]:
                lines.append(f"  + {Path(c.path).name} ({c.time_ago})")
            if len(added) > 10:
                lines.append(f"  ... and {len(added) - 10} more")

        if modified:
            lines.append(f"\n✏️ Modified ({len(modified)} files):")
            for c in modified[:10]:
                lines.append(f"  ~ {Path(c.path).name} ({c.time_ago})")
            if len(modified) > 10:
                lines.append(f"  ... and {len(modified) - 10} more")

        if deleted:
            lines.append(f"\n🗑️ Deleted ({len(deleted)} files):")
            for c in deleted[:5]:
                lines.append(f"  - {Path(c.path).name}")

        # Add git context if available
        if self.has_git:
            lines.append("\n📝 Git commits:")
            commits = get_recent_commits(self.source_path, days, max_commits=5)
            for commit in commits:
                lines.append(f"  • {commit.message[:60]} ({commit.author})")

        lines.append(f"\nTotal: {len(changes)} changes")
        return "\n".join(lines)

    def explain_file(self, file_path: str) -> str:
        """
        Explain the recent history of a file.
        Shows modification time and git history if available.
        """
        path = Path(file_path)

        # Try to resolve relative to source
        if not path.is_absolute() and self.source_path:
            path = self.source_path / path

        if not path.exists():
            return f"File not found: {file_path}"

        lines = []
        lines.append(f"File: {path.name}")
        lines.append(f"Path: {path}")

        # Basic file info
        try:
            stat = path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)
            size_kb = stat.st_size / 1024
            lines.append(f"Size: {size_kb:.1f} KB")
            lines.append(f"Last modified: {mtime.strftime('%Y-%m-%d %H:%M')}")
        except:
            pass

        # Check registry for when it was indexed
        stored = self.registry.files.get(str(path))
        if stored:
            indexed_at = stored.get('indexed_at', 'Unknown')
            lines.append(f"Indexed at: {indexed_at}")

        # Git history if available
        if self.has_git:
            lines.append("\nGit history:")
            try:
                file_changes = get_changed_files(self.source_path, days=30)
                rel_path = str(path.relative_to(self.repo_root))

                if rel_path in file_changes:
                    commits = file_changes[rel_path]
                    for commit in commits[:5]:
                        lines.append(f"  • {commit.date.strftime('%m/%d')} - {commit.message[:50]}")
                else:
                    lines.append("  No recent commits for this file")
            except:
                lines.append("  Could not read git history")

        return "\n".join(lines)

    def query_recent(self, query: str, vector_store, days: int = 7, k: int = 5) -> List[TemporalResult]:
        """
        Search with time awareness - boost recently changed files.
        """
        # Get base results from vector search
        results = vector_store.similarity_search_with_score(query, k=k*2)

        # Get recent changes
        recent_files = set()
        if self.source_path:
            changes = self.registry.get_changes(self.source_path, days)
            recent_files = {c.path for c in changes}

        temporal_results = []
        for doc, score in results:
            source = doc.metadata.get('source_file', '')

            # Check if recently changed
            is_recent = source in recent_files or any(
                source.endswith(Path(f).name) for f in recent_files
            )

            # Get modification time
            mtime = None
            try:
                mtime = datetime.fromtimestamp(Path(source).stat().st_mtime)
            except:
                pass

            temporal_results.append(TemporalResult(
                content=doc.page_content,
                source_file=source,
                relevance_score=float(score),
                last_modified=mtime,
                is_recently_changed=is_recent
            ))

        # Sort: recent changes first, then by relevance
        temporal_results.sort(
            key=lambda r: (r.is_recently_changed, -r.relevance_score),
            reverse=True
        )

        return temporal_results[:k]

    def get_recent_files(self, days: int = 7) -> List[FileChange]:
        """Get list of recently changed files."""
        if not self.source_path:
            return []
        return self.registry.get_changes(self.source_path, days)
