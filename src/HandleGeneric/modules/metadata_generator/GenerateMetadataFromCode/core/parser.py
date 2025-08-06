"""
Code parser for extracting metadata from Python source files using AST.
"""

import ast
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
import logging

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from utils.helpers import PathHelper


class FunctionInfo:
    """Container for function metadata."""

    def __init__(
        self,
        name: str,
        args: List[str],
        docstring: Optional[str] = None,
        start_line: int = 0,
        end_line: int = 0,
        decorators: List[str] = None,
        return_type: Optional[str] = None,
        is_async: bool = False,
    ):
        self.name = name
        self.args = args or []
        self.docstring = docstring
        self.start_line = start_line
        self.end_line = end_line
        self.decorators = decorators or []
        self.return_type = return_type
        self.is_async = is_async

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "args": self.args,
            "start_line": self.start_line,
            "end_line": self.end_line,
        }

        if self.docstring:
            result["docstring"] = self.docstring
        if self.decorators:
            result["decorators"] = self.decorators
        if self.return_type:
            result["return_type"] = self.return_type
        if self.is_async:
            result["is_async"] = self.is_async

        return result


class ClassInfo:
    """Container for class metadata."""

    def __init__(
        self,
        name: str,
        docstring: Optional[str] = None,
        start_line: int = 0,
        end_line: int = 0,
        base_classes: List[str] = None,
        decorators: List[str] = None,
        methods: List[FunctionInfo] = None,
    ):
        self.name = name
        self.docstring = docstring
        self.start_line = start_line
        self.end_line = end_line
        self.base_classes = base_classes or []
        self.decorators = decorators or []
        self.methods = methods or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "methods": [method.to_dict() for method in self.methods],
        }

        if self.docstring:
            result["docstring"] = self.docstring
        if self.base_classes:
            result["base_classes"] = self.base_classes
        if self.decorators:
            result["decorators"] = self.decorators

        return result


class CodeParser:
    """Parser for extracting metadata from Python source code using AST."""

    def __init__(self, config: Config = None):
        """
        Initialize the code parser.

        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)

    def parse_file(self, file_path: Path, content: str) -> Dict[str, Any]:
        """
        Parse a Python file and extract metadata.

        Args:
            file_path: Path to the file
            content: File content as string

        Returns:
            Dictionary containing extracted metadata
        """
        try:
            tree = ast.parse(content, filename=str(file_path))

            visitor = CodeVisitor(self.config)
            visitor.visit(tree)

            return {
                "path": str(file_path),
                "functions": [func.to_dict() for func in visitor.functions],
                "classes": [cls.to_dict() for cls in visitor.classes],
                "imports": visitor.imports,
            }

        except SyntaxError as e:
            self.logger.warning(f"Syntax error in {file_path}: {e}")
            return {
                "path": str(file_path),
                "functions": [],
                "classes": [],
                "imports": [],
                "error": f"Syntax error: {e}",
            }
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
            return {
                "path": str(file_path),
                "functions": [],
                "classes": [],
                "imports": [],
                "error": f"Parse error: {e}",
            }


class CodeVisitor(ast.NodeVisitor):
    """AST visitor for extracting code elements."""

    def __init__(self, config: Config):
        """
        Initialize the visitor.

        Args:
            config: Configuration object
        """
        self.config = config
        self.functions: List[FunctionInfo] = []
        self.classes: List[ClassInfo] = []
        self.imports: List[str] = []
        self._current_class: Optional[str] = None

    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statements."""
        for alias in node.names:
            import_name = alias.asname if alias.asname else alias.name
            self.imports.append(import_name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from-import statements."""
        module = node.module or ""
        for alias in node.names:
            if alias.name == "*":
                self.imports.append(f"{module}.*")
            else:
                import_name = alias.asname if alias.asname else alias.name
                if module:
                    self.imports.append(f"{module}.{import_name}")
                else:
                    self.imports.append(import_name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        self._process_function(node, is_async=False)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions."""
        self._process_function(node, is_async=True)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        if self._should_include_class(node.name):
            # Extract class metadata
            docstring = ast.get_docstring(node)
            base_classes = []
            decorators = []

            # Extract base classes
            if self.config.extract_base_classes:
                for base in node.bases:
                    base_classes.append(self._get_name_from_node(base))

            # Extract decorators
            if self.config.extract_decorators:
                for decorator in node.decorator_list:
                    decorators.append(self._get_name_from_node(decorator))

            # Create class info
            class_info = ClassInfo(
                name=node.name,
                docstring=docstring if self.config.extract_docstrings else None,
                start_line=node.lineno,
                end_line=node.end_lineno or node.lineno,
                base_classes=base_classes,
                decorators=decorators,
            )

            # Process methods
            old_class = self._current_class
            self._current_class = node.name

            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if self._should_include_method(child.name):
                        func_info = self._extract_function_info(
                            child, is_async=isinstance(child, ast.AsyncFunctionDef)
                        )
                        class_info.methods.append(func_info)

            self._current_class = old_class
            self.classes.append(class_info)

        self.generic_visit(node)

    def _process_function(self, node, is_async: bool = False) -> None:
        """Process a function node."""
        if self._current_class is None and self._should_include_function(node.name):
            func_info = self._extract_function_info(node, is_async)
            self.functions.append(func_info)

    def _extract_function_info(self, node, is_async: bool = False) -> FunctionInfo:
        """Extract function information from AST node."""
        # Extract arguments
        args = []
        for arg in node.args.args:
            arg_name = arg.arg
            if (
                hasattr(arg, "annotation")
                and arg.annotation
                and self.config.extract_type_hints
            ):
                arg_type = self._get_name_from_node(arg.annotation)
                args.append(f"{arg_name}: {arg_type}")
            else:
                args.append(arg_name)

        # Extract docstring
        docstring = ast.get_docstring(node) if self.config.extract_docstrings else None

        # Extract decorators
        decorators = []
        if self.config.extract_decorators:
            for decorator in node.decorator_list:
                decorators.append(self._get_name_from_node(decorator))

        # Extract return type
        return_type = None
        if hasattr(node, "returns") and node.returns and self.config.extract_type_hints:
            return_type = self._get_name_from_node(node.returns)

        return FunctionInfo(
            name=node.name,
            args=args,
            docstring=docstring,
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            decorators=decorators,
            return_type=return_type,
            is_async=is_async,
        )

    def _should_include_function(self, name: str) -> bool:
        """Check if a function should be included."""
        if name.startswith("_") and not self.config.include_private_methods:
            if not (
                name.startswith("__")
                and name.endswith("__")
                and self.config.include_magic_methods
            ):
                return False
        return True

    def _should_include_method(self, name: str) -> bool:
        """Check if a method should be included."""
        return self._should_include_function(name)

    def _should_include_class(self, name: str) -> bool:
        """Check if a class should be included."""
        if name.startswith("_") and not self.config.include_private_methods:
            return False
        return True

    def _get_name_from_node(self, node) -> str:
        """Extract name from an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name_from_node(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Call):
            return self._get_name_from_node(node.func)
        else:
            return str(type(node).__name__)
