"""
Data models for code changes and modifications.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any


class ChangeType(Enum):
    """Type of code change."""

    CREATE_FILE = "create_file"
    MODIFY_FILE = "modify_file"
    ADD_FUNCTION = "add_function"
    ADD_CLASS = "add_class"
    ADD_METHOD = "add_method"
    MODIFY_FUNCTION = "modify_function"
    MODIFY_CLASS = "modify_class"
    ADD_IMPORT = "add_import"
    CREATE_TEST = "create_test"


@dataclass
class CodeChange:
    """Represents a specific code change to be made."""

    change_type: ChangeType
    file_path: str
    content: str
    requirement_id: str

    # Location details
    target_class: Optional[str] = None
    target_function: Optional[str] = None
    insert_line: Optional[int] = None

    # Context
    description: str = ""
    dependencies: list = None

    # Status
    applied: bool = False
    error_message: str = ""

    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.dependencies is None:
            self.dependencies = []

    def mark_applied(self):
        """Mark change as successfully applied."""
        self.applied = True
        self.error_message = ""

    def mark_failed(self, error_message: str):
        """Mark change as failed with error message."""
        self.applied = False
        self.error_message = error_message

    def add_dependency(self, dependency: str):
        """Add a dependency for this change."""
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "change_type": self.change_type.value,
            "file_path": self.file_path,
            "content": self.content,
            "requirement_id": self.requirement_id,
            "target_class": self.target_class,
            "target_function": self.target_function,
            "insert_line": self.insert_line,
            "description": self.description,
            "dependencies": self.dependencies,
            "applied": self.applied,
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodeChange":
        """Create from dictionary."""
        change = cls(
            change_type=ChangeType(data["change_type"]),
            file_path=data["file_path"],
            content=data["content"],
            requirement_id=data["requirement_id"],
        )
        change.target_class = data.get("target_class")
        change.target_function = data.get("target_function")
        change.insert_line = data.get("insert_line")
        change.description = data.get("description", "")
        change.dependencies = data.get("dependencies", [])
        change.applied = data.get("applied", False)
        change.error_message = data.get("error_message", "")
        return change
