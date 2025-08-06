"""
Tests for HandleGeneric file utility functions.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from HandleGeneric.utils.file_utils import (
    ensure_directory,
    get_files_by_extension,
    copy_file_with_backup,
    get_file_size_mb,
    is_binary_file,
    get_relative_path,
)


class TestFileUtils:
    """Test cases for file utility functions."""

    def test_ensure_directory_new(self):
        """Test creating a new directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / "new_directory"

            ensure_directory(new_dir)

            assert new_dir.exists()
            assert new_dir.is_dir()

    def test_ensure_directory_existing(self):
        """Test ensuring an existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            existing_dir = Path(temp_dir)

            # Should not raise an exception
            ensure_directory(existing_dir)

            assert existing_dir.exists()
            assert existing_dir.is_dir()

    def test_ensure_directory_nested(self):
        """Test creating nested directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_dir = Path(temp_dir) / "level1" / "level2" / "level3"

            ensure_directory(nested_dir)

            assert nested_dir.exists()
            assert nested_dir.is_dir()

    def test_get_files_by_extension(self):
        """Test getting files by extension."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "test1.py").touch()
            (temp_path / "test2.py").touch()
            (temp_path / "test3.js").touch()
            (temp_path / "test4.txt").touch()

            # Get Python files
            py_files = get_files_by_extension(temp_path, [".py"])
            assert len(py_files) == 2
            assert all(f.suffix == ".py" for f in py_files)

            # Get JavaScript files
            js_files = get_files_by_extension(temp_path, [".js"])
            assert len(js_files) == 1
            assert all(f.suffix == ".js" for f in js_files)

            # Get multiple extensions
            code_files = get_files_by_extension(temp_path, [".py", ".js"])
            assert len(code_files) == 3

    def test_get_files_by_extension_recursive(self):
        """Test getting files by extension recursively."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create nested structure
            (temp_path / "subdir").mkdir()
            (temp_path / "test1.py").touch()
            (temp_path / "subdir" / "test2.py").touch()
            (temp_path / "subdir" / "test3.js").touch()

            # Get Python files recursively
            py_files = get_files_by_extension(temp_path, [".py"])
            assert len(py_files) == 2

    def test_copy_file_with_backup_new_destination(self):
        """Test copying file to new destination."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create source file
            source_file = temp_path / "source.txt"
            source_file.write_text("test content")

            # Copy to new destination
            dest_file = temp_path / "dest.txt"
            copy_file_with_backup(source_file, dest_file)

            assert dest_file.exists()
            assert dest_file.read_text() == "test content"

    def test_copy_file_with_backup_existing_destination(self):
        """Test copying file with backup of existing destination."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create source file
            source_file = temp_path / "source.txt"
            source_file.write_text("new content")

            # Create existing destination file
            dest_file = temp_path / "dest.txt"
            dest_file.write_text("old content")

            # Copy with backup
            copy_file_with_backup(source_file, dest_file)

            assert dest_file.exists()
            assert dest_file.read_text() == "new content"

            # Check backup was created
            backup_file = temp_path / "dest.txt.backup"
            assert backup_file.exists()
            assert backup_file.read_text() == "old content"

    def test_get_file_size_mb(self):
        """Test getting file size in MB."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a file with known content
            test_file = temp_path / "test.txt"
            test_file.write_text("test content")

            size_mb = get_file_size_mb(test_file)

            assert isinstance(size_mb, float)
            assert size_mb > 0

    def test_is_binary_file_text(self):
        """Test detecting text file as non-binary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create text file
            text_file = temp_path / "text.txt"
            text_file.write_text("This is text content")

            assert is_binary_file(text_file) is False

    def test_is_binary_file_binary(self):
        """Test detecting binary file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create binary file
            binary_file = temp_path / "binary.bin"
            with open(binary_file, "wb") as f:
                f.write(b"\x00\x01\x02\x03\x04")

            assert is_binary_file(binary_file) is True

    def test_get_relative_path_success(self):
        """Test getting relative path successfully."""
        base_path = Path("/base/path")
        file_path = Path("/base/path/subdir/file.txt")

        relative = get_relative_path(file_path, base_path)

        assert relative == "subdir/file.txt"

    def test_get_relative_path_fallback(self):
        """Test getting relative path with fallback."""
        base_path = Path("/base/path")
        file_path = Path("/different/path/file.txt")

        relative = get_relative_path(file_path, base_path)

        assert relative == str(file_path)

    def test_get_relative_path_same_level(self):
        """Test getting relative path at same level."""
        base_path = Path("/base/path")
        file_path = Path("/base/path/file.txt")

        relative = get_relative_path(file_path, base_path)

        assert relative == "file.txt"
