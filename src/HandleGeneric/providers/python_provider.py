"""
Python language provider implementation.

This module provides Python-specific implementations for code parsing,
validation, and generation.
"""

import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import logging

from ..core.language_provider import (
    LanguageProvider,
    FileMetadata,
    FunctionInfo,
    ClassInfo,
    SyntaxValidationResult,
)


class PythonProvider(LanguageProvider):
    """Language provider for Python."""

    @property
    def language_name(self) -> str:
        return "python"

    @property
    def file_extensions(self) -> Set[str]:
        return {".py", ".pyi", ".pyw"}

    @property
    def comment_prefixes(self) -> List[str]:
        return ["#"]

    def parse_file(self, file_path: Path, content: str) -> FileMetadata:
        """Parse a Python file and extract metadata."""
        try:
            tree = ast.parse(content, filename=str(file_path))
            visitor = PythonASTVisitor()
            visitor.visit(tree)

            return FileMetadata(
                path=str(file_path),
                language=self.language_name,
                size=len(content),
                lines_of_code=len(
                    [
                        line
                        for line in content.split("\n")
                        if line.strip() and not line.strip().startswith("#")
                    ]
                ),
                classes=visitor.classes,
                functions=visitor.functions,
                imports=visitor.imports,
                constants=visitor.constants,
                comments=self._extract_comments(content),
                docstring=visitor.module_docstring,
            )
        except SyntaxError as e:
            logging.getLogger(__name__).error(f"Syntax error in {file_path}: {e}")
            # Return basic metadata even if parsing fails
            return FileMetadata(
                path=str(file_path),
                language=self.language_name,
                size=len(content),
                lines_of_code=len(content.split("\n")),
                classes=[],
                functions=[],
                imports=[],
                constants={},
                comments=self._extract_comments(content),
                docstring=None,
            )

    def validate_syntax(
        self, file_path: Path, content: str
    ) -> tuple[SyntaxValidationResult, Optional[str]]:
        """Validate Python syntax."""
        try:
            ast.parse(content, filename=str(file_path))
            return SyntaxValidationResult.VALID, None
        except SyntaxError as e:
            error_msg = f"Syntax error in {file_path} line {e.lineno}: {e.msg}"
            return SyntaxValidationResult.INVALID, error_msg
        except Exception as e:
            error_msg = f"Error validating {file_path}: {str(e)}"
            return SyntaxValidationResult.ERROR, error_msg

    def generate_code_prompt(self, requirement: str, context: Dict[str, Any]) -> str:
        """Generate a Python-specific prompt for AI code generation."""
        return f"""You are an expert Python developer. Generate clean, well-documented Python code based on requirements.

Requirement: {requirement}

Context: {context.get('context', '')}

Guidelines:
- Follow PEP 8 style guidelines
- Include proper type hints
- Add comprehensive docstrings
- Handle exceptions appropriately
- Write clean, readable code
- Include necessary imports
- Provide only the Python code without markdown formatting

Generate the Python code:"""

    def extract_generated_code(self, ai_response: str) -> str:
        """Extract clean Python code from AI response."""
        # Remove markdown code blocks
        code_pattern = r"```(?:python)?\s*(.*?)```"
        matches = re.findall(code_pattern, ai_response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # If no code blocks found, try to extract Python-looking code
        lines = ai_response.split("\n")
        code_lines = []
        in_code = False

        for line in lines:
            # Start capturing when we see import, def, class, etc.
            if any(
                line.strip().startswith(keyword)
                for keyword in ["import ", "from ", "def ", "class ", "async def "]
            ):
                in_code = True

            if in_code and line.strip():
                code_lines.append(line)
            elif in_code and not line.strip():
                code_lines.append(line)  # Keep empty lines in code

        return "\n".join(code_lines).strip()

    def get_test_framework_commands(self) -> List[str]:
        """Get commands to run Python tests."""
        return ["python", "-m", "pytest", "-v"]

    def generate_test_code(
        self, function_info: FunctionInfo, context: Dict[str, Any]
    ) -> str:
        """Generate test code for a Python function."""
        function_name = function_info.name
        test_name = f"test_{function_name}"

        return f'''import pytest
from {context.get("module_name", "main")} import {function_name}


def {test_name}():
    """Test for {function_name} function."""
    # TODO: Add test cases
    # Example:
    # result = {function_name}()
    # assert result == expected_value
    pass


def {test_name}_edge_cases():
    """Test edge cases for {function_name} function."""
    # TODO: Add edge case tests
    pass


def {test_name}_error_handling():
    """Test error handling for {function_name} function."""
    # TODO: Add error handling tests
    pass
'''

    def get_standard_imports(self) -> List[str]:
        """Get standard Python imports."""
        return [
            "import os",
            "import sys",
            "import logging",
            "from typing import Dict, List, Optional, Any",
            "from pathlib import Path",
        ]

    def get_file_template(self, template_type: str = "basic") -> str:
        """Get Python file template."""
        templates = {
            "basic": '''#!/usr/bin/env python3
"""
Module description here.
"""

import logging
from typing import Any


def main():
    """Main function."""
    pass


if __name__ == "__main__":
    main()
''',
            "class": '''#!/usr/bin/env python3
"""
Module with class definition.
"""

from typing import Any, Optional


class ClassName:
    """Class description here."""
    
    def __init__(self):
        """Initialize the class."""
        pass
    
    def method_name(self) -> Any:
        """Method description here."""
        pass
''',
            "module": '''#!/usr/bin/env python3
"""
Module description here.

This module provides functionality for...
"""

import logging
from typing import Dict, List, Optional, Any

# Module-level constants
CONSTANT_NAME = "value"

# Configure logging
logger = logging.getLogger(__name__)


def function_name() -> Any:
    """Function description here."""
    pass
''',
        }
        return templates.get(template_type, templates["basic"])

    def _extract_comments(self, content: str) -> List[str]:
        """Extract comments from Python code."""
        comments = []
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#"):
                comments.append(stripped[1:].strip())
        return comments


class PythonASTVisitor(ast.NodeVisitor):
    """AST visitor for extracting Python metadata."""

    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = []
        self.constants = {}
        self.module_docstring = None
        self._class_stack = []

    def visit_Module(self, node):
        """Visit module node to extract module docstring."""
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            self.module_docstring = node.body[0].value.value
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Visit function definition."""
        self._visit_function(node, is_async=False)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Visit async function definition."""
        self._visit_function(node, is_async=True)
        self.generic_visit(node)

    def _visit_function(self, node, is_async=False):
        """Helper to visit function definitions."""
        # Extract docstring
        docstring = None
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            docstring = node.body[0].value.value

        # Extract parameters
        parameters = []
        for arg in node.args.args:
            param_name = arg.arg
            if arg.annotation:
                param_name += f": {ast.unparse(arg.annotation)}"
            parameters.append(param_name)

        # Extract return type
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)

        # Extract decorators
        decorators = []
        for decorator in node.decorator_list:
            decorators.append(ast.unparse(decorator))

        # Determine visibility
        visibility = "private" if node.name.startswith("_") else "public"

        function_info = FunctionInfo(
            name=node.name,
            parameters=parameters,
            docstring=docstring,
            start_line=node.lineno,
            end_line=getattr(node, "end_lineno", node.lineno),
            decorators=decorators,
            return_type=return_type,
            is_async=is_async,
            visibility=visibility,
            is_static="staticmethod" in [d.strip() for d in decorators],
        )

        # Add to appropriate collection
        if self._class_stack:
            self._class_stack[-1].methods.append(function_info)
        else:
            self.functions.append(function_info)

    def visit_ClassDef(self, node):
        """Visit class definition."""
        # Extract docstring
        docstring = None
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            docstring = node.body[0].value.value

        # Extract base classes
        base_classes = []
        for base in node.bases:
            base_classes.append(ast.unparse(base))

        # Extract decorators
        decorators = []
        for decorator in node.decorator_list:
            decorators.append(ast.unparse(decorator))

        # Determine visibility
        visibility = "private" if node.name.startswith("_") else "public"

        class_info = ClassInfo(
            name=node.name,
            docstring=docstring,
            start_line=node.lineno,
            end_line=getattr(node, "end_lineno", node.lineno),
            base_classes=base_classes,
            decorators=decorators,
            methods=[],
            visibility=visibility,
        )

        self._class_stack.append(class_info)
        self.classes.append(class_info)

        self.generic_visit(node)
        self._class_stack.pop()

    def visit_Import(self, node):
        """Visit import statement."""
        for alias in node.names:
            self.imports.append(f"import {alias.name}")

    def visit_ImportFrom(self, node):
        """Visit from import statement."""
        module = node.module or ""
        for alias in node.names:
            self.imports.append(f"from {module} import {alias.name}")

    def visit_Assign(self, node):
        """Visit assignment to extract constants."""
        # Only capture module-level assignments that look like constants
        if (
            not self._class_stack
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id.isupper()
        ):

            try:
                if isinstance(node.value, ast.Constant):
                    self.constants[node.targets[0].id] = node.value.value
                else:
                    self.constants[node.targets[0].id] = ast.unparse(node.value)
            except:
                pass  # Skip if we can't parse the value

        self.generic_visit(node)
