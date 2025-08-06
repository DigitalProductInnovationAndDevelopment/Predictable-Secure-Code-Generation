"""
Abstract base class for language providers.

This module defines the interface that all language-specific providers must implement
to support code parsing, validation, and generation for different programming languages.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class SyntaxValidationResult(Enum):
    """Result of syntax validation."""

    VALID = "valid"
    INVALID = "invalid"
    ERROR = "error"


@dataclass
class FunctionInfo:
    """Generic container for function metadata across languages."""

    name: str
    parameters: List[str]
    docstring: Optional[str] = None
    start_line: int = 0
    end_line: int = 0
    decorators: List[str] = None
    return_type: Optional[str] = None
    is_async: bool = False
    visibility: str = "public"  # public, private, protected
    is_static: bool = False

    def __post_init__(self):
        if self.decorators is None:
            self.decorators = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "parameters": self.parameters,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "visibility": self.visibility,
        }

        if self.docstring:
            result["docstring"] = self.docstring
        if self.decorators:
            result["decorators"] = self.decorators
        if self.return_type:
            result["return_type"] = self.return_type
        if self.is_async:
            result["is_async"] = self.is_async
        if self.is_static:
            result["is_static"] = self.is_static

        return result


@dataclass
class ClassInfo:
    """Generic container for class metadata across languages."""

    name: str
    docstring: Optional[str] = None
    start_line: int = 0
    end_line: int = 0
    base_classes: List[str] = None
    interfaces: List[str] = None
    decorators: List[str] = None
    methods: List[FunctionInfo] = None
    visibility: str = "public"
    is_abstract: bool = False
    is_final: bool = False

    def __post_init__(self):
        if self.base_classes is None:
            self.base_classes = []
        if self.interfaces is None:
            self.interfaces = []
        if self.decorators is None:
            self.decorators = []
        if self.methods is None:
            self.methods = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "methods": [method.to_dict() for method in self.methods],
            "visibility": self.visibility,
        }

        if self.docstring:
            result["docstring"] = self.docstring
        if self.base_classes:
            result["base_classes"] = self.base_classes
        if self.interfaces:
            result["interfaces"] = self.interfaces
        if self.decorators:
            result["decorators"] = self.decorators
        if self.is_abstract:
            result["is_abstract"] = self.is_abstract
        if self.is_final:
            result["is_final"] = self.is_final

        return result


@dataclass
class FileMetadata:
    """Generic container for file metadata across languages."""

    path: str
    language: str
    size: int
    lines_of_code: int
    classes: List[ClassInfo] = None
    functions: List[FunctionInfo] = None
    imports: List[str] = None
    constants: Dict[str, Any] = None
    comments: List[str] = None
    docstring: Optional[str] = None

    def __post_init__(self):
        if self.classes is None:
            self.classes = []
        if self.functions is None:
            self.functions = []
        if self.imports is None:
            self.imports = []
        if self.constants is None:
            self.constants = {}
        if self.comments is None:
            self.comments = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "path": self.path,
            "language": self.language,
            "size": self.size,
            "lines_of_code": self.lines_of_code,
            "classes": [cls.to_dict() for cls in self.classes],
            "functions": [func.to_dict() for func in self.functions],
            "imports": self.imports,
            "constants": self.constants,
            "comments": self.comments,
            "docstring": self.docstring,
        }


class LanguageProvider(ABC):
    """
    Abstract base class for language-specific providers.

    Each programming language should have its own provider implementation
    that handles parsing, validation, and code generation for that language.
    """

    @property
    @abstractmethod
    def language_name(self) -> str:
        """Return the name of the programming language."""
        pass

    @property
    @abstractmethod
    def file_extensions(self) -> Set[str]:
        """Return the set of file extensions for this language."""
        pass

    @property
    @abstractmethod
    def comment_prefixes(self) -> List[str]:
        """Return list of comment prefixes for this language."""
        pass

    @abstractmethod
    def parse_file(self, file_path: Path, content: str) -> FileMetadata:
        """
        Parse a source file and extract metadata.

        Args:
            file_path: Path to the source file
            content: Content of the source file

        Returns:
            FileMetadata object containing extracted information
        """
        pass

    @abstractmethod
    def validate_syntax(
        self, file_path: Path, content: str
    ) -> tuple[SyntaxValidationResult, Optional[str]]:
        """
        Validate the syntax of source code.

        Args:
            file_path: Path to the source file
            content: Content of the source file

        Returns:
            Tuple of (validation result, error message if any)
        """
        pass

    @abstractmethod
    def generate_code_prompt(self, requirement: str, context: Dict[str, Any]) -> str:
        """
        Generate a language-specific prompt for AI code generation.

        Args:
            requirement: The requirement description
            context: Additional context for code generation

        Returns:
            Formatted prompt for AI code generation
        """
        pass

    @abstractmethod
    def extract_generated_code(self, ai_response: str) -> str:
        """
        Extract clean code from AI response.

        Args:
            ai_response: Raw response from AI

        Returns:
            Clean, executable code
        """
        pass

    @abstractmethod
    def get_test_framework_commands(self) -> List[str]:
        """
        Get commands to run tests for this language.

        Returns:
            List of command parts to execute tests
        """
        pass

    @abstractmethod
    def generate_test_code(
        self, function_info: FunctionInfo, context: Dict[str, Any]
    ) -> str:
        """
        Generate test code for a function.

        Args:
            function_info: Information about the function to test
            context: Additional context for test generation

        Returns:
            Generated test code
        """
        pass

    @abstractmethod
    def get_standard_imports(self) -> List[str]:
        """
        Get standard/common imports for this language.

        Returns:
            List of standard imports
        """
        pass

    def supports_file(self, file_path: Path) -> bool:
        """
        Check if this provider supports the given file.

        Args:
            file_path: Path to check

        Returns:
            True if this provider can handle the file
        """
        return file_path.suffix.lower() in self.file_extensions

    def get_file_template(self, template_type: str = "basic") -> str:
        """
        Get a basic file template for this language.

        Args:
            template_type: Type of template (basic, class, module, etc.)

        Returns:
            Template string
        """
        return f"// {self.language_name} file template\n"
