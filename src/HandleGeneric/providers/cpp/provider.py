# C++ language provider implementation.

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


class CppProvider(LanguageProvider):
    """Language provider for C++."""

    @property
    def language_name(self) -> str:
        return "cpp"

    @property
    def file_extensions(self) -> Set[str]:
        return {".cpp", ".h", ".hpp", ".cc", ".cxx"}

    @property
    def comment_prefixes(self) -> List[str]:
        return ["//", "/*"]

    def parse_file(self, file_path: Path, content: str) -> FileMetadata:
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
                        if line.strip() and not line.strip().startswith("//")
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
        try:
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".cpp", delete=False
            ) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            try:
                result = subprocess.run(
                    ["g++", temp_file_path, "-fsyntax-only"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )

                if result.returncode == 0:
                    return SyntaxValidationResult.VALID, None
                else:
                    return SyntaxValidationResult.INVALID, result.stderr.strip()
            finally:
                Path(temp_file_path).unlink(missing_ok=True)

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return self._basic_syntax_check(content)

    def _basic_syntax_check(
        self, content: str
    ) -> tuple[SyntaxValidationResult, Optional[str]]:
        brace_count = content.count("{") - content.count("}")
        if brace_count != 0:
            return SyntaxValidationResult.INVALID, "Unbalanced braces"

        paren_count = content.count("(") - content.count(")")
        if paren_count != 0:
            return SyntaxValidationResult.INVALID, "Unbalanced parentheses"

        bracket_count = content.count("[") - content.count("]")
        if bracket_count != 0:
            return SyntaxValidationResult.INVALID, "Unbalanced brackets"

        return SyntaxValidationResult.VALID, None

    def generate_code_prompt(self, requirement: str, context: Dict[str, Any]) -> str:
        return f"""You are an expert C++ developer. Generate clean, well-documented C++ code based on requirements.

Requirement: {requirement}

Context: {context.get('context', '')}

Guidelines:
- Use modern C++ features
- Follow C++ naming conventions (CamelCase for classes, snake_case for functions)
- Include proper comments
- Use appropriate access modifiers
- Write clean, readable code
- Follow C++ best practices and coding standards
- Include necessary #include statements
- Provide only the C++ code without markdown formatting

Generate the C++ code:"""

    def extract_generated_code(self, ai_response: str) -> str:
        code_pattern = r"```(?:cpp|c\+\+)?\s*(.*?)```"
        matches = re.findall(code_pattern, ai_response, re.DOTALL | re.IGNORECASE)

        if matches:
            return matches[0].strip()

        lines = ai_response.split("\n")
        code_lines = []
        in_code = False

        for line in lines:
            if any(
                line.strip().startswith(keyword)
                for keyword in ["#include", "int main", "class ", "namespace "]
            ):
                in_code = True

            if in_code and line.strip():
                code_lines.append(line)
            elif in_code and not line.strip():
                code_lines.append(line)

        return "\n".join(code_lines).strip()

    def get_test_framework_commands(self) -> List[str]:
        return ["make", "ctest"]

    def generate_test_code(
        self, function_info: FunctionInfo, context: Dict[str, Any]
    ) -> str:
        method_name = function_info.name
        class_name = context.get("class_name", "TestClass")

        return f"""#include <gtest/gtest.h>

TEST({class_name}Tests, {method_name}_ShouldWorkCorrectly) {{
    // TODO: Add test cases
    // auto result = {method_name}(...);
    // EXPECT_EQ(expectedValue, result);
}}

TEST({class_name}Tests, {method_name}_ShouldHandleEdgeCases) {{
    // TODO: Add edge case tests
}}

TEST({class_name}Tests, {method_name}_ShouldHandleErrors) {{
    // TODO: Add error handling tests
}}
"""

    def get_standard_imports(self) -> List[str]:
        return [
            "#include <iostream>",
            "#include <vector>",
            "#include <string>",
            "#include <algorithm>",
        ]

    def get_file_template(self, template_type: str = "basic") -> str:
        templates = {
            "basic": """#include <iostream>

int main() {
    std::cout << \"Hello, World!\" << std::endl;
    return 0;
}
""",
            "class": """#include <string>

class ClassName {
private:
    std::string field;

public:
    ClassName(const std::string& field) : field(field) {}

    std::string get_field() const { return field; }
    void set_field(const std::string& f) { field = f; }
};
""",
            "interface": "// C++ does not have native interfaces like C#. Use abstract classes instead.",
        }
        return templates.get(template_type, templates["basic"])

    def _extract_methods(self, content: str) -> List[FunctionInfo]:
        methods = []
        method_pattern = r"(\w[\w:\s<>*&]*?)\s+(\w+)\s*\(([^)]*)\)\s*\{"
        matches = re.finditer(method_pattern, content)

        for match in matches:
            return_type = match.group(1).strip()
            name = match.group(2)
            params_str = match.group(3).strip()

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
                    visibility="public",
                    is_static=False,
                    is_async=False,
                )
            )

        return methods

    def _extract_classes(self, content: str) -> List[ClassInfo]:
        classes = []
        class_pattern = r"class\s+(\w+)\s*(?::\s*public\s+([^{]+))?\s*\{"
        matches = re.finditer(class_pattern, content)

        for match in matches:
            name = match.group(1)
            inheritance_str = match.group(2)

            base_classes = []
            interfaces = []

            if inheritance_str:
                base_classes = [b.strip() for b in inheritance_str.split(",")]

            line_num = content[: match.start()].count("\n") + 1

            classes.append(
                ClassInfo(
                    name=name,
                    start_line=line_num,
                    base_classes=base_classes,
                    interfaces=interfaces,
                    visibility="public",
                    is_abstract=False,
                    is_final=False,
                )
            )

        return classes

    def _extract_imports(self, content: str) -> List[str]:
        return re.findall(r"#include\s+[<\"]\w+.*?[>\"]", content)

    def _extract_constants(self, content: str) -> Dict[str, Any]:
        constants = {}
        const_pattern = r"const\s+\w+\s+(\w+)\s*=\s*([^;]+);"
        matches = re.findall(const_pattern, content)

        for name, value in matches:
            constants[name] = value.strip()

        return constants

    def _extract_comments(self, content: str) -> List[str]:
        comments = []

        single_line_pattern = r"//\s*(.*)"
        matches = re.findall(single_line_pattern, content)
        comments.extend(matches)

        multi_line_pattern = r"/\*(?!\*)(.*?)\*/"
        matches = re.findall(multi_line_pattern, content, re.DOTALL)
        for match in matches:
            lines = match.strip().split("\n")
            comments.extend([line.strip() for line in lines if line.strip()])

        return comments

    def _extract_file_header_comment(self, content: str) -> Optional[str]:
        header_patterns = [
            r"^\s*//\s*.*?\n(?:\s*//.*?\n)*",
            r"^\s*/\*\*(.*?)\*/",
        ]

        for pattern in header_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                if "/*" in match.group(0):
                    lines = match.group(1).strip().split("\n")
                    cleaned_lines = [
                        line.strip().lstrip("*").strip()
                        for line in lines
                        if line.strip()
                    ]
                    return "\n".join(cleaned_lines).strip()
                else:
                    lines = match.group(0).strip().split("\n")
                    cleaned_lines = [
                        line.strip().lstrip("//").strip()
                        for line in lines
                        if line.strip()
                    ]
                    return "\n".join(cleaned_lines).strip()

        return None
