"""
TypeScript language provider implementation.

This module provides TypeScript-specific implementations for code parsing,
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


class TypeScriptProvider(LanguageProvider):
    """Language provider for TypeScript."""

    @property
    def language_name(self) -> str:
        return "typescript"

    @property
    def file_extensions(self) -> Set[str]:
        return {".ts", ".tsx"}

    @property
    def comment_prefixes(self) -> List[str]:
        return ["//", "/*"]

    def parse_file(self, file_path: Path, content: str) -> FileMetadata:
        """Parse a TypeScript file and extract metadata."""
        try:
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
        """Validate TypeScript syntax using tsc if available."""
        try:
            # Try to validate with TypeScript compiler
            result = subprocess.run(
                ["npx", "tsc", "--noEmit", "--skipLibCheck", "-"],
                input=content,
                text=True,
                capture_output=True,
                timeout=15,
            )

            if result.returncode == 0:
                return SyntaxValidationResult.VALID, None
            else:
                return SyntaxValidationResult.INVALID, result.stderr.strip()

        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback to basic syntax check
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
        """Generate a TypeScript-specific prompt for AI code generation."""
        return f"""You are an expert TypeScript developer. Generate clean, well-documented TypeScript code based on requirements.

Requirement: {requirement}

Context: {context.get('context', '')}

Guidelines:
- Use modern TypeScript features and strict typing
- Include proper TSDoc comments
- Define appropriate interfaces and types
- Handle errors appropriately with proper typing
- Write clean, readable code
- Follow TypeScript best practices
- Include necessary imports
- Provide only the TypeScript code without markdown formatting

Generate the TypeScript code:"""

    def extract_generated_code(self, ai_response: str) -> str:
        """Extract clean TypeScript code from AI response."""
        # Remove markdown code blocks
        code_pattern = r"```(?:typescript|ts)?\s*(.*?)```"
        matches = re.findall(code_pattern, ai_response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # If no code blocks found, try to extract TS-looking code
        lines = ai_response.split("\n")
        code_lines = []
        in_code = False

        for line in lines:
            # Start capturing when we see TS keywords
            if any(
                line.strip().startswith(keyword)
                for keyword in [
                    "import ",
                    "export ",
                    "function ",
                    "class ",
                    "interface ",
                    "type ",
                    "const ",
                    "let ",
                    "var ",
                    "enum ",
                    "namespace ",
                ]
            ):
                in_code = True

            if in_code and line.strip():
                code_lines.append(line)
            elif in_code and not line.strip():
                code_lines.append(line)  # Keep empty lines in code

        return "\n".join(code_lines).strip()

    def get_test_framework_commands(self) -> List[str]:
        """Get commands to run TypeScript tests."""
        return ["npm", "run", "test"]

    def generate_test_code(
        self, function_info: FunctionInfo, context: Dict[str, Any]
    ) -> str:
        """Generate test code for a TypeScript function."""
        function_name = function_info.name

        return f"""import {{ {function_name} }} from './{context.get("module_name", "main")}';

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
        """Get standard TypeScript imports."""
        return [
            "import * as fs from 'fs';",
            "import * as path from 'path';",
            "import * as util from 'util';",
        ]

    def get_file_template(self, template_type: str = "basic") -> str:
        """Get TypeScript file template."""
        templates = {
            "basic": """/**
 * @fileoverview Description of the module
 */

/**
 * Main function
 */
function main(): void {
    // Implementation here
}

export { main };
""",
            "class": """/**
 * @fileoverview Class definition module
 */

/**
 * Interface for class options
 */
interface ClassOptions {
    // Define options here
}

/**
 * Class description
 */
class ClassName {
    private readonly options: ClassOptions;

    /**
     * Create a new instance
     * @param options - Configuration options
     */
    constructor(options: ClassOptions) {
        this.options = options;
    }

    /**
     * Method description
     * @returns Return value description
     */
    public methodName(): any {
        // Implementation
    }
}

export { ClassName, ClassOptions };
""",
            "module": """/**
 * @fileoverview Module description
 * 
 * This module provides functionality for...
 */

import * as fs from 'fs';
import * as path from 'path';

// Type definitions
interface ConfigType {
    // Define interface here
}

// Constants
const CONSTANT_NAME: string = 'value';

/**
 * Function description
 * @param param - Parameter description
 * @returns Return value description
 */
function functionName(param: any): any {
    // Implementation
}

export {
    functionName,
    CONSTANT_NAME,
    ConfigType
};
""",
        }
        return templates.get(template_type, templates["basic"])

    def _extract_functions(self, content: str) -> List[FunctionInfo]:
        """Extract function definitions from TypeScript code."""
        functions = []

        # Function declarations with type annotations
        function_pattern = r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)\s*:\s*([^{]+)?\s*\{"
        matches = re.finditer(function_pattern, content)

        for match in matches:
            name = match.group(1)
            params_str = match.group(2).strip()
            return_type = match.group(3).strip() if match.group(3) else None

            # Parse parameters with types
            parameters = []
            if params_str:
                for param in params_str.split(","):
                    param = param.strip()
                    if param:
                        parameters.append(param)

            line_num = content[: match.start()].count("\n") + 1

            # Check if async
            is_async = "async" in match.group(0)

            functions.append(
                FunctionInfo(
                    name=name,
                    parameters=parameters,
                    start_line=line_num,
                    return_type=return_type,
                    is_async=is_async,
                    visibility="public",
                )
            )

        # Arrow functions with type annotations
        arrow_pattern = (
            r"(?:const|let|var)\s+(\w+)\s*:\s*\([^)]*\)\s*=>\s*[^=]*=\s*\([^)]*\)\s*=>"
        )
        simple_arrow_pattern = (
            r"(?:const|let|var)\s+(\w+)\s*=\s*\(([^)]*)\)\s*:\s*([^=]+)?\s*=>"
        )

        matches = re.finditer(simple_arrow_pattern, content)
        for match in matches:
            name = match.group(1)
            params_str = match.group(2).strip()
            return_type = match.group(3).strip() if match.group(3) else None

            parameters = []
            if params_str:
                for param in params_str.split(","):
                    param = param.strip()
                    if param:
                        parameters.append(param)

            line_num = content[: match.start()].count("\n") + 1

            functions.append(
                FunctionInfo(
                    name=name,
                    parameters=parameters,
                    start_line=line_num,
                    return_type=return_type,
                    visibility="public",
                )
            )

        return functions

    def _extract_classes(self, content: str) -> List[ClassInfo]:
        """Extract class definitions from TypeScript code."""
        classes = []

        # Class declarations with optional extends and implements
        class_pattern = r"(?:export\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{"
        matches = re.finditer(class_pattern, content)

        for match in matches:
            name = match.group(1)
            base_class = match.group(2)
            interfaces_str = match.group(3)

            base_classes = [base_class] if base_class else []
            interfaces = []
            if interfaces_str:
                interfaces = [i.strip() for i in interfaces_str.split(",")]

            line_num = content[: match.start()].count("\n") + 1

            # Check if abstract
            is_abstract = "abstract" in match.group(0)

            classes.append(
                ClassInfo(
                    name=name,
                    start_line=line_num,
                    base_classes=base_classes,
                    interfaces=interfaces,
                    visibility="public",
                    is_abstract=is_abstract,
                )
            )

        return classes

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from TypeScript code."""
        imports = []

        # ES6 imports
        import_pattern = r'import\s+.*?from\s+[\'"][^\'\"]+[\'"]'
        matches = re.findall(import_pattern, content)
        imports.extend(matches)

        # Type-only imports
        type_import_pattern = r'import\s+type\s+.*?from\s+[\'"][^\'\"]+[\'"]'
        matches = re.findall(type_import_pattern, content)
        imports.extend(matches)

        # CommonJS requires (if any)
        require_pattern = r'(?:const|let|var)\s+.*?=\s*require\([\'"][^\'\"]+[\'\"]\)'
        matches = re.findall(require_pattern, content)
        imports.extend(matches)

        return imports

    def _extract_constants(self, content: str) -> Dict[str, Any]:
        """Extract constant definitions from TypeScript code."""
        constants = {}

        # Const declarations with type annotations
        const_pattern = r"const\s+([A-Z_][A-Z0-9_]*)\s*:\s*[^=]*=\s*([^;]+);?"
        matches = re.findall(const_pattern, content)

        for name, value in matches:
            constants[name] = value.strip()

        # Simple const declarations
        simple_const_pattern = r"const\s+([A-Z_][A-Z0-9_]*)\s*=\s*([^;]+);?"
        matches = re.findall(simple_const_pattern, content)

        for name, value in matches:
            if name not in constants:  # Don't override typed constants
                constants[name] = value.strip()

        return constants

    def _extract_comments(self, content: str) -> List[str]:
        """Extract comments from TypeScript code."""
        comments = []

        # Single-line comments
        single_line_pattern = r"//\s*(.*)"
        matches = re.findall(single_line_pattern, content)
        comments.extend(matches)

        # Multi-line comments
        multi_line_pattern = r"/\*(.*?)\*/"
        matches = re.findall(multi_line_pattern, content, re.DOTALL)
        for match in matches:
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
