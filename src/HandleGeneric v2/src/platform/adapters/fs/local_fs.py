"""Local file system adapter."""

from typing import List, Optional
from pathlib import Path
from platform.ports.fs import FileSystem
from platform.kernel.logging import get_logger

logger = get_logger(__name__)


class LocalFileSystem:
    """Local file system implementation."""

    def read_text(self, path: Path, encoding: str = "utf-8") -> str:
        """Read text content from a file."""
        try:
            return path.read_text(encoding=encoding)
        except Exception as e:
            logger.error("Failed to read file", path=str(path), error=str(e))
            raise

    def write_text(self, path: Path, content: str, encoding: str = "utf-8") -> None:
        """Write text content to a file."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding=encoding)
            logger.debug("File written", path=str(path), size=len(content))
        except Exception as e:
            logger.error("Failed to write file", path=str(path), error=str(e))
            raise

    def exists(self, path: Path) -> bool:
        """Check if a path exists."""
        return path.exists()

    def is_file(self, path: Path) -> bool:
        """Check if path is a file."""
        return path.is_file()

    def is_dir(self, path: Path) -> bool:
        """Check if path is a directory."""
        return path.is_dir()

    def mkdir(self, path: Path, parents: bool = True, exist_ok: bool = True) -> None:
        """Create a directory."""
        try:
            path.mkdir(parents=parents, exist_ok=exist_ok)
            logger.debug("Directory created", path=str(path))
        except Exception as e:
            logger.error("Failed to create directory", path=str(path), error=str(e))
            raise

    def scan(
        self,
        root: Path,
        include_exts: Optional[set[str]] = None,
        exclude_dirs: Optional[set[str]] = None,
        max_size_mb: Optional[int] = None,
    ) -> List[Path]:
        """Scan directory for files matching criteria."""
        files = []
        exclude_dirs = exclude_dirs or set()

        try:
            for path in root.rglob("*"):
                # Skip directories
                if not path.is_file():
                    continue

                # Skip excluded directories
                if any(excluded in str(path) for excluded in exclude_dirs):
                    continue

                # Check file extension
                if include_exts and path.suffix not in include_exts:
                    continue

                # Check file size
                if max_size_mb:
                    size_mb = self.get_size_mb(path)
                    if size_mb > max_size_mb:
                        logger.warning("Skipping large file", path=str(path), size_mb=size_mb)
                        continue

                files.append(path)

            logger.info("File scan completed", root=str(root), files_found=len(files))
            return files

        except Exception as e:
            logger.error("Failed to scan directory", root=str(root), error=str(e))
            raise

    def get_size_mb(self, path: Path) -> float:
        """Get file size in MB."""
        try:
            size_bytes = path.stat().st_size
            return size_bytes / (1024 * 1024)
        except Exception as e:
            logger.error("Failed to get file size", path=str(path), error=str(e))
            return 0.0
