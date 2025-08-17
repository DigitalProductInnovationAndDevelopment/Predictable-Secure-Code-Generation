"""S2 - Metadata Generation Use Cases."""

from typing import List, Set, Optional
from pathlib import Path
from platform.domain.models.metadata import FileMetadata, ProjectMetadata
from platform.ports.fs import FileSystem
from platform.ports.providers import MetadataProvider
from platform.kernel.registry import registry
from platform.kernel.config import config
from platform.kernel.logging import get_logger

logger = get_logger(__name__)


class GenerateMetadata:
    """Use case for generating metadata from code files."""

    def __init__(self, file_system: FileSystem):
        self.file_system = file_system

    def execute(
        self,
        project_path: Path,
        include_languages: Optional[Set[str]] = None,
        exclude_dirs: Optional[Set[str]] = None,
    ) -> ProjectMetadata:
        """Execute metadata generation for a project."""
        logger.info("Starting metadata generation", project_path=str(project_path))

        exclude_dirs = exclude_dirs or config.ignored_directories
        include_languages = include_languages or set(registry.metadata.get_supported_languages())

        # Scan for files
        all_files = self.file_system.scan(
            project_path, exclude_dirs=exclude_dirs, max_size_mb=config.max_file_size_mb
        )

        # Group files by language and process
        file_metadata_list = []
        languages_found = set()

        for file_path in all_files:
            try:
                # Find appropriate provider
                provider = self._find_provider_for_file(file_path)
                if not provider:
                    continue

                # Skip if language not in include list
                if provider.language not in include_languages:
                    continue

                # Read file content
                content = self.file_system.read_text(file_path)

                # Extract metadata
                metadata = provider.parse_file(file_path, content)
                file_metadata_list.append(metadata)
                languages_found.add(provider.language)

                logger.debug(
                    "Processed file for metadata",
                    file=str(file_path),
                    language=provider.language,
                    functions=len(metadata.functions),
                    classes=len(metadata.classes),
                )

            except Exception as e:
                logger.warning(
                    "Failed to process file for metadata", file=str(file_path), error=str(e)
                )
                continue

        # Create project metadata
        project_metadata = ProjectMetadata(
            files=file_metadata_list, languages=sorted(list(languages_found))
        )

        logger.info(
            "Metadata generation completed",
            total_files=len(file_metadata_list),
            languages=list(languages_found),
            total_functions=sum(len(f.functions) for f in file_metadata_list),
            total_classes=sum(len(f.classes) for f in file_metadata_list),
            total_loc=sum(f.loc for f in file_metadata_list),
        )

        return project_metadata

    def _find_provider_for_file(self, file_path: Path) -> Optional[MetadataProvider]:
        """Find the appropriate metadata provider for a file."""
        for language in registry.metadata.get_supported_languages():
            provider = registry.metadata.get(language)
            if provider and provider.can_handle(file_path):
                return provider
        return None
