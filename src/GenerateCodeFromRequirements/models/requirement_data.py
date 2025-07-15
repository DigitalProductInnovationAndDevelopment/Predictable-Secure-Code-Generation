"""
Data models for requirement handling.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any


class RequirementStatus(Enum):
    """Status of a requirement implementation."""

    NEW = "new"
    MODIFIED = "modified"
    IMPLEMENTED = "implemented"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class RequirementData:
    """Represents a single requirement with its implementation details."""

    id: str
    description: str
    status: RequirementStatus = RequirementStatus.NEW

    # Implementation details
    target_files: list = None
    generated_code: str = ""
    test_code: str = ""

    # Analysis
    complexity_score: float = 0.0
    implementation_notes: str = ""
    dependencies: list = None

    # Error tracking
    error_message: str = ""

    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.target_files is None:
            self.target_files = []
        if self.dependencies is None:
            self.dependencies = []

    def mark_implemented(self, generated_code: str = "", test_code: str = ""):
        """Mark requirement as successfully implemented."""
        self.status = RequirementStatus.IMPLEMENTED
        if generated_code:
            self.generated_code = generated_code
        if test_code:
            self.test_code = test_code

    def mark_failed(self, error_message: str):
        """Mark requirement as failed with error message."""
        self.status = RequirementStatus.FAILED
        self.error_message = error_message

    def add_target_file(self, file_path: str):
        """Add a target file for this requirement."""
        if file_path not in self.target_files:
            self.target_files.append(file_path)

    def add_dependency(self, dependency: str):
        """Add a dependency for this requirement."""
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.value,
            "target_files": self.target_files,
            "generated_code": self.generated_code,
            "test_code": self.test_code,
            "complexity_score": self.complexity_score,
            "implementation_notes": self.implementation_notes,
            "dependencies": self.dependencies,
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RequirementData":
        """Create from dictionary."""
        req = cls(
            id=data["id"],
            description=data["description"],
            status=RequirementStatus(data.get("status", "new")),
        )
        req.target_files = data.get("target_files", [])
        req.generated_code = data.get("generated_code", "")
        req.test_code = data.get("test_code", "")
        req.complexity_score = data.get("complexity_score", 0.0)
        req.implementation_notes = data.get("implementation_notes", "")
        req.dependencies = data.get("dependencies", [])
        req.error_message = data.get("error_message", "")
        return req
