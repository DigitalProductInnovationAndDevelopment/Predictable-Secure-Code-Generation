"""
Code integrator for applying generated code changes to existing codebases.
"""

import os
import ast
import shutil
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

import sys

sys.path.append(str(Path(__file__).parent.parent))
from models.code_change import CodeChange, ChangeType
from models.requirement_data import RequirementData
from models.generation_result import GenerationResult


class CodeIntegrator:
    """Integrates generated code into existing codebase."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the integrator."""
        self.logger = logger or logging.getLogger(__name__)

    def prepare_output_directory(self, source_path: str, output_path: str) -> bool:
        """
        Prepare output directory by copying source code.

        Args:
            source_path: Path to source code
            output_path: Path to output directory

        Returns:
            True if successful, False otherwise
        """
        try:
            source_path = Path(source_path)
            output_path = Path(output_path)

            # Create output directory if it doesn't exist
            output_path.mkdir(parents=True, exist_ok=True)

            # Copy source to output
            if source_path.is_file():
                shutil.copy2(source_path, output_path)
            else:
                # Copy entire directory structure
                if output_path.exists():
                    shutil.rmtree(output_path)
                shutil.copytree(
                    source_path,
                    output_path,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"),
                )

            self.logger.info(f"Source code copied from {source_path} to {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to prepare output directory: {str(e)}")
            return False

    def apply_code_changes(
        self, changes: List[CodeChange], output_path: str, result: GenerationResult
    ) -> bool:
        """
        Apply a list of code changes to the output directory.

        Args:
            changes: List of code changes to apply
            output_path: Path to output directory
            result: Generation result to update

        Returns:
            True if all changes applied successfully, False otherwise
        """
        output_path = Path(output_path)
        success_count = 0

        self.logger.info(f"Applying {len(changes)} code changes")

        for change in changes:
            try:
                if self._apply_single_change(change, output_path, result):
                    change.mark_applied()
                    success_count += 1
                    self.logger.debug(
                        f"Applied change: {change.change_type.value} to {change.file_path}"
                    )
                else:
                    change.mark_failed("Failed to apply change")
                    result.add_problem(
                        "error",
                        "integration",
                        f"Failed to apply {change.change_type.value} to {change.file_path}",
                        file_path=change.file_path,
                        requirement_id=change.requirement_id,
                    )

            except Exception as e:
                error_msg = f"Error applying change: {str(e)}"
                change.mark_failed(error_msg)
                result.add_problem(
                    "error",
                    "integration",
                    error_msg,
                    file_path=change.file_path,
                    requirement_id=change.requirement_id,
                )
                self.logger.error(
                    f"Error applying change to {change.file_path}: {str(e)}"
                )

        self.logger.info(f"Applied {success_count}/{len(changes)} changes successfully")
        return success_count == len(changes)

    def _apply_single_change(
        self, change: CodeChange, output_path: Path, result: GenerationResult
    ) -> bool:
        """Apply a single code change."""
        target_file = output_path / change.file_path

        if change.change_type == ChangeType.CREATE_FILE:
            return self._create_file(target_file, change.content, result)

        elif change.change_type == ChangeType.MODIFY_FILE:
            return self._modify_file(target_file, change.content, result)

        elif change.change_type == ChangeType.ADD_FUNCTION:
            return self._add_function_to_file(target_file, change, result)

        elif change.change_type == ChangeType.ADD_CLASS:
            return self._add_class_to_file(target_file, change, result)

        elif change.change_type == ChangeType.ADD_METHOD:
            return self._add_method_to_class(target_file, change, result)

        elif change.change_type == ChangeType.ADD_IMPORT:
            return self._add_import_to_file(target_file, change.content, result)

        elif change.change_type == ChangeType.CREATE_TEST:
            return self._create_test_file(target_file, change.content, result)

        else:
            self.logger.error(f"Unknown change type: {change.change_type}")
            return False

    def _create_file(
        self, file_path: Path, content: str, result: GenerationResult
    ) -> bool:
        """Create a new file with the given content."""
        try:
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            result.files_created.append(str(file_path))
            return True

        except Exception as e:
            self.logger.error(f"Failed to create file {file_path}: {str(e)}")
            return False

    def _modify_file(
        self, file_path: Path, new_content: str, result: GenerationResult
    ) -> bool:
        """Replace entire file content."""
        try:
            if not file_path.exists():
                self.logger.error(f"File {file_path} does not exist for modification")
                return False

            # Backup original content
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # Write new content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            if str(file_path) not in result.files_modified:
                result.files_modified.append(str(file_path))
            return True

        except Exception as e:
            self.logger.error(f"Failed to modify file {file_path}: {str(e)}")
            return False

    def _add_function_to_file(
        self, file_path: Path, change: CodeChange, result: GenerationResult
    ) -> bool:
        """Add a function to an existing file."""
        try:
            if not file_path.exists():
                return self._create_file(file_path, change.content, result)

            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # If file is empty or only has imports, add function directly
            if not original_content.strip() or self._only_has_imports(original_content):
                new_content = original_content + "\n\n" + change.content
            else:
                # Add function at the end of the file
                new_content = original_content.rstrip() + "\n\n" + change.content + "\n"

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            if str(file_path) not in result.files_modified:
                result.files_modified.append(str(file_path))
            return True

        except Exception as e:
            self.logger.error(f"Failed to add function to {file_path}: {str(e)}")
            return False

    def _add_class_to_file(
        self, file_path: Path, change: CodeChange, result: GenerationResult
    ) -> bool:
        """Add a class to an existing file."""
        try:
            if not file_path.exists():
                return self._create_file(file_path, change.content, result)

            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # Add class at the end of the file
            new_content = original_content.rstrip() + "\n\n" + change.content + "\n"

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            if str(file_path) not in result.files_modified:
                result.files_modified.append(str(file_path))
            return True

        except Exception as e:
            self.logger.error(f"Failed to add class to {file_path}: {str(e)}")
            return False

    def _add_method_to_class(
        self, file_path: Path, change: CodeChange, result: GenerationResult
    ) -> bool:
        """Add a method to an existing class."""
        try:
            if not file_path.exists():
                self.logger.error(
                    f"File {file_path} does not exist for method addition"
                )
                return False

            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # Parse the AST to find the class
            try:
                tree = ast.parse(original_content)
            except SyntaxError as e:
                self.logger.error(f"Syntax error in {file_path}: {str(e)}")
                return False

            # Find the target class
            target_class = change.target_class
            if not target_class:
                self.logger.error("No target class specified for method addition")
                return False

            class_found = False
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == target_class:
                    class_found = True
                    break

            if not class_found:
                self.logger.error(f"Class {target_class} not found in {file_path}")
                return False

            # Simple approach: add method at the end of the class
            # Find the last line of the class and insert before it
            lines = original_content.split("\n")
            class_indent = self._find_class_indent(lines, target_class)

            if class_indent is None:
                self.logger.error(
                    f"Could not determine indentation for class {target_class}"
                )
                return False

            # Find insertion point (end of class)
            insertion_point = self._find_class_end(lines, target_class, class_indent)

            # Add method with proper indentation
            method_lines = change.content.split("\n")
            indented_method = [
                " " * (class_indent + 4) + line if line.strip() else line
                for line in method_lines
            ]

            # Insert method
            new_lines = (
                lines[:insertion_point]
                + [""]
                + indented_method
                + lines[insertion_point:]
            )
            new_content = "\n".join(new_lines)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            if str(file_path) not in result.files_modified:
                result.files_modified.append(str(file_path))
            return True

        except Exception as e:
            self.logger.error(f"Failed to add method to class in {file_path}: {str(e)}")
            return False

    def _add_import_to_file(
        self, file_path: Path, import_statement: str, result: GenerationResult
    ) -> bool:
        """Add an import statement to a file."""
        try:
            if not file_path.exists():
                return self._create_file(file_path, import_statement + "\n", result)

            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # Check if import already exists
            if import_statement.strip() in original_content:
                return True  # Already exists

            lines = original_content.split("\n")

            # Find the right place to insert the import
            insertion_point = 0

            # Skip shebang and encoding declarations
            for i, line in enumerate(lines):
                if line.startswith("#") and (
                    "coding" in line or "encoding" in line or line.startswith("#!")
                ):
                    insertion_point = i + 1
                elif line.strip().startswith('"""') or line.strip().startswith("'''"):
                    # Skip docstrings
                    quote = '"""' if line.strip().startswith('"""') else "'''"
                    if line.count(quote) >= 2:
                        insertion_point = i + 1
                    else:
                        # Multi-line docstring
                        for j in range(i + 1, len(lines)):
                            if quote in lines[j]:
                                insertion_point = j + 1
                                break
                elif line.strip().startswith("import ") or line.strip().startswith(
                    "from "
                ):
                    # Insert after existing imports
                    insertion_point = i + 1
                elif line.strip() and not line.startswith("#"):
                    # First non-import, non-comment line
                    break

            # Insert import
            new_lines = (
                lines[:insertion_point] + [import_statement] + lines[insertion_point:]
            )
            new_content = "\n".join(new_lines)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            if str(file_path) not in result.files_modified:
                result.files_modified.append(str(file_path))
            return True

        except Exception as e:
            self.logger.error(f"Failed to add import to {file_path}: {str(e)}")
            return False

    def _create_test_file(
        self, file_path: Path, content: str, result: GenerationResult
    ) -> bool:
        """Create a test file."""
        try:
            # Ensure test file is in tests directory
            if "test" not in str(file_path):
                test_dir = file_path.parent / "tests"
                test_dir.mkdir(exist_ok=True)
                file_path = test_dir / f"test_{file_path.name}"

            success = self._create_file(file_path, content, result)
            if success and str(file_path) not in result.tests_generated:
                result.tests_generated.append(str(file_path))
            return success

        except Exception as e:
            self.logger.error(f"Failed to create test file {file_path}: {str(e)}")
            return False

    def _only_has_imports(self, content: str) -> bool:
        """Check if file only contains imports and comments."""
        try:
            tree = ast.parse(content)
            for node in tree.body:
                if not isinstance(node, (ast.Import, ast.ImportFrom)):
                    return False
            return True
        except:
            return False

    def _find_class_indent(self, lines: List[str], class_name: str) -> Optional[int]:
        """Find the indentation level of a class."""
        for line in lines:
            if f"class {class_name}" in line and line.strip().startswith("class"):
                return len(line) - len(line.lstrip())
        return None

    def _find_class_end(
        self, lines: List[str], class_name: str, class_indent: int
    ) -> int:
        """Find the end of a class definition."""
        class_start = -1

        # Find class start
        for i, line in enumerate(lines):
            if f"class {class_name}" in line and line.strip().startswith("class"):
                class_start = i
                break

        if class_start == -1:
            return len(lines)

        # Find class end (next class or function at same or lower indentation level)
        for i in range(class_start + 1, len(lines)):
            line = lines[i]
            if line.strip() == "":
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent <= class_indent and line.strip():
                return i

        return len(lines)
