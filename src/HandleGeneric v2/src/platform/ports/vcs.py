"""Version control system ports."""

from typing import Protocol, List, Optional
from pathlib import Path
from pydantic import BaseModel


class GitCommit(BaseModel):
    """Git commit information."""

    hash: str
    message: str
    author: str
    date: str
    files_changed: List[str]


class GitReader(Protocol):
    """Read operations for Git repositories."""

    def get_current_branch(self, repo_path: Path) -> str:
        """Get the current Git branch."""
        ...

    def get_recent_commits(
        self, repo_path: Path, count: int = 10, since: Optional[str] = None
    ) -> List[GitCommit]:
        """Get recent commits."""
        ...

    def get_changed_files(self, repo_path: Path, since_commit: Optional[str] = None) -> List[Path]:
        """Get files changed since a commit."""
        ...

    def is_repo(self, path: Path) -> bool:
        """Check if path is a Git repository."""
        ...


class CommitWriter(Protocol):
    """Write operations for Git repositories."""

    def stage_files(self, repo_path: Path, files: List[Path]) -> None:
        """Stage files for commit."""
        ...

    def commit(self, repo_path: Path, message: str, author: Optional[str] = None) -> str:
        """Create a commit and return the commit hash."""
        ...
