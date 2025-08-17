"""Pytest runner adapter for executing Python tests."""

import subprocess
import json
from typing import List, Optional
from pathlib import Path
from platform.ports.runners import TestRunner
from platform.domain.models.validation import TestResult
from platform.kernel.logging import get_logger

logger = get_logger(__name__)


class PytestRunner:
    """Pytest test runner implementation."""

    def run(
        self,
        root: Path,
        selector: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        capture_output: bool = True,
    ) -> TestResult:
        """Run pytest tests in the given directory."""
        try:
            # Build pytest command
            cmd = ["python", "-m", "pytest"]

            # Add JSON reporting
            report_path = root / "test_report.json"
            cmd.extend(["--json-report", f"--json-report-file={report_path}"])

            # Add selector if provided
            if selector:
                cmd.extend(["-k", selector])

            # Add verbosity
            cmd.append("-v")

            # Add root directory
            cmd.append(str(root))

            logger.info("Running pytest", command=" ".join(cmd), root=str(root))

            # Execute command
            result = subprocess.run(
                cmd,
                cwd=root,
                capture_output=capture_output,
                text=True,
                timeout=timeout_seconds or 300,
            )

            # Parse results
            passed = 0
            failed = 0
            errors = 0

            if report_path.exists():
                try:
                    with open(report_path) as f:
                        report_data = json.load(f)
                        summary = report_data.get("summary", {})
                        passed = summary.get("passed", 0)
                        failed = summary.get("failed", 0)
                        errors = summary.get("error", 0)
                except Exception as e:
                    logger.warning("Failed to parse test report", error=str(e))

            # Determine status
            if result.returncode == 0:
                status = "passed"
            elif failed > 0 or errors > 0:
                status = "failed"
            else:
                status = "error"

            test_result = TestResult(
                status=status,
                passed=passed,
                failed=failed,
                errors=errors,
                report_path=str(report_path) if report_path.exists() else None,
            )

            logger.info(
                "Pytest execution completed",
                status=status,
                passed=passed,
                failed=failed,
                errors=errors,
            )

            return test_result

        except subprocess.TimeoutExpired:
            logger.error("Pytest execution timed out", timeout=timeout_seconds)
            return TestResult(status="error", errors=1)
        except Exception as e:
            logger.error("Pytest execution failed", error=str(e))
            return TestResult(status="error", errors=1)

    def can_handle(self, root: Path) -> bool:
        """Check if this runner can handle tests in the given directory."""
        # Look for pytest markers
        pytest_files = ["pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini"]

        # Check for pytest config files
        for config_file in pytest_files:
            if (root / config_file).exists():
                return True

        # Check for test files
        test_files = list(root.rglob("test_*.py")) + list(root.rglob("*_test.py"))
        return len(test_files) > 0

    def get_test_files(self, root: Path) -> List[Path]:
        """Get list of test files that would be executed."""
        test_files = []
        test_files.extend(root.rglob("test_*.py"))
        test_files.extend(root.rglob("*_test.py"))
        return test_files
