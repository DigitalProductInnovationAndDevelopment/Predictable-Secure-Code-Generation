"""
JavaScript language provider implementation.

This module provides JavaScript-specific implementations for code parsing,
validation, and generation.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import logging

from ...core.language import (
    LanguageProvider,
    FileMetadata,
    FunctionInfo,
    ClassInfo,
    SyntaxValidationResult,
)


class JavaScriptProvider(LanguageProvider):
    """Language provider for JavaScript."""

    @property
    def language_name(self) -> str:
        return "javascript"

    @property
    def file_extensions(self) -> Set[str]:
        return {".js", ".jsx", ".mjs"}

    @property
    def comment_prefixes(self) -> List[str]:
        return ["//", "/*"]

    def parse_file(self, file_path: Path, content: str) -> FileMetadata:
        """Parse a JavaScript file and extract metadata."""
        try:
            # Basic parsing using regex patterns (in production, consider using a proper JS parser)
            functions = self._extract_functions(content)
            classes = self._extract_classes(content)
            imports = self._extract_imports(content)
            constants = self._extract_constants(content)
            comments = self._extract_comments(content)

            return FileMetadata(
                path=str(file_path),
                language=self.language_name,
                size=len(content),
                lines_of_code=len(
                    [
                        line
                        for line in content.split("\n")
                        if line.strip()
                        and not line.strip().startswith("//")
                        and not line.strip().startswith("/*")
                    ]
                ),
                classes=classes,
                functions=functions,
                imports=imports,
                constants=constants,
                comments=comments,
                docstring=self._extract_file_header_comment(content),
            )
        except Exception as e:
            logging.getLogger(__name__).error(f"Error parsing {file_path}: {e}")
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
        """Validate JavaScript syntax using Node.js if available."""
        try:
            # Try to validate with Node.js
            result = subprocess.run(
                ["node", "--check", "-"],
                input=content,
                text=True,
                capture_output=True,
                timeout=10,
            )

            if result.returncode == 0:
                return SyntaxValidationResult.VALID, None
            else:
                return SyntaxValidationResult.INVALID, result.stderr.strip()

        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback to basic regex validation
            return self._basic_syntax_check(content)

    def _basic_syntax_check(
        self, content: str
    ) -> tuple[SyntaxValidationResult, Optional[str]]:
        """Basic syntax validation using regex patterns."""
        # Check for balanced braces
        brace_count = content.count("{") - content.count("}")
        if brace_count != 0:
            return SyntaxValidationResult.INVALID, "Unbalanced braces"

        # Check for balanced parentheses
        paren_count = content.count("(") - content.count(")")
        if paren_count != 0:
            return SyntaxValidationResult.INVALID, "Unbalanced parentheses"

        # Check for balanced brackets
        bracket_count = content.count("[") - content.count("]")
        if bracket_count != 0:
            return SyntaxValidationResult.INVALID, "Unbalanced brackets"

        return SyntaxValidationResult.VALID, None

    def generate_code_prompt(self, requirement: str, context: Dict[str, Any]) -> str:
        """Generate a JavaScript-specific prompt for AI code generation."""
        return f"""You are an expert JavaScript developer. Generate clean, well-documented JavaScript code based on requirements.

Requirement: {requirement}

Context: {context.get('context', '')}

Guidelines:
- Use modern ES6+ features
- Include proper JSDoc comments
- Handle errors appropriately
- Write clean, readable code
- Follow JavaScript best practices
- Include necessary imports/requires
- Provide only the JavaScript code without markdown formatting

Generate the JavaScript code:"""

    def extract_generated_code(self, ai_response: str) -> str:
        """Extract clean JavaScript code from AI response."""
        # Remove markdown code blocks
        code_pattern = r"```(?:javascript|js)?\s*(.*?)```"
        matches = re.findall(code_pattern, ai_response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # If no code blocks found, try to extract JS-looking code
        lines = ai_response.split("\n")
        code_lines = []
        in_code = False

        for line in lines:
            # Start capturing when we see import, function, class, etc.
            if any(
                line.strip().startswith(keyword)
                for keyword in [
                    "import ",
                    "export ",
                    "function ",
                    "class ",
                    "const ",
                    "let ",
                    "var ",
                ]
            ):
                in_code = True

            if in_code and line.strip():
                code_lines.append(line)
            elif in_code and not line.strip():
                code_lines.append(line)  # Keep empty lines in code

        return "\n".join(code_lines).strip()

    def get_test_framework_commands(self) -> List[str]:
        """Get commands to run JavaScript tests."""
        return ["npm", "test"]

    def generate_test_code(
        self, function_info: FunctionInfo, context: Dict[str, Any]
    ) -> str:
        """Generate test code for a JavaScript function."""
        function_name = function_info.name

        return f"""const {{ {function_name} }} = require('./{context.get("module_name", "main")}');

describe('{function_name}', () => {{
    test('should work correctly', () => {{
        // TODO: Add test cases
        // const result = {function_name}();
        // expect(result).toBe(expectedValue);
    }});

    test('should handle edge cases', () => {{
        // TODO: Add edge case tests
    }});

    test('should handle errors', () => {{
        // TODO: Add error handling tests
    }});
}});
"""

    def get_standard_imports(self) -> List[str]:
        """Get standard JavaScript imports."""
        return [
            "const fs = require('fs');",
            "const path = require('path');",
            "const util = require('util');",
        ]

    def get_file_template(self, template_type: str = "basic") -> str:
        """Get JavaScript file template."""
        templates = {
            "basic": """/**
 * @fileoverview Description of the module
 */

/**
 * Main function
 */
function main() {
    // Implementation here
}

module.exports = { main };
""",
            "class": """/**
 * @fileoverview Class definition module
 */

/**
 * Class description
 */
class ClassName {
    /**
     * Create a new instance
     */
    constructor() {
        // Initialization
    }

    /**
     * Method description
     * @returns {*} Return value description
     */
    methodName() {
        // Implementation
    }
}

module.exports = ClassName;
""",
            "module": """/**
 * @fileoverview Module description
 * 
 * This module provides functionality for...
 */

const fs = require('fs');
const path = require('path');

// Constants
const CONSTANT_NAME = 'value';

/**
 * Function description
 * @param {*} param Parameter description
 * @returns {*} Return value description
 */
function functionName(param) {
    // Implementation
}

module.exports = {
    functionName,
    CONSTANT_NAME
};
""",
        }
        return templates.get(template_type, templates["basic"])

    def _extract_functions(self, content: str) -> List[FunctionInfo]:
        """Extract function definitions from JavaScript code."""
        functions = []

        # Regular function declarations
        function_pattern = r"function\s+(\w+)\s*\(([^)]*)\)\s*\{"
        matches = re.finditer(function_pattern, content)

        for match in matches:
            name = match.group(1)
            params_str = match.group(2).strip()
            parameters = [p.strip() for p in params_str.split(",") if p.strip()]

            # Try to find the line number
            line_num = content[: match.start()].count("\n") + 1

            functions.append(
                FunctionInfo(
                    name=name,
                    parameters=parameters,
                    start_line=line_num,
                    visibility="public",
                )
            )

        # Arrow functions (basic pattern)
        arrow_pattern = r"(?:const|let|var)\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>"
        matches = re.finditer(arrow_pattern, content)

        for match in matches:
            name = match.group(1)
            params_str = match.group(2).strip()
            parameters = [p.strip() for p in params_str.split(",") if p.strip()]

            line_num = content[: match.start()].count("\n") + 1

            functions.append(
                FunctionInfo(
                    name=name,
                    parameters=parameters,
                    start_line=line_num,
                    visibility="public",
                )
            )

        return functions

    def _extract_classes(self, content: str) -> List[ClassInfo]:
        """Extract class definitions from JavaScript code."""
        classes = []

        class_pattern = r"class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{"
        matches = re.finditer(class_pattern, content)

        for match in matches:
            name = match.group(1)
            base_class = match.group(2)
            base_classes = [base_class] if base_class else []

            line_num = content[: match.start()].count("\n") + 1

            classes.append(
                ClassInfo(
                    name=name,
                    start_line=line_num,
                    base_classes=base_classes,
                    visibility="public",
                )
            )

        return classes

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from JavaScript code."""
        imports = []

        # ES6 imports
        import_pattern = r'import\s+.*?from\s+[\'"][^\'\"]+[\'"]'
        matches = re.findall(import_pattern, content)
        imports.extend(matches)

        # CommonJS requires
        require_pattern = r'(?:const|let|var)\s+.*?=\s*require\([\'"][^\'\"]+[\'\"]\)'
        matches = re.findall(require_pattern, content)
        imports.extend(matches)

        return imports

    def _extract_constants(self, content: str) -> Dict[str, Any]:
        """Extract constant definitions from JavaScript code."""
        constants = {}

        const_pattern = r"const\s+([A-Z_][A-Z0-9_]*)\s*=\s*([^;]+);?"
        matches = re.findall(const_pattern, content)

        for name, value in matches:
            constants[name] = value.strip()

        return constants

    def _extract_comments(self, content: str) -> List[str]:
        """Extract comments from JavaScript code."""
        comments = []

        # Single-line comments
        single_line_pattern = r"//\s*(.*)"
        matches = re.findall(single_line_pattern, content)
        comments.extend(matches)

        # Multi-line comments
        multi_line_pattern = r"/\*(.*?)\*/"
        matches = re.findall(multi_line_pattern, content, re.DOTALL)
        for match in matches:
            # Split multi-line comments into individual lines
            lines = match.strip().split("\n")
            comments.extend(
                [line.strip().lstrip("*").strip() for line in lines if line.strip()]
            )

        return comments

    def _extract_file_header_comment(self, content: str) -> Optional[str]:
        """Extract file header comment/docstring."""
        # Look for @fileoverview comment at the beginning
        fileoverview_pattern = (
            r"/\*\*\s*\n\s*\*\s*@fileoverview\s+(.*?)(?:\n\s*\*\s*@|\*\/)"
        )
        match = re.search(fileoverview_pattern, content, re.DOTALL)

        if match:
            return match.group(1).strip()

        # Look for first multi-line comment
        first_comment_pattern = r"^\s*/\*\*(.*?)\*/"
        match = re.search(first_comment_pattern, content, re.DOTALL)

        if match:
            lines = match.group(1).strip().split("\n")
            cleaned_lines = [line.strip().lstrip("*").strip() for line in lines]
            return "\n".join(cleaned_lines).strip()

        return None
