"""
Helper utilities for file operations and path handling.
"""

import os
import json
import fnmatch
from pathlib import Path
from typing import List, Generator, Dict, Any, Optional
import logging


class PathHelper:
    """Helper class for path operations."""

    @staticmethod
    def normalize_path(path: str) -> Path:
        """
        Normalize a path to a Path object.

        Args:
            path: String path to normalize

        Returns:
            Normalized Path object
        """
        return Path(path).resolve()

    @staticmethod
    def is_python_file(file_path: Path) -> bool:
        """
        Check if a file is a Python file.

        Args:
            file_path: Path to check

        Returns:
            True if file is a Python file
        """
        return file_path.suffix == ".py"

    @staticmethod
    def matches_pattern(file_path: Path, patterns: List[str]) -> bool:
        """
        Check if a file path matches any of the given patterns.

        Args:
            file_path: Path to check
            patterns: List of glob patterns

        Returns:
            True if path matches any pattern
        """
        path_str = str(file_path)
        return any(fnmatch.fnmatch(path_str, pattern) for pattern in patterns)

    @staticmethod
    def get_relative_path(file_path: Path, base_path: Path) -> str:
        """
        Get relative path from base path.

        Args:
            file_path: File path
            base_path: Base directory path

        Returns:
            Relative path as string
        """
        try:
            return str(file_path.relative_to(base_path))
        except ValueError:
            return str(file_path)


class FileHelper:
    """Helper class for file operations."""

    def __init__(self, config=None):
        """
        Initialize FileHelper.

        Args:
            config: Configuration object (optional)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

    def find_python_files(self, project_path: Path) -> Generator[Path, None, None]:
        """
        Find all Python files in a project directory.

        Args:
            project_path: Root directory to search

        Yields:
            Path objects for Python files
        """
        if not project_path.exists():
            self.logger.error(f"Project path does not exist: {project_path}")
            return

        for root, dirs, files in os.walk(project_path):
            root_path = Path(root)

            # Skip excluded directories
            if self.config and self._should_exclude_directory(root_path, project_path):
                dirs.clear()  # Don't recurse into excluded directories
                continue

            for file in files:
                file_path = root_path / file

                if PathHelper.is_python_file(file_path) and self._should_include_file(
                    file_path
                ):
                    yield file_path

    def _should_include_file(self, file_path: Path) -> bool:
        """
        Check if a file should be included based on configuration.

        Args:
            file_path: Path to check

        Returns:
            True if file should be included
        """
        if not self.config:
            return True

        # Check include patterns
        if self.config.include_patterns:
            included = PathHelper.matches_pattern(
                file_path, self.config.include_patterns
            )
            if not included:
                return False

        # Check exclude patterns
        if self.config.exclude_patterns:
            excluded = PathHelper.matches_pattern(
                file_path, self.config.exclude_patterns
            )
            if excluded:
                return False

        return True

    def _should_exclude_directory(self, dir_path: Path, project_path: Path) -> bool:
        """
        Check if a directory should be excluded.

        Args:
            dir_path: Directory path to check
            project_path: Project root path

        Returns:
            True if directory should be excluded
        """
        if not self.config or not self.config.exclude_patterns:
            return False

        relative_path = PathHelper.get_relative_path(dir_path, project_path)
        return PathHelper.matches_pattern(
            Path(relative_path), self.config.exclude_patterns
        )

    def read_file_safely(self, file_path: Path) -> Optional[str]:
        """
        Safely read a file's contents.

        Args:
            file_path: Path to file

        Returns:
            File contents as string or None if error
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except (UnicodeDecodeError, IOError) as e:
            self.logger.warning(f"Could not read file {file_path}: {e}")
            return None

    def save_json(self, data: Dict[str, Any], output_path: Path) -> bool:
        """
        Save data as JSON to file.

        Args:
            data: Data to save
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            indent = self.config.indent_json if self.config else 2
            sort_keys = self.config.sort_keys if self.config else True

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    data, f, indent=indent, sort_keys=sort_keys, ensure_ascii=False
                )

            self.logger.info(f"Metadata saved to: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save metadata to {output_path}: {e}")
            return False

    def ensure_directory_exists(self, directory: Path) -> bool:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            directory: Directory path

        Returns:
            True if directory exists or was created successfully
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create directory {directory}: {e}")
            return False
