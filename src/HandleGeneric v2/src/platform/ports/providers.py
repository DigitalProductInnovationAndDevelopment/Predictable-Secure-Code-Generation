"""Provider interfaces for language-specific operations."""

from typing import Protocol, List, Optional, Dict, Any
from pathlib import Path
from platform.domain.models.requirements import Requirement
from platform.domain.models.metadata import FileMetadata
from platform.domain.models.generation import GeneratedFile
from platform.domain.models.validation import SyntaxResult


class ProjectContext(Dict[str, Any]):
    """Type alias for project context."""

    pass


class CodeGenProvider(Protocol):
    """Provider for code generation per language."""

    language: str

    def build_prompt(self, requirement: Requirement, context: ProjectContext) -> str:
        """Build a prompt for code generation."""
        ...

    def postprocess(self, files: List[GeneratedFile]) -> List[GeneratedFile]:
        """Post-process generated files (formatting, linting, etc.)."""
        ...

    def get_file_extension(self) -> str:
        """Get the primary file extension for this language."""
        ...

    def get_template_vars(self, context: ProjectContext) -> Dict[str, Any]:
        """Get template variables for prompt generation."""
        ...


class MetadataProvider(Protocol):
    """Provider for extracting metadata from code files."""

    language: str
    extensions: set[str]

    def parse_file(self, path: Path, content: str) -> FileMetadata:
        """Parse a file and extract metadata."""
        ...

    def can_handle(self, file_path: Path) -> bool:
        """Check if this provider can handle the given file."""
        ...


class SyntaxValidator(Protocol):
    """Provider for syntax validation per language."""

    language: str

    def validate(self, file: Path, content: str) -> SyntaxResult:
        """Validate syntax of the given file content."""
        ...

    def can_handle(self, file_path: Path) -> bool:
        """Check if this provider can handle the given file."""
        ...
