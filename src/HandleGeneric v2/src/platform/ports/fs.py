"""File system related ports."""

from typing import Protocol, List, Iterator, Optional
from pathlib import Path
from platform.domain.models.generation import GeneratedFile


class FileSystem(Protocol):
    """File system operations."""

    def read_text(self, path: Path, encoding: str = "utf-8") -> str:
        """Read text content from a file."""
        ...

    def write_text(self, path: Path, content: str, encoding: str = "utf-8") -> None:
        """Write text content to a file."""
        ...

    def exists(self, path: Path) -> bool:
        """Check if a path exists."""
        ...

    def is_file(self, path: Path) -> bool:
        """Check if path is a file."""
        ...

    def is_dir(self, path: Path) -> bool:
        """Check if path is a directory."""
        ...

    def mkdir(self, path: Path, parents: bool = True, exist_ok: bool = True) -> None:
        """Create a directory."""
        ...

    def scan(
        self,
        root: Path,
        include_exts: Optional[set[str]] = None,
        exclude_dirs: Optional[set[str]] = None,
        max_size_mb: Optional[int] = None,
    ) -> List[Path]:
        """Scan directory for files matching criteria."""
        ...

    def get_size_mb(self, path: Path) -> float:
        """Get file size in MB."""
        ...


class ArtifactWriter(Protocol):
    """Writer for generated code artifacts."""

    def write(self, root: Path, files: List[GeneratedFile]) -> None:
        """Write generated files to the specified root directory."""
        ...

    def write_report(self, root: Path, report: dict) -> Path:
        """Write a generation report to the root directory."""
        ...
