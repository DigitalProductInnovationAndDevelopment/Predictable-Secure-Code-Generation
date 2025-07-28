"""
Data models for validation results and status tracking.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


class ValidationStatus(Enum):
    """Enumeration for validation status."""

    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class ValidationProblem:
    """Represents a single validation problem."""

    severity: str  # "error", "warning", "info"
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    column: Optional[int] = None
    error_code: Optional[str] = None
    suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "severity": self.severity,
            "message": self.message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "error_code": self.error_code,
            "suggestion": self.suggestion,
        }


@dataclass
class ValidationResult:
    """Represents the result of a validation step."""

    step_name: str
    status: ValidationStatus
    is_valid: bool
    problems: List[ValidationProblem] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def add_problem(self, severity: str, message: str, **kwargs):
        """Add a validation problem."""
        problem = ValidationProblem(severity=severity, message=message, **kwargs)
        self.problems.append(problem)

    def add_error(self, message: str, **kwargs):
        """Add an error problem."""
        self.add_problem("error", message, **kwargs)
        self.is_valid = False
        if self.status == ValidationStatus.VALID:
            self.status = ValidationStatus.INVALID

    def add_warning(self, message: str, **kwargs):
        """Add a warning problem."""
        self.add_problem("warning", message, **kwargs)
        if self.status == ValidationStatus.VALID:
            self.status = ValidationStatus.WARNING

    def add_info(self, message: str, **kwargs):
        """Add an info problem."""
        self.add_problem("info", message, **kwargs)

    def get_errors(self) -> List[ValidationProblem]:
        """Get all error problems."""
        return [p for p in self.problems if p.severity == "error"]

    def get_warnings(self) -> List[ValidationProblem]:
        """Get all warning problems."""
        return [p for p in self.problems if p.severity == "warning"]

    def error_count(self) -> int:
        """Get count of errors."""
        return len(self.get_errors())

    def warning_count(self) -> int:
        """Get count of warnings."""
        return len(self.get_warnings())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "step_name": self.step_name,
            "status": self.status.value,
            "is_valid": self.is_valid,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat(),
            "error_count": self.error_count(),
            "warning_count": self.warning_count(),
            "problems": [p.to_dict() for p in self.problems],
            "metadata": self.metadata,
        }


@dataclass
class OverallValidationResult:
    """Represents the overall validation result for all steps."""

    codebase_path: str
    metadata_path: str
    overall_status: ValidationStatus
    is_valid: bool
    step_results: List[ValidationResult] = field(default_factory=list)
    total_execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def add_step_result(self, result: ValidationResult):
        """Add a step validation result."""
        self.step_results.append(result)
        self.total_execution_time += result.execution_time

        # Update overall status based on step results
        if not result.is_valid:
            self.is_valid = False
            if result.status == ValidationStatus.INVALID:
                self.overall_status = ValidationStatus.INVALID
        elif (
            result.status == ValidationStatus.WARNING
            and self.overall_status == ValidationStatus.VALID
        ):
            self.overall_status = ValidationStatus.WARNING

    def get_step_result(self, step_name: str) -> Optional[ValidationResult]:
        """Get result for a specific step."""
        for result in self.step_results:
            if result.step_name == step_name:
                return result
        return None

    def get_all_problems(self) -> List[ValidationProblem]:
        """Get all problems from all steps."""
        all_problems = []
        for result in self.step_results:
            all_problems.extend(result.problems)
        return all_problems

    def total_error_count(self) -> int:
        """Get total error count across all steps."""
        return sum(result.error_count() for result in self.step_results)

    def total_warning_count(self) -> int:
        """Get total warning count across all steps."""
        return sum(result.warning_count() for result in self.step_results)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "codebase_path": self.codebase_path,
            "metadata_path": self.metadata_path,
            "overall_status": self.overall_status.value,
            "is_valid": self.is_valid,
            "total_execution_time": self.total_execution_time,
            "timestamp": self.timestamp.isoformat(),
            "total_error_count": self.total_error_count(),
            "total_warning_count": self.total_warning_count(),
            "step_results": [result.to_dict() for result in self.step_results],
        }
