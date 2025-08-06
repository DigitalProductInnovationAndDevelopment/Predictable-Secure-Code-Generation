"""
Generic metadata generator for any programming language.

This module provides a language-agnostic metadata generator that can process
codebases in multiple programming languages using registered language providers.
"""

import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

from ..language.registry import get_global_registry
from ..initialization import ensure_initialized
from ..language.detector import FileDetector


class GenericMetadataGenerator:
    """
    Generic metadata generator for any programming language.

    This class can generate metadata for projects containing files in multiple
    programming languages, using the appropriate language providers.
    """

    def __init__(self, exclude_patterns: Optional[List[str]] = None):
        """
        Initialize the generic metadata generator.

        Args:
            exclude_patterns: Optional list of file patterns to exclude
        """
        self.logger = logging.getLogger(__name__)

        # Ensure language providers are initialized
        ensure_initialized()

        self.registry = get_global_registry()
        self.file_detector = FileDetector(exclude_patterns)

        self.logger.info("Generic metadata generator initialized")

    def generate_metadata(
        self,
        project_path: str,
        output_path: str,
        filename: str = "metadata.json",
        languages: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate metadata for a multi-language project.

        Args:
            project_path: Path to the project directory
            output_path: Path where to save the metadata
            filename: Name of the metadata file
            languages: Optional list of languages to process (process all if None)

        Returns:
            Generated metadata dictionary
        """
        start_time = time.time()

        project_path = Path(project_path)
        output_path = Path(output_path)

        self.logger.info(f"Starting generic metadata generation for: {project_path}")

        # Validate paths
        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

        if not project_path.is_dir():
            raise ValueError(f"Project path is not a directory: {project_path}")

        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)

        # Analyze project structure
        self.logger.info("Analyzing project structure...")
        project_analysis = self.file_detector.analyze_project_structure(project_path)

        # Find files by language
        self.logger.info("Discovering source files...")
        files_by_language = self.file_detector.find_project_files(
            project_path, languages
        )

        if not files_by_language:
            self.logger.warning("No supported source files found in the project")
            return self._create_empty_metadata(
                project_path, project_analysis, start_time
            )

        # Process files for each language
        all_files_metadata = []
        language_summaries = {}

        for language, file_paths in files_by_language.items():
            self.logger.info(f"Processing {len(file_paths)} {language} files...")

            provider = self.registry.get_provider(language)
            if not provider:
                self.logger.warning(f"No provider found for language: {language}")
                continue

            language_files, language_summary = self._process_language_files(
                language, file_paths, provider, project_path
            )

            all_files_metadata.extend(language_files)
            language_summaries[language] = language_summary

        # Create final metadata structure
        metadata = self._create_metadata_structure(
            all_files_metadata,
            language_summaries,
            project_analysis,
            project_path,
            start_time,
        )

        # Save metadata
        output_file_path = output_path / filename
        self._save_metadata(metadata, output_file_path)

        execution_time = time.time() - start_time
        self.logger.info(
            f"Generic metadata generation completed in {execution_time:.2f} seconds"
        )

        return metadata

    def generate_single_file_metadata(
        self, file_path: str, output_path: str, filename: str = "metadata.json"
    ) -> Dict[str, Any]:
        """
        Generate metadata for a single source file.

        Args:
            file_path: Path to the source file
            output_path: Path where to save the metadata
            filename: Name of the metadata file

        Returns:
            Generated metadata dictionary
        """
        start_time = time.time()

        file_path = Path(file_path)
        output_path = Path(output_path)

        self.logger.info(f"Starting single file metadata generation for: {file_path}")

        # Validate file
        if not file_path.exists():
            raise ValueError(f"File does not exist: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        # Detect language
        language = self.file_detector.detect_language(file_path)
        if not language:
            raise ValueError(f"Unsupported file type: {file_path}")

        # Get provider
        provider = self.registry.get_provider(language)
        if not provider:
            raise ValueError(f"No provider available for language: {language}")

        # Read file content
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            raise ValueError(f"Cannot read file {file_path}: {e}")

        # Parse file
        file_metadata = provider.parse_file(file_path, content)

        # Create metadata structure
        metadata = {
            "files": [file_metadata.to_dict()],
            "languages": [language],
            "project_info": {
                "type": "single_file",
                "source_path": str(file_path),
                "main_language": language,
                "total_files": 1,
                "generation_time": time.time() - start_time,
                "generator_version": "2.0.0",
            },
            "language_summaries": {
                language: {
                    "file_count": 1,
                    "total_lines": file_metadata.lines_of_code,
                    "total_size": file_metadata.size,
                }
            },
        }

        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)

        # Save metadata
        output_file_path = output_path / filename
        self._save_metadata(metadata, output_file_path)

        self.logger.info("Single file metadata generation completed")

        return metadata

    def _process_language_files(
        self, language: str, file_paths: List[Path], provider, project_root: Path
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Process files for a specific language.

        Args:
            language: Programming language name
            file_paths: List of file paths to process
            provider: Language provider instance
            project_root: Project root path for relative path calculation

        Returns:
            Tuple of (file metadata list, language summary)
        """
        files_metadata = []
        total_lines = 0
        total_size = 0
        processed_files = 0

        for file_path in file_paths:
            try:
                # Read file content
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Parse file using language provider
                file_metadata = provider.parse_file(file_path, content)

                # Convert to relative path
                try:
                    relative_path = file_path.relative_to(project_root)
                    file_metadata.path = str(relative_path)
                except ValueError:
                    # File is outside project root, use absolute path
                    file_metadata.path = str(file_path)

                files_metadata.append(file_metadata.to_dict())
                total_lines += file_metadata.lines_of_code
                total_size += file_metadata.size
                processed_files += 1

                self.logger.debug(f"Processed {language} file: {file_metadata.path}")

            except Exception as e:
                self.logger.warning(f"Failed to process {file_path}: {e}")

        language_summary = {
            "file_count": processed_files,
            "total_lines": total_lines,
            "total_size": total_size,
            "provider": provider.__class__.__name__,
        }

        return files_metadata, language_summary

    def _create_metadata_structure(
        self,
        files_metadata: List[Dict[str, Any]],
        language_summaries: Dict[str, Dict[str, Any]],
        project_analysis: Dict[str, Any],
        project_path: Path,
        start_time: float,
    ) -> Dict[str, Any]:
        """
        Create the final metadata structure.

        Args:
            files_metadata: List of file metadata
            language_summaries: Summary for each language
            project_analysis: Project structure analysis
            project_path: Project root path
            start_time: Generation start time

        Returns:
            Complete metadata dictionary
        """
        execution_time = time.time() - start_time

        return {
            "files": files_metadata,
            "languages": list(language_summaries.keys()),
            "language_summaries": language_summaries,
            "project_info": {
                "source_path": str(project_path),
                "total_files": len(files_metadata),
                "main_language": project_analysis.get("main_language"),
                "project_type": project_analysis.get("project_type"),
                "generation_time": execution_time,
                "generator_version": "2.0.0",
                "supported_languages": self.registry.get_supported_languages(),
                "project_analysis": project_analysis,
            },
        }

    def _create_empty_metadata(
        self, project_path: Path, project_analysis: Dict[str, Any], start_time: float
    ) -> Dict[str, Any]:
        """
        Create empty metadata structure when no files are found.

        Args:
            project_path: Project root path
            project_analysis: Project structure analysis
            start_time: Generation start time

        Returns:
            Empty metadata dictionary
        """
        return {
            "files": [],
            "languages": [],
            "language_summaries": {},
            "project_info": {
                "source_path": str(project_path),
                "total_files": 0,
                "main_language": None,
                "project_type": project_analysis.get("project_type", "empty"),
                "generation_time": time.time() - start_time,
                "generator_version": "2.0.0",
                "supported_languages": self.registry.get_supported_languages(),
                "project_analysis": project_analysis,
            },
        }

    def _save_metadata(self, metadata: Dict[str, Any], output_file_path: Path) -> None:
        """
        Save metadata to JSON file.

        Args:
            metadata: Metadata dictionary to save
            output_file_path: Output file path
        """
        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Metadata saved to: {output_file_path}")

        except Exception as e:
            self.logger.error(f"Failed to save metadata to {output_file_path}: {e}")
            raise

    def get_supported_info(self) -> Dict[str, Any]:
        """
        Get information about supported languages and extensions.

        Returns:
            Dictionary with support information
        """
        return {
            "supported_languages": self.registry.get_supported_languages(),
            "supported_extensions": list(self.registry.get_supported_extensions()),
            "providers_info": self.registry.get_providers_info(),
        }
