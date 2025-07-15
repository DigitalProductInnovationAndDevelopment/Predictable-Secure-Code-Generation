"""
Helper utilities for code generation system.
"""

import ast
import json
import yaml
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path


class GenerationHelper:
    """Helper utilities for code generation operations."""

    @staticmethod
    def validate_python_syntax(code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Python code syntax.

        Args:
            code: Python code to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Parse error: {str(e)}"

    @staticmethod
    def extract_functions_from_code(code: str) -> List[Dict[str, Any]]:
        """
        Extract function definitions from Python code.

        Args:
            code: Python code to analyze

        Returns:
            List of function information dictionaries
        """
        functions = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": (
                            node.end_lineno
                            if hasattr(node, "end_lineno")
                            else node.lineno
                        ),
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [
                            GenerationHelper._get_decorator_name(dec)
                            for dec in node.decorator_list
                        ],
                        "docstring": ast.get_docstring(node),
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                    }
                    functions.append(func_info)

        except Exception as e:
            logging.error(f"Failed to extract functions: {str(e)}")

        return functions

    @staticmethod
    def extract_classes_from_code(code: str) -> List[Dict[str, Any]]:
        """
        Extract class definitions from Python code.

        Args:
            code: Python code to analyze

        Returns:
            List of class information dictionaries
        """
        classes = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                "name": item.name,
                                "line_start": item.lineno,
                                "line_end": (
                                    item.end_lineno
                                    if hasattr(item, "end_lineno")
                                    else item.lineno
                                ),
                                "args": [arg.arg for arg in item.args.args],
                                "docstring": ast.get_docstring(item),
                                "is_property": any(
                                    GenerationHelper._get_decorator_name(dec)
                                    == "property"
                                    for dec in item.decorator_list
                                ),
                            }
                            methods.append(method_info)

                    class_info = {
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": (
                            node.end_lineno
                            if hasattr(node, "end_lineno")
                            else node.lineno
                        ),
                        "bases": [
                            GenerationHelper._get_name_from_node(base)
                            for base in node.bases
                        ],
                        "decorators": [
                            GenerationHelper._get_decorator_name(dec)
                            for dec in node.decorator_list
                        ],
                        "docstring": ast.get_docstring(node),
                        "methods": methods,
                    }
                    classes.append(class_info)

        except Exception as e:
            logging.error(f"Failed to extract classes: {str(e)}")

        return classes

    @staticmethod
    def extract_imports_from_code(code: str) -> List[str]:
        """
        Extract import statements from Python code.

        Args:
            code: Python code to analyze

        Returns:
            List of import statements
        """
        imports = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_stmt = f"import {alias.name}"
                        if alias.asname:
                            import_stmt += f" as {alias.asname}"
                        imports.append(import_stmt)

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    names = [alias.name for alias in node.names]
                    import_stmt = f"from {module} import {', '.join(names)}"
                    imports.append(import_stmt)

        except Exception as e:
            logging.error(f"Failed to extract imports: {str(e)}")

        return imports

    @staticmethod
    def _get_decorator_name(decorator_node) -> str:
        """Get decorator name from AST node."""
        if isinstance(decorator_node, ast.Name):
            return decorator_node.id
        elif isinstance(decorator_node, ast.Attribute):
            return decorator_node.attr
        elif isinstance(decorator_node, ast.Call):
            return GenerationHelper._get_decorator_name(decorator_node.func)
        else:
            return str(decorator_node)

    @staticmethod
    def _get_name_from_node(node) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{GenerationHelper._get_name_from_node(node.value)}.{node.attr}"
        else:
            return str(node)

    @staticmethod
    def format_code_with_black(code: str) -> str:
        """
        Format Python code using black-style formatting.

        Args:
            code: Python code to format

        Returns:
            Formatted code
        """
        try:
            import black

            formatted = black.format_str(code, mode=black.FileMode())
            return formatted
        except ImportError:
            logging.warning("Black not available, returning original code")
            return code
        except Exception as e:
            logging.error(f"Failed to format code with black: {str(e)}")
            return code

    @staticmethod
    def estimate_code_complexity(code: str) -> float:
        """
        Estimate code complexity using simple metrics.

        Args:
            code: Python code to analyze

        Returns:
            Complexity score (higher = more complex)
        """
        try:
            tree = ast.parse(code)
            complexity = 0

            # Count various complexity indicators
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For)):
                    complexity += 1
                elif isinstance(node, ast.Try):
                    complexity += 1
                elif isinstance(node, ast.FunctionDef):
                    complexity += 0.5
                elif isinstance(node, ast.ClassDef):
                    complexity += 1
                elif isinstance(node, (ast.And, ast.Or)):
                    complexity += 0.5
                elif isinstance(node, ast.ListComp):
                    complexity += 0.5

            # Normalize by number of lines
            lines = len(code.split("\n"))
            if lines > 0:
                complexity = complexity / lines * 10  # Scale to reasonable range

            return min(complexity, 10.0)  # Cap at 10

        except Exception as e:
            logging.error(f"Failed to estimate complexity: {str(e)}")
            return 1.0  # Default complexity

    @staticmethod
    def save_result_to_file(
        result: Dict[str, Any], file_path: str, format_type: str = "json"
    ) -> bool:
        """
        Save result data to file in specified format.

        Args:
            result: Result data to save
            file_path: Path to output file
            format_type: Output format (json, yaml, text)

        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            if format_type.lower() == "json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, default=str)

            elif format_type.lower() == "yaml":
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(
                        result,
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                        indent=2,
                    )

            elif format_type.lower() == "text":
                with open(file_path, "w", encoding="utf-8") as f:
                    if hasattr(result, "get_summary"):
                        f.write(result.get_summary())
                    else:
                        f.write(str(result))
            else:
                logging.error(f"Unsupported format: {format_type}")
                return False

            return True

        except Exception as e:
            logging.error(f"Failed to save result to {file_path}: {str(e)}")
            return False

    @staticmethod
    def load_result_from_file(
        file_path: str, format_type: str = "json"
    ) -> Optional[Dict[str, Any]]:
        """
        Load result data from file.

        Args:
            file_path: Path to input file
            format_type: File format (json, yaml)

        Returns:
            Loaded data or None if failed
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if format_type.lower() == "json":
                    return json.load(f)
                elif format_type.lower() == "yaml":
                    return yaml.safe_load(f)
                else:
                    logging.error(f"Unsupported format for loading: {format_type}")
                    return None

        except Exception as e:
            logging.error(f"Failed to load result from {file_path}: {str(e)}")
            return None

    @staticmethod
    def merge_code_blocks(
        original: str, new_code: str, merge_strategy: str = "append"
    ) -> str:
        """
        Merge new code with existing code.

        Args:
            original: Original code
            new_code: New code to merge
            merge_strategy: How to merge ("append", "prepend", "smart")

        Returns:
            Merged code
        """
        if not original.strip():
            return new_code

        if not new_code.strip():
            return original

        if merge_strategy == "append":
            return original.rstrip() + "\n\n" + new_code
        elif merge_strategy == "prepend":
            return new_code.rstrip() + "\n\n" + original
        elif merge_strategy == "smart":
            # Smart merge: avoid duplicates, maintain structure
            original_lines = set(
                line.strip() for line in original.split("\n") if line.strip()
            )
            new_lines = [
                line
                for line in new_code.split("\n")
                if line.strip() and line.strip() not in original_lines
            ]

            if new_lines:
                return original.rstrip() + "\n\n" + "\n".join(new_lines)
            else:
                return original
        else:
            logging.warning(f"Unknown merge strategy: {merge_strategy}, using append")
            return original.rstrip() + "\n\n" + new_code

    @staticmethod
    def calculate_file_metrics(file_path: str) -> Dict[str, Any]:
        """
        Calculate metrics for a Python file.

        Args:
            file_path: Path to Python file

        Returns:
            Dictionary of file metrics
        """
        metrics = {
            "lines_of_code": 0,
            "blank_lines": 0,
            "comment_lines": 0,
            "function_count": 0,
            "class_count": 0,
            "complexity_score": 0.0,
            "has_docstrings": False,
            "has_type_hints": False,
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            metrics["lines_of_code"] = len([line for line in lines if line.strip()])
            metrics["blank_lines"] = len([line for line in lines if not line.strip()])
            metrics["comment_lines"] = len(
                [line for line in lines if line.strip().startswith("#")]
            )

            # Analyze AST
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics["function_count"] += 1
                    if ast.get_docstring(node):
                        metrics["has_docstrings"] = True
                    # Check for type hints
                    if node.returns or any(arg.annotation for arg in node.args.args):
                        metrics["has_type_hints"] = True

                elif isinstance(node, ast.ClassDef):
                    metrics["class_count"] += 1
                    if ast.get_docstring(node):
                        metrics["has_docstrings"] = True

            metrics["complexity_score"] = GenerationHelper.estimate_code_complexity(
                content
            )

        except Exception as e:
            logging.error(f"Failed to calculate metrics for {file_path}: {str(e)}")

        return metrics
