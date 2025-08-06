"""
C# language provider implementation.

This module provides C#-specific implementations for code parsing,
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


class CSharpProvider(LanguageProvider):
    """Language provider for C#."""

    @property
    def language_name(self) -> str:
        return "csharp"

    @property
    def file_extensions(self) -> Set[str]:
        return {".cs"}

    @property
    def comment_prefixes(self) -> List[str]:
        return ["//", "/*", "///"]

    def parse_file(self, file_path: Path, content: str) -> FileMetadata:
        """Parse a C# file and extract metadata."""
        try:
            functions = self._extract_methods(content)
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
        """Validate C# syntax using csc if available."""
        try:
            # Create a temporary file to compile
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".cs", delete=False
            ) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            try:
                # Try using dotnet compiler
                result = subprocess.run(
                    [
                        "dotnet",
                        "build",
                        temp_file_path,
                        "--nologo",
                        "--verbosity",
                        "quiet",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )

                if result.returncode == 0:
                    return SyntaxValidationResult.VALID, None
                else:
                    return SyntaxValidationResult.INVALID, result.stderr.strip()
            finally:
                # Clean up
                Path(temp_file_path).unlink(missing_ok=True)

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
        """Generate a C#-specific prompt for AI code generation."""
        return f"""You are an expert C# developer. Generate clean, well-documented C# code based on requirements.

Requirement: {requirement}

Context: {context.get('context', '')}

Guidelines:
- Follow C# naming conventions (PascalCase for classes and methods, camelCase for fields)
- Include proper XML documentation comments
- Use appropriate access modifiers
- Handle exceptions appropriately with try-catch blocks
- Write clean, readable code
- Follow C# best practices and coding standards
- Include necessary using statements
- Use modern C# features when appropriate
- Provide only the C# code without markdown formatting

Generate the C# code:"""

    def extract_generated_code(self, ai_response: str) -> str:
        """Extract clean C# code from AI response."""
        # Remove markdown code blocks
        code_pattern = r"```(?:csharp|cs|c#)?\s*(.*?)```"
        matches = re.findall(code_pattern, ai_response, re.DOTALL | re.IGNORECASE)

        if matches:
            return matches[0].strip()

        # If no code blocks found, try to extract C#-looking code
        lines = ai_response.split("\n")
        code_lines = []
        in_code = False

        for line in lines:
            # Start capturing when we see C# keywords
            if any(
                line.strip().startswith(keyword)
                for keyword in [
                    "using ",
                    "namespace ",
                    "public ",
                    "private ",
                    "protected ",
                    "class ",
                    "interface ",
                    "enum ",
                    "struct ",
                    "[",
                    "//",
                ]
            ):
                in_code = True

            if in_code and line.strip():
                code_lines.append(line)
            elif in_code and not line.strip():
                code_lines.append(line)  # Keep empty lines in code

        return "\n".join(code_lines).strip()

    def get_test_framework_commands(self) -> List[str]:
        """Get commands to run C# tests."""
        return ["dotnet", "test"]

    def generate_test_code(
        self, function_info: FunctionInfo, context: Dict[str, Any]
    ) -> str:
        """Generate test code for a C# method."""
        method_name = function_info.name
        class_name = context.get("class_name", "TestClass")

        return f"""using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace {context.get("namespace", "Tests")}
{{
    [TestClass]
    public class {class_name}Tests
    {{
        private {class_name} _instance;

        [TestInitialize]
        public void Setup()
        {{
            _instance = new {class_name}();
        }}

        [TestMethod]
        public void {method_name}_ShouldWorkCorrectly()
        {{
            // TODO: Add test cases
            // var result = _instance.{method_name}();
            // Assert.AreEqual(expectedValue, result);
        }}

        [TestMethod]
        public void {method_name}_ShouldHandleEdgeCases()
        {{
            // TODO: Add edge case tests
        }}

        [TestMethod]
        [ExpectedException(typeof(ArgumentException))]
        public void {method_name}_ShouldHandleErrors()
        {{
            // TODO: Add error handling tests
        }}
    }}
}}
"""

    def get_standard_imports(self) -> List[str]:
        """Get standard C# using statements."""
        return [
            "using System;",
            "using System.Collections.Generic;",
            "using System.IO;",
            "using System.Linq;",
            "using System.Text;",
            "using System.Threading.Tasks;",
        ]

    def get_file_template(self, template_type: str = "basic") -> str:
        """Get C# file template."""
        templates = {
            "basic": """using System;

namespace ProjectName
{
    /// <summary>
    /// Class description
    /// </summary>
    public class ClassName
    {
        /// <summary>
        /// Main method
        /// </summary>
        /// <param name="args">Command line arguments</param>
        public static void Main(string[] args)
        {
            // Implementation here
        }
    }
}
""",
            "class": """using System;
using System.Collections.Generic;

namespace ProjectName
{
    /// <summary>
    /// Class description
    /// </summary>
    public class ClassName
    {
        private string _field;

        /// <summary>
        /// Initializes a new instance of the <see cref="ClassName"/> class.
        /// </summary>
        /// <param name="field">Initial value</param>
        public ClassName(string field)
        {
            _field = field;
        }

        /// <summary>
        /// Gets or sets the field value
        /// </summary>
        public string Field
        {
            get => _field;
            set => _field = value;
        }

        /// <summary>
        /// Method description
        /// </summary>
        /// <returns>Return value description</returns>
        public string MethodName()
        {
            // Implementation
            return _field;
        }
    }
}
""",
            "interface": """using System;

namespace ProjectName
{
    /// <summary>
    /// Interface description
    /// </summary>
    public interface IInterfaceName
    {
        /// <summary>
        /// Method description
        /// </summary>
        /// <param name="param">Parameter description</param>
        /// <returns>Return value description</returns>
        ReturnType MethodName(ParamType param);
    }
}
""",
        }
        return templates.get(template_type, templates["basic"])

    def _extract_methods(self, content: str) -> List[FunctionInfo]:
        """Extract method definitions from C# code."""
        methods = []

        # Method pattern with access modifiers, return type, etc.
        method_pattern = r"(public|private|protected|internal)?\s*(static)?\s*(virtual|override|abstract)?\s*(async)?\s*(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{"
        matches = re.finditer(method_pattern, content)

        for match in matches:
            visibility = match.group(1) or "private"
            is_static = bool(match.group(2))
            modifiers = match.group(3)
            is_async = bool(match.group(4))
            return_type = match.group(5)
            name = match.group(6)
            params_str = match.group(7).strip()

            # Parse parameters
            parameters = []
            if params_str:
                for param in params_str.split(","):
                    param = param.strip()
                    if param:
                        parameters.append(param)

            line_num = content[: match.start()].count("\n") + 1

            methods.append(
                FunctionInfo(
                    name=name,
                    parameters=parameters,
                    start_line=line_num,
                    return_type=return_type,
                    visibility=visibility,
                    is_static=is_static,
                    is_async=is_async,
                )
            )

        return methods

    def _extract_classes(self, content: str) -> List[ClassInfo]:
        """Extract class definitions from C# code."""
        classes = []

        # Class pattern with modifiers
        class_pattern = r"(public|private|protected|internal)?\s*(abstract|sealed|static)?\s*class\s+(\w+)(?:\s*:\s*([^{]+))?\s*\{"
        matches = re.finditer(class_pattern, content)

        for match in matches:
            visibility = match.group(1) or "internal"
            modifiers = match.group(2)
            name = match.group(3)
            inheritance_str = match.group(4)

            base_classes = []
            interfaces = []

            if inheritance_str:
                inheritance_parts = [
                    part.strip() for part in inheritance_str.split(",")
                ]
                # In C#, first inheritance is usually base class, rest are interfaces
                if inheritance_parts:
                    # Simplified assumption: if it starts with 'I' and has uppercase next letter, it's an interface
                    for part in inheritance_parts:
                        if part.startswith("I") and len(part) > 1 and part[1].isupper():
                            interfaces.append(part)
                        else:
                            base_classes.append(part)

            line_num = content[: match.start()].count("\n") + 1

            is_abstract = modifiers == "abstract"
            is_final = modifiers == "sealed"

            classes.append(
                ClassInfo(
                    name=name,
                    start_line=line_num,
                    base_classes=base_classes,
                    interfaces=interfaces,
                    visibility=visibility,
                    is_abstract=is_abstract,
                    is_final=is_final,
                )
            )

        return classes

    def _extract_imports(self, content: str) -> List[str]:
        """Extract using statements from C# code."""
        imports = []

        using_pattern = r"using\s+[^;]+;"
        matches = re.findall(using_pattern, content)
        imports.extend(matches)

        return imports

    def _extract_constants(self, content: str) -> Dict[str, Any]:
        """Extract constant definitions from C# code."""
        constants = {}

        # Const fields
        const_pattern = r"(?:public|private|protected|internal)?\s*const\s+\w+\s+([A-Z_][A-Z0-9_]*)\s*=\s*([^;]+);"
        matches = re.findall(const_pattern, content)

        for name, value in matches:
            constants[name] = value.strip()

        # Static readonly fields
        readonly_pattern = r"(?:public|private|protected|internal)?\s*static\s+readonly\s+\w+\s+([A-Z_][A-Z0-9_]*)\s*=\s*([^;]+);"
        matches = re.findall(readonly_pattern, content)

        for name, value in matches:
            constants[name] = value.strip()

        return constants

    def _extract_comments(self, content: str) -> List[str]:
        """Extract comments from C# code."""
        comments = []

        # Single-line comments
        single_line_pattern = r"//\s*(.*)"
        matches = re.findall(single_line_pattern, content)
        comments.extend(matches)

        # Multi-line comments (excluding XML docs)
        multi_line_pattern = r"/\*(?![\*!])(.*?)\*/"
        matches = re.findall(multi_line_pattern, content, re.DOTALL)
        for match in matches:
            lines = match.strip().split("\n")
            comments.extend([line.strip() for line in lines if line.strip()])

        return comments

    def _extract_file_header_comment(self, content: str) -> Optional[str]:
        """Extract file header comment."""
        # Look for file header comment at the beginning
        header_patterns = [
            r"^\s*//\s*.*?\n(?:\s*//.*?\n)*",  # Single-line comment block
            r"^\s*/\*\*(.*?)\*/",  # Multi-line comment block
        ]

        for pattern in header_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                if "/*" in match.group(0):
                    # Multi-line comment
                    lines = match.group(1).strip().split("\n")
                    cleaned_lines = [
                        line.strip().lstrip("*").strip()
                        for line in lines
                        if line.strip()
                    ]
                    return "\n".join(cleaned_lines).strip()
                else:
                    # Single-line comment block
                    lines = match.group(0).strip().split("\n")
                    cleaned_lines = [
                        line.strip().lstrip("//").strip()
                        for line in lines
                        if line.strip()
                    ]
                    return "\n".join(cleaned_lines).strip()

        return None
