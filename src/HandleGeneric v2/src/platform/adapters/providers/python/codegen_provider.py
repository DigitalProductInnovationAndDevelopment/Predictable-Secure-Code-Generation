"""Python code generation provider with prompt templates."""

import subprocess
from typing import List, Dict, Any
from pathlib import Path
from platform.ports.providers import CodeGenProvider, ProjectContext
from platform.domain.models.requirements import Requirement
from platform.domain.models.generation import GeneratedFile
from platform.kernel.logging import get_logger

logger = get_logger(__name__)


class PythonCodeGenProvider:
    """Python code generation provider."""

    language = "python"

    def build_prompt(self, requirement: Requirement, context: ProjectContext) -> str:
        """Build a prompt for Python code generation."""
        template_vars = self.get_template_vars(context)

        prompt = f"""You are an expert Python developer. Generate clean, well-documented Python code based on the following requirement.

## Requirement
**ID**: {requirement.id}
**Title**: {requirement.title}
**Description**: {requirement.description}

**Acceptance Criteria**:
{chr(10).join(f"- {criteria}" for criteria in requirement.acceptance)}

## Context
{self._format_context(template_vars)}

## Instructions
1. Generate production-ready Python code following PEP 8 style guidelines
2. Include comprehensive docstrings for all functions and classes
3. Add type hints where appropriate
4. Include error handling and input validation
5. Write the code as if it will be reviewed by senior developers
6. Generate only the code files needed - no explanations or markdown
7. Each file should start with a comment indicating its purpose

## File Structure
Generate files in this format:
```python
# File: path/to/file.py
# Purpose: Brief description of what this file does

[file content here]
```

Generate the code now:"""

        return prompt

    def postprocess(self, files: List[GeneratedFile]) -> List[GeneratedFile]:
        """Post-process generated Python files with formatting and linting."""
        processed_files = []

        for file in files:
            try:
                # Apply Black formatting if available
                formatted_content = self._format_with_black(file.content)

                # Apply isort for import sorting if available
                sorted_content = self._sort_imports(formatted_content)

                processed_file = GeneratedFile(
                    path=file.path, content=sorted_content, language=self.language
                )
                processed_files.append(processed_file)

                logger.debug(
                    "Post-processed Python file",
                    path=file.path,
                    original_size=len(file.content),
                    processed_size=len(sorted_content),
                )

            except Exception as e:
                logger.warning(
                    "Post-processing failed, using original content", path=file.path, error=str(e)
                )
                processed_files.append(file)

        return processed_files

    def get_file_extension(self) -> str:
        """Get the primary file extension for Python."""
        return ".py"

    def get_template_vars(self, context: ProjectContext) -> Dict[str, Any]:
        """Get template variables for prompt generation."""
        return {
            "language": self.language,
            "style_guide": "PEP 8",
            "type_hints": context.get("use_type_hints", True),
            "async_support": context.get("async_support", False),
            "test_framework": context.get("test_framework", "pytest"),
            "project_structure": context.get("project_structure", "package"),
        }

    def _format_context(self, template_vars: Dict[str, Any]) -> str:
        """Format the context for the prompt."""
        context_lines = []
        context_lines.append(f"- Language: {template_vars['language']}")
        context_lines.append(f"- Style Guide: {template_vars['style_guide']}")
        context_lines.append(
            f"- Type Hints: {'Enabled' if template_vars['type_hints'] else 'Disabled'}"
        )
        context_lines.append(
            f"- Async Support: {'Enabled' if template_vars['async_support'] else 'Disabled'}"
        )
        context_lines.append(f"- Test Framework: {template_vars['test_framework']}")
        context_lines.append(f"- Project Structure: {template_vars['project_structure']}")

        return "\n".join(context_lines)

    def _format_with_black(self, content: str) -> str:
        """Format Python code with Black formatter."""
        try:
            result = subprocess.run(
                ["black", "--code", content, "--line-length", "88"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return result.stdout
            else:
                logger.warning("Black formatting failed", stderr=result.stderr)
                return content

        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.debug("Black not available, skipping formatting")
            return content
        except Exception as e:
            logger.warning("Black formatting error", error=str(e))
            return content

    def _sort_imports(self, content: str) -> str:
        """Sort imports with isort."""
        try:
            result = subprocess.run(
                ["isort", "--stdout", "--profile", "black", "-"],
                input=content,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return result.stdout
            else:
                logger.warning("isort failed", stderr=result.stderr)
                return content

        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.debug("isort not available, skipping import sorting")
            return content
        except Exception as e:
            logger.warning("isort error", error=str(e))
            return content
