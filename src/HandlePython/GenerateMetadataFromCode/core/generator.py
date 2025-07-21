"""
Main metadata generator that orchestrates the entire process.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import time

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.parser import CodeParser
from core.analyzer import CodeAnalyzer
from utils.config import Config
from utils.helpers import FileHelper, PathHelper


class MetadataGenerator:
    """Main class for generating metadata from code projects."""

    def __init__(self, config: Config = None):
        """
        Initialize the metadata generator.

        Args:
            config: Configuration object (optional)
        """
        self.config = config or Config()
        self._setup_logging()
        self.file_helper = FileHelper(self.config)
        self.parser = CodeParser(self.config)
        self.analyzer = CodeAnalyzer(self.config)

        # Validate configuration
        config_errors = self.config.validate()
        if config_errors:
            raise ValueError(f"Configuration errors: {', '.join(config_errors)}")

    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level), format=self.config.log_format
        )
        self.logger = logging.getLogger(__name__)

    def generate_metadata(
        self, project_path: str, output_path: str, filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate metadata for a code project.

        Args:
            project_path: Path to the project directory
            output_path: Path where to save the metadata
            filename: Optional filename for the metadata file

        Returns:
            Generated metadata dictionary
        """
        start_time = time.time()

        # Normalize paths
        project_path = PathHelper.normalize_path(project_path)
        output_path = PathHelper.normalize_path(output_path)

        self.logger.info(f"Starting metadata generation for: {project_path}")

        # Validate project path
        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

        if not project_path.is_dir():
            raise ValueError(f"Project path is not a directory: {project_path}")

        # Ensure output directory exists
        if not self.file_helper.ensure_directory_exists(output_path):
            raise ValueError(f"Cannot create output directory: {output_path}")

        # Find and parse Python files
        self.logger.info("Discovering Python files...")
        python_files = list(self.file_helper.find_python_files(project_path))

        if not python_files:
            self.logger.warning("No Python files found in the project")
            return self._create_empty_metadata(project_path)

        self.logger.info(f"Found {len(python_files)} Python files")

        # Parse files
        self.logger.info("Parsing Python files...")
        parsed_files = []

        for file_path in python_files:
            relative_path = PathHelper.get_relative_path(file_path, project_path)
            self.logger.debug(f"Parsing: {relative_path}")

            content = self.file_helper.read_file_safely(file_path)
            if content is not None:
                parsed_data = self.parser.parse_file(file_path, content)
                # Use relative path for output
                parsed_data["path"] = relative_path
                parsed_files.append(parsed_data)
            else:
                self.logger.warning(f"Skipping unreadable file: {relative_path}")

        # Analyze project
        self.logger.info("Analyzing project structure...")
        analysis_results = self.analyzer.analyze_project(parsed_files, project_path)

        # Create metadata structure
        metadata = self._create_metadata_structure(
            parsed_files, analysis_results, project_path, start_time
        )

        # Save metadata
        output_filename = filename or self.config.output_filename
        output_file_path = output_path / output_filename

        if self.file_helper.save_json(metadata, output_file_path):
            self.logger.info(
                f"Metadata generation completed in {time.time() - start_time:.2f} seconds"
            )
        else:
            raise RuntimeError(f"Failed to save metadata to: {output_file_path}")

        return metadata

    def generate_from_single_file(
        self, file_path: str, output_path: str, filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate metadata for a single Python file.

        Args:
            file_path: Path to the Python file
            output_path: Path where to save the metadata
            filename: Optional filename for the metadata file

        Returns:
            Generated metadata dictionary
        """
        start_time = time.time()

        # Normalize paths
        file_path = PathHelper.normalize_path(file_path)
        output_path = PathHelper.normalize_path(output_path)

        self.logger.info(f"Starting metadata generation for file: {file_path}")

        # Validate file path
        if not file_path.exists():
            raise ValueError(f"File does not exist: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        if not PathHelper.is_python_file(file_path):
            raise ValueError(f"File is not a Python file: {file_path}")

        # Parse file
        content = self.file_helper.read_file_safely(file_path)
        if content is None:
            raise ValueError(f"Cannot read file: {file_path}")

        parsed_data = self.parser.parse_file(file_path, content)
        parsed_data["path"] = file_path.name  # Use just filename for single file

        # Create minimal metadata structure
        metadata = {
            "files": [parsed_data],
            "entry_points": [],
            "project_info": {
                "type": "single_file",
                "source_path": str(file_path),
                "total_files": 1,
                "generation_time": time.time() - start_time,
            },
        }

        # Save metadata
        output_filename = filename or self.config.output_filename
        output_file_path = output_path / output_filename

        if self.file_helper.save_json(metadata, output_file_path):
            self.logger.info(f"Single file metadata generation completed")
        else:
            raise RuntimeError(f"Failed to save metadata to: {output_file_path}")

        return metadata

    def _create_metadata_structure(
        self,
        parsed_files: List[Dict[str, Any]],
        analysis_results: Dict[str, Any],
        project_path: Path,
        start_time: float,
    ) -> Dict[str, Any]:
        """
        Create the final metadata structure.

        Args:
            parsed_files: List of parsed file data
            analysis_results: Analysis results
            project_path: Project root path
            start_time: Generation start time

        Returns:
            Complete metadata dictionary
        """
        metadata = {
            "files": parsed_files,
            "entry_points": analysis_results.get("entry_points", []),
            "dependencies": analysis_results.get("dependencies", {}),
            "metrics": analysis_results.get("metrics", {}),
            "project_info": {
                "source_path": str(project_path),
                "total_files": len(parsed_files),
                "generation_time": time.time() - start_time,
                "generator_version": "1.0.0",
                "config": {
                    "include_patterns": self.config.include_patterns,
                    "exclude_patterns": self.config.exclude_patterns,
                    "extract_docstrings": self.config.extract_docstrings,
                    "extract_type_hints": self.config.extract_type_hints,
                    "include_private_methods": self.config.include_private_methods,
                },
            },
        }

        return metadata

    def _create_empty_metadata(self, project_path: Path) -> Dict[str, Any]:
        """
        Create empty metadata structure when no files are found.

        Args:
            project_path: Project root path

        Returns:
            Empty metadata dictionary
        """
        return {
            "files": [],
            "entry_points": [],
            "dependencies": {
                "internal_dependencies": [],
                "external_dependencies": [],
                "total_internal": 0,
                "total_external": 0,
            },
            "metrics": {
                "total_files": 0,
                "total_functions": 0,
                "total_classes": 0,
                "total_methods": 0,
            },
            "project_info": {
                "source_path": str(project_path),
                "total_files": 0,
                "generation_time": 0.0,
                "generator_version": "1.0.0",
                "warning": "No Python files found in the project",
            },
        }
