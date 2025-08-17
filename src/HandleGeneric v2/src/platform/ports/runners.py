"""Test runner and sandbox execution ports."""

from typing import Protocol, List, Optional, Dict, Any
from pathlib import Path
from platform.domain.models.validation import TestResult


class TestRunner(Protocol):
    """Test execution interface."""

    def run(
        self,
        root: Path,
        selector: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        capture_output: bool = True,
    ) -> TestResult:
        """Run tests in the given directory."""
        ...

    def can_handle(self, root: Path) -> bool:
        """Check if this runner can handle tests in the given directory."""
        ...

    def get_test_files(self, root: Path) -> List[Path]:
        """Get list of test files that would be executed."""
        ...


class Sandbox(Protocol):
    """Sandbox for isolated code execution."""

    def execute(
        self,
        command: str,
        working_dir: Path,
        timeout_seconds: int = 60,
        env_vars: Optional[Dict[str, str]] = None,
        capture_output: bool = True,
    ) -> "ExecutionResult":
        """Execute a command in a sandbox."""
        ...

    def setup_environment(
        self, working_dir: Path, requirements: Optional[List[str]] = None
    ) -> None:
        """Set up the sandbox environment."""
        ...

    def cleanup(self, working_dir: Path) -> None:
        """Clean up sandbox resources."""
        ...


class ExecutionResult:
    """Result of sandbox execution."""

    def __init__(self, return_code: int, stdout: str, stderr: str, execution_time: float):
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
        self.execution_time = execution_time

    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.return_code == 0
