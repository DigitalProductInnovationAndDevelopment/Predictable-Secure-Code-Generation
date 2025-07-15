"""
Data models for generation results and status tracking.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


class GenerationStatus(Enum):
    """Status of code generation process."""

    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"


@dataclass
class GenerationProblem:
    """Represents a problem encountered during generation."""

    severity: str  # "error", "warning", "info"
    category: str  # "requirement", "integration", "testing", "validation"
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    requirement_id: Optional[str] = None


@dataclass
class GenerationResult:
    """Result of code generation process."""

    status: GenerationStatus
    timestamp: datetime = field(default_factory=datetime.now)

    # Requirements processing
    requirements_analyzed: int = 0
    requirements_implemented: int = 0
    requirements_failed: int = 0

    # Code changes
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    tests_generated: List[str] = field(default_factory=list)

    # Problems and issues
    problems: List[GenerationProblem] = field(default_factory=list)

    # Metadata
    metadata_updated: bool = False
    validation_passed: bool = False

    # Execution details
    execution_time: float = 0.0
    ai_tokens_used: int = 0

    # Paths
    source_path: Optional[str] = None
    output_path: Optional[str] = None
    requirements_path: Optional[str] = None
    metadata_path: Optional[str] = None

    def add_problem(
        self,
        severity: str,
        category: str,
        message: str,
        file_path: str = None,
        line_number: int = None,
        requirement_id: str = None,
    ):
        """Add a problem to the result."""
        problem = GenerationProblem(
            severity=severity,
            category=category,
            message=message,
            file_path=file_path,
            line_number=line_number,
            requirement_id=requirement_id,
        )
        self.problems.append(problem)

    def get_problems_by_severity(self, severity: str) -> List[GenerationProblem]:
        """Get all problems of a specific severity."""
        return [p for p in self.problems if p.severity == severity]

    def has_errors(self) -> bool:
        """Check if there are any error-level problems."""
        return any(p.severity == "error" for p in self.problems)

    def has_warnings(self) -> bool:
        """Check if there are any warning-level problems."""
        return any(p.severity == "warning" for p in self.problems)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "requirements_analyzed": self.requirements_analyzed,
            "requirements_implemented": self.requirements_implemented,
            "requirements_failed": self.requirements_failed,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "tests_generated": self.tests_generated,
            "problems": [
                {
                    "severity": p.severity,
                    "category": p.category,
                    "message": p.message,
                    "file_path": p.file_path,
                    "line_number": p.line_number,
                    "requirement_id": p.requirement_id,
                }
                for p in self.problems
            ],
            "metadata_updated": self.metadata_updated,
            "validation_passed": self.validation_passed,
            "execution_time": self.execution_time,
            "ai_tokens_used": self.ai_tokens_used,
            "source_path": self.source_path,
            "output_path": self.output_path,
            "requirements_path": self.requirements_path,
            "metadata_path": self.metadata_path,
        }

    def get_summary(self) -> str:
        """Get a human-readable summary of the generation result."""
        summary_lines = [
            f"Code Generation Summary - {self.status.value.upper()}",
            f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"Requirements: {self.requirements_implemented}/{self.requirements_analyzed} implemented",
            f"Files created: {len(self.files_created)}",
            f"Files modified: {len(self.files_modified)}",
            f"Tests generated: {len(self.tests_generated)}",
            "",
            f"Problems: {len(self.get_problems_by_severity('error'))} errors, "
            f"{len(self.get_problems_by_severity('warning'))} warnings",
            f"Metadata updated: {'Yes' if self.metadata_updated else 'No'}",
            f"Validation passed: {'Yes' if self.validation_passed else 'No'}",
            "",
            f"Execution time: {self.execution_time:.2f}s",
            f"AI tokens used: {self.ai_tokens_used}",
        ]

        if self.problems:
            summary_lines.extend(["", "Problems:"])
            for problem in self.problems:
                location = ""
                if problem.file_path:
                    location = f" ({problem.file_path}"
                    if problem.line_number:
                        location += f":{problem.line_number}"
                    location += ")"

                req_info = (
                    f" [Req: {problem.requirement_id}]"
                    if problem.requirement_id
                    else ""
                )
                summary_lines.append(
                    f"  {problem.severity.upper()}: {problem.message}{location}{req_info}"
                )

        return "\n".join(summary_lines)
