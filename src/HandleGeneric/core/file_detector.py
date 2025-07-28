"""
File detection utilities for identifying programming languages and project structure.

This module provides utilities for detecting file types, programming languages,
and discovering relevant files in projects.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Generator, Tuple
from collections import defaultdict
import logging

from .language_registry import get_global_registry


class FileDetector:
    """Utility class for detecting file types and programming languages."""

    def __init__(self, exclude_patterns: Optional[List[str]] = None):
        """
        Initialize the file detector.

        Args:
            exclude_patterns: List of patterns to exclude from detection
        """
        self.registry = get_global_registry()
        self.logger = logging.getLogger(__name__)

        # Default exclude patterns
        default_excludes = [
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "__pycache__/*",
            ".pytest_cache/*",
            "node_modules/*",
            ".git/*",
            ".svn/*",
            ".hg/*",
            "*.class",
            "*.jar",
            "*.war",
            "target/*",
            "build/*",
            "bin/*",
            "obj/*",
            "*.exe",
            "*.dll",
            "*.so",
            ".vscode/*",
            ".idea/*",
            "*.log",
            "*.tmp",
            "dist/*",
            ".next/*",
            ".nuxt/*",
            "coverage/*",
        ]

        self.exclude_patterns = exclude_patterns or default_excludes
        self._compile_exclude_patterns()

    def _compile_exclude_patterns(self):
        """Compile exclude patterns for efficient matching."""
        self._exclude_regexes = []
        for pattern in self.exclude_patterns:
            # Convert glob patterns to regex
            regex_pattern = pattern.replace("*", ".*").replace("?", ".")
            if pattern.endswith("/*"):
                regex_pattern = regex_pattern[:-3] + "/.*"
            self._exclude_regexes.append(re.compile(regex_pattern))

    def should_exclude_file(self, file_path: Path) -> bool:
        """
        Check if a file should be excluded based on patterns.

        Args:
            file_path: Path to check

        Returns:
            True if file should be excluded
        """
        path_str = str(file_path)

        for regex in self._exclude_regexes:
            if regex.search(path_str):
                return True

        return False

    def detect_language(self, file_path: Path) -> Optional[str]:
        """
        Detect the programming language of a file.

        Args:
            file_path: Path to the file

        Returns:
            Language name or None if not detected
        """
        return self.registry.detect_language(file_path)

    def find_project_files(
        self, project_path: Path, languages: Optional[List[str]] = None
    ) -> Dict[str, List[Path]]:
        """
        Find all relevant source files in a project, grouped by language.

        Args:
            project_path: Root path of the project
            languages: Optional list of languages to filter by

        Returns:
            Dictionary mapping language names to lists of file paths
        """
        if not project_path.exists() or not project_path.is_dir():
            self.logger.error(
                f"Project path does not exist or is not a directory: {project_path}"
            )
            return {}

        files_by_language = defaultdict(list)

        for file_path in self._walk_directory(project_path):
            if self.should_exclude_file(file_path):
                continue

            language = self.detect_language(file_path)
            if language and (not languages or language in languages):
                files_by_language[language].append(file_path)

        # Convert defaultdict to regular dict
        result = dict(files_by_language)

        self.logger.info(
            f"Found files in {len(result)} languages: {list(result.keys())}"
        )
        for lang, files in result.items():
            self.logger.debug(f"  {lang}: {len(files)} files")

        return result

    def find_files_by_language(self, project_path: Path, language: str) -> List[Path]:
        """
        Find all files for a specific language in a project.

        Args:
            project_path: Root path of the project
            language: Programming language to search for

        Returns:
            List of file paths for the specified language
        """
        files_by_language = self.find_project_files(project_path, [language])
        return files_by_language.get(language, [])

    def analyze_project_structure(self, project_path: Path) -> Dict[str, any]:
        """
        Analyze the overall structure of a project.

        Args:
            project_path: Root path of the project

        Returns:
            Dictionary with project analysis
        """
        files_by_language = self.find_project_files(project_path)

        total_files = sum(len(files) for files in files_by_language.values())

        # Calculate lines of code per language
        lines_by_language = {}
        for language, files in files_by_language.items():
            total_lines = 0
            for file_path in files:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        total_lines += len(f.readlines())
                except Exception as e:
                    self.logger.warning(f"Could not read file {file_path}: {e}")
            lines_by_language[language] = total_lines

        # Detect main language (most lines of code)
        main_language = (
            max(lines_by_language.items(), key=lambda x: x[1])[0]
            if lines_by_language
            else None
        )

        return {
            "total_files": total_files,
            "languages": list(files_by_language.keys()),
            "main_language": main_language,
            "files_by_language": {
                lang: len(files) for lang, files in files_by_language.items()
            },
            "lines_by_language": lines_by_language,
            "project_type": self._detect_project_type(project_path, files_by_language),
        }

    def _detect_project_type(
        self, project_path: Path, files_by_language: Dict[str, List[Path]]
    ) -> str:
        """
        Detect the type of project based on files and structure.

        Args:
            project_path: Project root path
            files_by_language: Files grouped by language

        Returns:
            Project type string
        """
        # Check for common project files
        project_files = list(project_path.glob("*"))
        project_file_names = [f.name.lower() for f in project_files]

        # Web projects
        if any(
            name in project_file_names
            for name in ["package.json", "yarn.lock", "webpack.config.js"]
        ):
            return "web"

        # Python projects
        if any(
            name in project_file_names
            for name in ["setup.py", "pyproject.toml", "requirements.txt"]
        ):
            return "python"

        # Java projects
        if any(
            name in project_file_names
            for name in ["pom.xml", "build.gradle", "gradle.properties"]
        ):
            return "java"

        # .NET projects
        if any(
            name.endswith((".csproj", ".sln", ".vbproj")) for name in project_file_names
        ):
            return "dotnet"

        # Default based on main language
        if files_by_language:
            main_lang = max(files_by_language.items(), key=lambda x: len(x[1]))[0]
            return main_lang

        return "unknown"

    def _walk_directory(self, directory: Path) -> Generator[Path, None, None]:
        """
        Walk through directory and yield file paths.

        Args:
            directory: Directory to walk

        Yields:
            File paths
        """
        try:
            for root, dirs, files in os.walk(directory):
                # Modify dirs in-place to skip excluded directories
                dirs[:] = [
                    d for d in dirs if not self._should_exclude_dir(Path(root) / d)
                ]

                for file in files:
                    file_path = Path(root) / file
                    if file_path.is_file():
                        yield file_path
        except Exception as e:
            self.logger.error(f"Error walking directory {directory}: {e}")

    def _should_exclude_dir(self, dir_path: Path) -> bool:
        """
        Check if a directory should be excluded.

        Args:
            dir_path: Directory path to check

        Returns:
            True if directory should be excluded
        """
        dir_name = dir_path.name

        # Common directories to exclude
        exclude_dirs = {
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".git",
            ".svn",
            ".hg",
            "target",
            "build",
            "bin",
            "obj",
            ".vscode",
            ".idea",
            "dist",
            ".next",
            ".nuxt",
            "coverage",
        }

        return dir_name in exclude_dirs or self.should_exclude_file(dir_path)
