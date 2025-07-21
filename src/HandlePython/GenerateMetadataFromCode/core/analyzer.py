"""
Code analyzer for identifying entry points and code relationships.
"""

import ast
from pathlib import Path
from typing import List, Dict, Any, Set, Optional, Tuple
import logging

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from utils.helpers import PathHelper


class CodeAnalyzer:
    """Analyzer for identifying entry points and code relationships."""

    def __init__(self, config: Config = None):
        """
        Initialize the code analyzer.

        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)

    def analyze_project(
        self, parsed_files: List[Dict[str, Any]], project_path: Path
    ) -> Dict[str, Any]:
        """
        Analyze a project and identify entry points and relationships.

        Args:
            parsed_files: List of parsed file metadata
            project_path: Root path of the project

        Returns:
            Analysis results including entry points
        """
        entry_points = self._find_entry_points(parsed_files, project_path)
        dependencies = self._analyze_dependencies(parsed_files)
        complexity_metrics = self._calculate_complexity_metrics(parsed_files)

        return {
            "entry_points": entry_points,
            "dependencies": dependencies,
            "metrics": complexity_metrics,
        }

    def _find_entry_points(
        self, parsed_files: List[Dict[str, Any]], project_path: Path
    ) -> List[str]:
        """
        Find entry points in the project.

        Args:
            parsed_files: List of parsed file metadata
            project_path: Root path of the project

        Returns:
            List of entry point descriptions
        """
        entry_points = []

        for file_data in parsed_files:
            file_path = Path(file_data["path"])
            relative_path = PathHelper.get_relative_path(file_path, project_path)

            # Check if file is a potential entry point file
            if self._is_entry_point_file(file_path):
                entry_functions = self._find_entry_functions_in_file(file_data)
                for func_name in entry_functions:
                    entry_points.append(f"{relative_path} -> {func_name}()")

            # Check for if __name__ == "__main__" pattern
            if self._has_main_guard(file_path):
                entry_points.append(f"{relative_path} -> __main__")

        return entry_points

    def _is_entry_point_file(self, file_path: Path) -> bool:
        """
        Check if a file is likely an entry point file.

        Args:
            file_path: Path to check

        Returns:
            True if file is likely an entry point
        """
        filename = file_path.name.lower()
        return filename in [name.lower() for name in self.config.entry_point_files]

    def _find_entry_functions_in_file(self, file_data: Dict[str, Any]) -> List[str]:
        """
        Find entry point functions in a file.

        Args:
            file_data: Parsed file metadata

        Returns:
            List of entry point function names
        """
        entry_functions = []

        for func in file_data.get("functions", []):
            func_name = func["name"]
            if func_name.lower() in [
                name.lower() for name in self.config.entry_point_functions
            ]:
                entry_functions.append(func_name)

        # Also check methods in classes
        for cls in file_data.get("classes", []):
            for method in cls.get("methods", []):
                method_name = method["name"]
                if method_name.lower() in [
                    name.lower() for name in self.config.entry_point_functions
                ]:
                    entry_functions.append(f"{cls['name']}.{method_name}")

        return entry_functions

    def _has_main_guard(self, file_path: Path) -> bool:
        """
        Check if a file has the if __name__ == "__main__" pattern.

        Args:
            file_path: Path to the file

        Returns:
            True if file has main guard
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Simple string check - could be enhanced with AST analysis
            return (
                'if __name__ == "__main__"' in content
                or "if __name__ == '__main__'" in content
            )

        except Exception as e:
            self.logger.warning(f"Could not check main guard in {file_path}: {e}")
            return False

    def _analyze_dependencies(
        self, parsed_files: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze dependencies between files.

        Args:
            parsed_files: List of parsed file metadata

        Returns:
            Dependency analysis results
        """
        internal_imports = set()
        external_imports = set()

        for file_data in parsed_files:
            for import_name in file_data.get("imports", []):
                # Simple heuristic: if import doesn't contain dots or is local, it's internal
                if self._is_internal_import(import_name, parsed_files):
                    internal_imports.add(import_name)
                else:
                    external_imports.add(import_name)

        return {
            "internal_dependencies": sorted(list(internal_imports)),
            "external_dependencies": sorted(list(external_imports)),
            "total_internal": len(internal_imports),
            "total_external": len(external_imports),
        }

    def _is_internal_import(
        self, import_name: str, parsed_files: List[Dict[str, Any]]
    ) -> bool:
        """
        Determine if an import is internal to the project.

        Args:
            import_name: Name of the import
            parsed_files: List of parsed file metadata

        Returns:
            True if import is internal
        """
        # Extract module names from file paths
        internal_modules = set()
        for file_data in parsed_files:
            file_path = Path(file_data["path"])
            if file_path.name == "__init__.py":
                # Package import
                internal_modules.add(file_path.parent.name)
            else:
                # Module import
                internal_modules.add(file_path.stem)

        # Check if import matches any internal module
        import_base = import_name.split(".")[0]
        return import_base in internal_modules

    def _calculate_complexity_metrics(
        self, parsed_files: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate complexity metrics for the project.

        Args:
            parsed_files: List of parsed file metadata

        Returns:
            Complexity metrics
        """
        total_files = len(parsed_files)
        total_functions = 0
        total_classes = 0
        total_methods = 0
        lines_of_code = 0

        function_complexity = []
        class_complexity = []

        for file_data in parsed_files:
            functions = file_data.get("functions", [])
            classes = file_data.get("classes", [])

            total_functions += len(functions)
            total_classes += len(classes)

            # Calculate function complexity (based on line count)
            for func in functions:
                func_lines = func.get("end_line", 0) - func.get("start_line", 0) + 1
                function_complexity.append(func_lines)
                lines_of_code += func_lines

            # Calculate class complexity
            for cls in classes:
                cls_lines = cls.get("end_line", 0) - cls.get("start_line", 0) + 1
                class_complexity.append(cls_lines)
                lines_of_code += cls_lines

                methods = cls.get("methods", [])
                total_methods += len(methods)

        avg_function_complexity = (
            sum(function_complexity) / len(function_complexity)
            if function_complexity
            else 0
        )

        avg_class_complexity = (
            sum(class_complexity) / len(class_complexity) if class_complexity else 0
        )

        return {
            "total_files": total_files,
            "total_functions": total_functions,
            "total_classes": total_classes,
            "total_methods": total_methods,
            "estimated_lines_of_code": lines_of_code,
            "average_function_complexity": round(avg_function_complexity, 2),
            "average_class_complexity": round(avg_class_complexity, 2),
            "functions_per_file": (
                round(total_functions / total_files, 2) if total_files > 0 else 0
            ),
            "classes_per_file": (
                round(total_classes / total_files, 2) if total_files > 0 else 0
            ),
        }
