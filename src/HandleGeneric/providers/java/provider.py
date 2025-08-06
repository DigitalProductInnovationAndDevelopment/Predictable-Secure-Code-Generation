"""
Java language provider implementation.

This module provides Java-specific implementations for code parsing,
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


class JavaProvider(LanguageProvider):
    """Language provider for Java."""

    @property
    def language_name(self) -> str:
        return "java"

    @property
    def file_extensions(self) -> Set[str]:
        return {".java"}

    @property
    def comment_prefixes(self) -> List[str]:
        return ["//", "/*"]

    def parse_file(self, file_path: Path, content: str) -> FileMetadata:
        """Parse a Java file and extract metadata."""
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
                docstring=self._extract_class_javadoc(content),
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
        """Validate Java syntax using javac if available."""
        try:
            # Create a temporary file to compile
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".java", delete=False
            ) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            try:
                result = subprocess.run(
                    ["javac", "-cp", ".", temp_file_path],
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
                Path(temp_file_path.replace(".java", ".class")).unlink(missing_ok=True)

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

        # Check for basic Java structure
        if not re.search(r"class\s+\w+", content):
            return SyntaxValidationResult.INVALID, "No class definition found"

        return SyntaxValidationResult.VALID, None

    def generate_code_prompt(self, requirement: str, context: Dict[str, Any]) -> str:
        """Generate a Java-specific prompt for AI code generation."""
        return f"""You are an expert Java developer. Generate clean, well-documented Java code based on requirements.

Requirement: {requirement}

Context: {context.get('context', '')}

Guidelines:
- Follow Java naming conventions (PascalCase for classes, camelCase for methods)
- Include proper Javadoc comments
- Use appropriate access modifiers
- Handle exceptions appropriately
- Write clean, readable code
- Follow Java best practices
- Include necessary imports
- Provide only the Java code without markdown formatting

Generate the Java code:"""

    def extract_generated_code(self, ai_response: str) -> str:
        """Extract clean Java code from AI response."""
        # Remove markdown code blocks
        code_pattern = r"```(?:java)?\s*(.*?)```"
        matches = re.findall(code_pattern, ai_response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # If no code blocks found, try to extract Java-looking code
        lines = ai_response.split("\n")
        code_lines = []
        in_code = False

        for line in lines:
            # Start capturing when we see Java keywords
            if any(
                line.strip().startswith(keyword)
                for keyword in [
                    "package ",
                    "import ",
                    "public ",
                    "private ",
                    "protected ",
                    "class ",
                    "interface ",
                    "enum ",
                    "@",
                ]
            ):
                in_code = True

            if in_code and line.strip():
                code_lines.append(line)
            elif in_code and not line.strip():
                code_lines.append(line)  # Keep empty lines in code

        return "\n".join(code_lines).strip()

    def get_test_framework_commands(self) -> List[str]:
        """Get commands to run Java tests."""
        return ["mvn", "test"]

    def generate_test_code(
        self, function_info: FunctionInfo, context: Dict[str, Any]
    ) -> str:
        """Generate test code for a Java method."""
        method_name = function_info.name
        class_name = context.get("class_name", "TestClass")

        return f"""import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

class {class_name}Test {{
    
    private {class_name} instance;
    
    @BeforeEach
    void setUp() {{
        instance = new {class_name}();
    }}
    
    @Test
    void test{method_name.capitalize()}() {{
        // TODO: Add test cases
        // Object result = instance.{method_name}();
        // assertEquals(expectedValue, result);
    }}
    
    @Test
    void test{method_name.capitalize()}EdgeCases() {{
        // TODO: Add edge case tests
    }}
    
    @Test
    void test{method_name.capitalize()}ErrorHandling() {{
        // TODO: Add error handling tests
    }}
}}
"""

    def get_standard_imports(self) -> List[str]:
        """Get standard Java imports."""
        return [
            "import java.util.*;",
            "import java.io.*;",
            "import java.nio.file.*;",
        ]

    def get_file_template(self, template_type: str = "basic") -> str:
        """Get Java file template."""
        templates = {
            "basic": """/**
 * @author Your Name
 * @version 1.0
 */
public class ClassName {
    
    /**
     * Main method
     * @param args command line arguments
     */
    public static void main(String[] args) {
        // Implementation here
    }
}
""",
            "class": """/**
 * Class description
 * 
 * @author Your Name
 * @version 1.0
 */
public class ClassName {
    
    private String field;
    
    /**
     * Constructor
     * @param field initial value
     */
    public ClassName(String field) {
        this.field = field;
    }
    
    /**
     * Getter method
     * @return field value
     */
    public String getField() {
        return field;
    }
    
    /**
     * Setter method
     * @param field new value
     */
    public void setField(String field) {
        this.field = field;
    }
}
""",
            "interface": """/**
 * Interface description
 * 
 * @author Your Name
 * @version 1.0
 */
public interface InterfaceName {
    
    /**
     * Method description
     * @param param parameter description
     * @return return value description
     */
    ReturnType methodName(ParamType param);
}
""",
        }
        return templates.get(template_type, templates["basic"])

    def _extract_methods(self, content: str) -> List[FunctionInfo]:
        """Extract method definitions from Java code."""
        methods = []

        # Method pattern with access modifiers, return type, etc.
        method_pattern = r"(public|private|protected)?\s*(static)?\s*(final)?\s*(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+[^{]+)?\s*\{"
        matches = re.finditer(method_pattern, content)

        for match in matches:
            visibility = match.group(1) or "package"
            is_static = bool(match.group(2))
            return_type = match.group(4)
            name = match.group(5)
            params_str = match.group(6).strip()

            # Skip constructor (return type same as method name assumption)
            if return_type == name:
                continue

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
                )
            )

        return methods

    def _extract_classes(self, content: str) -> List[ClassInfo]:
        """Extract class definitions from Java code."""
        classes = []

        # Class pattern with modifiers
        class_pattern = r"(public|private|protected)?\s*(abstract|final)?\s*class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{"
        matches = re.finditer(class_pattern, content)

        for match in matches:
            visibility = match.group(1) or "package"
            modifiers = match.group(2)
            name = match.group(3)
            base_class = match.group(4)
            interfaces_str = match.group(5)

            base_classes = [base_class] if base_class else []
            interfaces = []
            if interfaces_str:
                interfaces = [i.strip() for i in interfaces_str.split(",")]

            line_num = content[: match.start()].count("\n") + 1

            is_abstract = modifiers == "abstract"
            is_final = modifiers == "final"

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
        """Extract import statements from Java code."""
        imports = []

        import_pattern = r"import\s+(?:static\s+)?[^;]+;"
        matches = re.findall(import_pattern, content)
        imports.extend(matches)

        return imports

    def _extract_constants(self, content: str) -> Dict[str, Any]:
        """Extract constant definitions from Java code."""
        constants = {}

        # Final static fields (constants)
        const_pattern = r"(?:public|private|protected)?\s*static\s+final\s+\w+\s+([A-Z_][A-Z0-9_]*)\s*=\s*([^;]+);"
        matches = re.findall(const_pattern, content)

        for name, value in matches:
            constants[name] = value.strip()

        return constants

    def _extract_comments(self, content: str) -> List[str]:
        """Extract comments from Java code."""
        comments = []

        # Single-line comments
        single_line_pattern = r"//\s*(.*)"
        matches = re.findall(single_line_pattern, content)
        comments.extend(matches)

        # Multi-line comments (excluding Javadoc)
        multi_line_pattern = r"/\*(?!\*)(.*?)\*/"
        matches = re.findall(multi_line_pattern, content, re.DOTALL)
        for match in matches:
            lines = match.strip().split("\n")
            comments.extend([line.strip() for line in lines if line.strip()])

        return comments

    def _extract_class_javadoc(self, content: str) -> Optional[str]:
        """Extract class-level Javadoc."""
        # Look for Javadoc before class declaration
        javadoc_pattern = r"/\*\*(.*?)\*/\s*(?:public|private|protected)?\s*(?:abstract|final)?\s*class"
        match = re.search(javadoc_pattern, content, re.DOTALL)

        if match:
            lines = match.group(1).strip().split("\n")
            cleaned_lines = [
                line.strip().lstrip("*").strip() for line in lines if line.strip()
            ]
            return "\n".join(cleaned_lines).strip()

        return None
