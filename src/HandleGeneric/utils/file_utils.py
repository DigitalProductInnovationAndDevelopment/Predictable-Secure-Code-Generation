"""
File utility functions for HandleGeneric.

This module contains utility functions for file operations.
"""

import os
import shutil
from pathlib import Path
from typing import List, Set, Optional


def ensure_directory(path: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Path to the directory
    """
    path.mkdir(parents=True, exist_ok=True)


def get_files_by_extension(directory: Path, extensions: List[str]) -> List[Path]:
    """
    Get all files in a directory with specified extensions.

    Args:
        directory: Directory to search
        extensions: List of file extensions to include

    Returns:
        List of file paths
    """
    files = []
    for ext in extensions:
        files.extend(directory.glob(f"**/*{ext}"))
    return files


def copy_file_with_backup(source: Path, destination: Path) -> None:
    """
    Copy a file with backup if destination exists.

    Args:
        source: Source file path
        destination: Destination file path
    """
    if destination.exists():
        backup_path = destination.with_suffix(destination.suffix + ".backup")
        shutil.copy2(destination, backup_path)

    shutil.copy2(source, destination)


def get_file_size_mb(file_path: Path) -> float:
    """
    Get file size in megabytes.

    Args:
        file_path: Path to the file

    Returns:
        File size in MB
    """
    return file_path.stat().st_size / (1024 * 1024)


def is_binary_file(file_path: Path) -> bool:
    """
    Check if a file is binary.

    Args:
        file_path: Path to the file

    Returns:
        True if binary, False otherwise
    """
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            return b"\x00" in chunk
    except Exception:
        return False


def get_relative_path(file_path: Path, base_path: Path) -> str:
    """
    Get relative path from base path.

    Args:
        file_path: Path to the file
        base_path: Base path

    Returns:
        Relative path as string
    """
    try:
        return str(file_path.relative_to(base_path))
    except ValueError:
        return str(file_path)
