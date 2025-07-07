"""
Helper utilities for the validation system.
"""

import os
import json
import subprocess
import fnmatch
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging


class ValidationHelper:
    """Helper class for validation operations."""

    @staticmethod
    def load_metadata(metadata_path: str) -> Dict[str, Any]:
        """Load metadata from JSON file."""
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in metadata file: {e}")

    @staticmethod
    def get_python_files(
        codebase_path: str, exclude_patterns: List[str] = None
    ) -> List[str]:
        """Get all Python files in the codebase."""
        if exclude_patterns is None:
            exclude_patterns = [
                "__pycache__/*",
                "*.pyc",
                ".git/*",
                ".pytest_cache/*",
                "htmlcov/*",
                ".coverage*",
                "build/*",
                "dist/*",
                "*.egg-info/*",
            ]

        python_files = []
        codebase_path = Path(codebase_path)

        for root, dirs, files in os.walk(codebase_path):
            # Remove excluded directories
            dirs[:] = [
                d
                for d in dirs
                if not ValidationHelper._is_excluded(
                    Path(root) / d, codebase_path, exclude_patterns
                )
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    if not ValidationHelper._is_excluded(
                        file_path, codebase_path, exclude_patterns
                    ):
                        python_files.append(str(file_path))

        return python_files

    @staticmethod
    def _is_excluded(
        file_path: Path, base_path: Path, exclude_patterns: List[str]
    ) -> bool:
        """Check if a file should be excluded."""
        try:
            relative_path = file_path.relative_to(base_path)
            relative_str = str(relative_path)

            for pattern in exclude_patterns:
                if fnmatch.fnmatch(relative_str, pattern):
                    return True
            return False
        except ValueError:
            return False

    @staticmethod
    def run_command(
        command: List[str], cwd: str = None, timeout: int = 300
    ) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(
                command, cwd=cwd, capture_output=True, text=True, timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return -1, "", str(e)

    @staticmethod
    def check_python_syntax(file_path: str) -> Tuple[bool, Optional[str]]:
        """Check Python file syntax."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            compile(content, file_path, "exec")
            return True, None
        except SyntaxError as e:
            error_msg = f"Syntax error in {file_path} at line {e.lineno}: {e.msg}"
            return False, error_msg
        except Exception as e:
            error_msg = f"Error checking syntax in {file_path}: {str(e)}"
            return False, error_msg

    @staticmethod
    def find_test_files(
        codebase_path: str, test_patterns: List[str], test_directories: List[str]
    ) -> List[str]:
        """Find test files in the codebase."""
        test_files = []
        codebase_path = Path(codebase_path)

        # Look in test directories
        for test_dir in test_directories:
            test_dir_path = codebase_path / test_dir
            if test_dir_path.exists():
                for pattern in test_patterns:
                    test_files.extend(test_dir_path.glob(pattern))

        # Look for test files in the main codebase
        for pattern in test_patterns:
            test_files.extend(codebase_path.glob(f"**/{pattern}"))

        return [str(f) for f in set(test_files)]

    @staticmethod
    def extract_requirements_from_csv(csv_path: str) -> List[Dict[str, str]]:
        """Extract requirements from CSV file."""
        requirements = []

        if not os.path.exists(csv_path):
            return requirements

        try:
            import csv

            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    requirements.append(
                        {
                            "id": row.get("id", ""),
                            "description": row.get("description", ""),
                        }
                    )
        except Exception as e:
            logging.warning(f"Could not read requirements from {csv_path}: {e}")

        return requirements

    @staticmethod
    def create_file_function_summary(metadata: Dict[str, Any]) -> str:
        """Create a summary of files and functions from metadata."""
        summary_parts = []

        for file_data in metadata.get("files", []):
            file_path = file_data.get("path", "")
            summary_parts.append(f"\nFile: {file_path}")

            # Add functions
            for func in file_data.get("functions", []):
                func_name = func.get("name", "")
                args = func.get("args", [])
                docstring = func.get("docstring", "")

                summary_parts.append(f"  Function: {func_name}({', '.join(args)})")
                if docstring:
                    # Truncate long docstrings
                    short_doc = docstring.split("\n")[0][:100]
                    summary_parts.append(f"    Description: {short_doc}")

            # Add classes and methods
            for cls in file_data.get("classes", []):
                cls_name = cls.get("name", "")
                summary_parts.append(f"  Class: {cls_name}")

                for method in cls.get("methods", []):
                    method_name = method.get("name", "")
                    args = method.get("args", [])
                    summary_parts.append(
                        f"    Method: {method_name}({', '.join(args)})"
                    )

        return "\n".join(summary_parts)

    @staticmethod
    def save_report(
        report_data: Dict[str, Any], output_path: str, format_type: str = "json"
    ):
        """Save validation report to file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if format_type == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
        elif format_type == "yaml":
            try:
                import yaml

                with open(output_path, "w", encoding="utf-8") as f:
                    yaml.dump(report_data, f, default_flow_style=False)
            except ImportError:
                raise ImportError("PyYAML is required for YAML output")
        elif format_type == "text":
            with open(output_path, "w", encoding="utf-8") as f:
                ValidationHelper._write_text_report(report_data, f)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    @staticmethod
    def _write_text_report(report_data: Dict[str, Any], file_handle):
        """Write validation report in text format."""
        file_handle.write("VALIDATION REPORT\n")
        file_handle.write("=" * 50 + "\n\n")

        file_handle.write(
            f"Overall Status: {report_data.get('overall_status', 'unknown')}\n"
        )
        file_handle.write(f"Valid: {report_data.get('is_valid', False)}\n")
        file_handle.write(f"Total Errors: {report_data.get('total_error_count', 0)}\n")
        file_handle.write(
            f"Total Warnings: {report_data.get('total_warning_count', 0)}\n\n"
        )

        for step_result in report_data.get("step_results", []):
            file_handle.write(f"Step: {step_result.get('step_name', '')}\n")
            file_handle.write(f"Status: {step_result.get('status', '')}\n")
            file_handle.write(f"Valid: {step_result.get('is_valid', False)}\n")

            if step_result.get("problems"):
                file_handle.write("Problems:\n")
                for problem in step_result["problems"]:
                    severity = problem.get("severity", "").upper()
                    message = problem.get("message", "")
                    file_path = problem.get("file_path", "")
                    line_num = problem.get("line_number", "")

                    location = f" ({file_path}:{line_num})" if file_path else ""
                    file_handle.write(f"  [{severity}] {message}{location}\n")

            file_handle.write("\n")

    @staticmethod
    def setup_logging(log_level: str = "INFO", verbose: bool = False):
        """Setup logging configuration."""
        level = getattr(logging, log_level.upper())
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        if verbose:
            format_str = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"

        logging.basicConfig(level=level, format=format_str)

        # Suppress some noisy loggers
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
