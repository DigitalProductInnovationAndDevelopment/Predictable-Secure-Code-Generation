"""
Generic code generator for any programming language.

This module provides a language-agnostic code generator that can generate
code in any supported programming language using registered language providers.
"""

import logging
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from ..language.registry import get_global_registry
from ..initialization import ensure_initialized


class GenerationStatus(Enum):
    """Status of code generation operation."""

    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"


@dataclass
class GenerationResult:
    """Result of a code generation operation."""

    status: GenerationStatus
    target_language: str
    generated_files: List[str]
    test_files: List[str]
    requirements_implemented: int
    requirements_failed: int
    execution_time: float
    errors: List[str]
    warnings: List[str]
    ai_tokens_used: int = 0


class GenericCodeGenerator:
    """
    Generic code generator for any programming language.

    This class can generate code in any supported programming language
    using the appropriate language providers and AI assistance.
    """

    def __init__(self, ai_client=None):
        """
        Initialize the generic code generator.

        Args:
            ai_client: Optional AI client for code generation
        """
        self.logger = logging.getLogger(__name__)

        # Ensure language providers are initialized
        ensure_initialized()

        self.registry = get_global_registry()
        self.ai_client = ai_client

        if not self.ai_client:
            self.logger.warning(
                "No AI client provided - limited functionality available"
            )

        self.logger.info("Generic code generator initialized")

    def generate_from_requirements(
        self,
        requirements: List[Dict[str, Any]],
        target_language: str,
        output_path: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> GenerationResult:
        """
        Generate code from requirements in the specified language.

        Args:
            requirements: List of requirement dictionaries
            target_language: Target programming language
            output_path: Path to output directory
            context: Optional context for code generation

        Returns:
            Generation result
        """
        start_time = time.time()

        self.logger.info(
            f"Starting code generation for {len(requirements)} requirements in {target_language}"
        )

        # Validate inputs
        if not requirements:
            raise ValueError("No requirements provided")

        provider = self.registry.get_provider(target_language)
        if not provider:
            raise ValueError(f"Unsupported target language: {target_language}")

        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        # Initialize result
        result = GenerationResult(
            status=GenerationStatus.IN_PROGRESS,
            target_language=target_language,
            generated_files=[],
            test_files=[],
            requirements_implemented=0,
            requirements_failed=0,
            execution_time=0,
            errors=[],
            warnings=[],
        )

        context = context or {}

        # Generate code for each requirement
        for i, requirement in enumerate(requirements):
            try:
                self.logger.info(
                    f"Processing requirement {i+1}/{len(requirements)}: {requirement.get('description', 'No description')[:50]}..."
                )

                file_result = self._generate_single_requirement(
                    requirement, provider, output_path, context, result
                )

                if file_result:
                    result.requirements_implemented += 1
                else:
                    result.requirements_failed += 1

            except Exception as e:
                error_msg = f"Failed to process requirement {i+1}: {str(e)}"
                self.logger.error(error_msg)
                result.errors.append(error_msg)
                result.requirements_failed += 1

        # Generate tests if requested
        if context.get("generate_tests", True) and result.generated_files:
            self._generate_tests(result, provider, output_path, context)

        # Determine final status
        if result.requirements_failed == 0:
            result.status = GenerationStatus.SUCCESS
        elif result.requirements_implemented > 0:
            result.status = GenerationStatus.PARTIAL_SUCCESS
        else:
            result.status = GenerationStatus.FAILED

        result.execution_time = time.time() - start_time

        self.logger.info(
            f"Code generation completed in {result.execution_time:.2f}s - "
            f"Status: {result.status.value}, "
            f"Implemented: {result.requirements_implemented}/{len(requirements)}"
        )

        return result

    def generate_file_template(
        self,
        language: str,
        template_type: str = "basic",
        output_path: str = None,
        filename: str = None,
    ) -> str:
        """
        Generate a file template for the specified language.

        Args:
            language: Target programming language
            template_type: Type of template (basic, class, module, etc.)
            output_path: Optional output path to save the template
            filename: Optional filename for the template

        Returns:
            Generated template content
        """
        provider = self.registry.get_provider(language)
        if not provider:
            raise ValueError(f"Unsupported language: {language}")

        template_content = provider.get_file_template(template_type)

        if output_path and filename:
            output_path = Path(output_path)
            output_path.mkdir(parents=True, exist_ok=True)

            template_file = output_path / filename
            with open(template_file, "w", encoding="utf-8") as f:
                f.write(template_content)

            self.logger.info(f"Template saved to: {template_file}")

        return template_content

    def _generate_single_requirement(
        self,
        requirement: Dict[str, Any],
        provider,
        output_path: Path,
        context: Dict[str, Any],
        result: GenerationResult,
    ) -> bool:
        """
        Generate code for a single requirement.

        Args:
            requirement: Requirement dictionary
            provider: Language provider
            output_path: Output directory path
            context: Generation context
            result: Generation result to update

        Returns:
            True if successful, False otherwise
        """
        try:
            requirement_id = requirement.get("id", "unknown")
            description = requirement.get("description", "")

            if not self.ai_client:
                result.warnings.append(
                    f"No AI client available for requirement {requirement_id}"
                )
                return False

            # Generate AI prompt
            ai_context = {
                "context": context.get("project_context", ""),
                "requirement_id": requirement_id,
                "existing_files": result.generated_files,
            }

            prompt = provider.generate_code_prompt(description, ai_context)

            # Call AI to generate code
            ai_response = self.ai_client.ask_question(
                question=prompt,
                max_tokens=context.get("max_tokens", 2000),
                temperature=context.get("temperature", 0.7),
            )

            if ai_response.get("status") != "success":
                error_msg = f"AI generation failed for requirement {requirement_id}: {ai_response.get('error', 'Unknown error')}"
                result.errors.append(error_msg)
                return False

            result.ai_tokens_used += ai_response.get("usage", {}).get("total_tokens", 0)

            # Extract clean code
            generated_code = provider.extract_generated_code(ai_response["answer"])

            if not generated_code.strip():
                result.warnings.append(
                    f"No code generated for requirement {requirement_id}"
                )
                return False

            # Determine filename
            filename = self._generate_filename(requirement, provider, context)
            file_path = output_path / filename

            # Add standard imports if needed
            if context.get("add_standard_imports", True):
                imports = provider.get_standard_imports()
                if imports and not any(
                    imp.strip() in generated_code for imp in imports[:3]
                ):
                    # Add a few standard imports if they don't already exist
                    generated_code = "\n".join(imports[:3]) + "\n\n" + generated_code

            # Save generated code
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(generated_code)

            result.generated_files.append(str(file_path))

            self.logger.info(
                f"Generated code for requirement {requirement_id} -> {filename}"
            )

            return True

        except Exception as e:
            error_msg = f"Error generating code for requirement {requirement.get('id', 'unknown')}: {str(e)}"
            result.errors.append(error_msg)
            return False

    def _generate_tests(
        self,
        result: GenerationResult,
        provider,
        output_path: Path,
        context: Dict[str, Any],
    ) -> None:
        """
        Generate test files for the generated code.

        Args:
            result: Generation result to update
            provider: Language provider
            output_path: Output directory path
            context: Generation context
        """
        try:
            self.logger.info("Generating test files...")

            tests_dir = output_path / "tests"
            tests_dir.mkdir(exist_ok=True)

            for generated_file in result.generated_files:
                try:
                    # Create a simple test file
                    file_path = Path(generated_file)
                    module_name = file_path.stem

                    # Create a mock function info for test generation
                    from .core.language_provider import FunctionInfo

                    function_info = FunctionInfo(
                        name="main_function", parameters=[]  # Generic function name
                    )

                    test_context = {
                        "module_name": module_name,
                        "class_name": context.get("class_name", "TestClass"),
                        "namespace": context.get("namespace", "Tests"),
                    }

                    test_code = provider.generate_test_code(function_info, test_context)

                    # Determine test filename
                    test_filename = f"test_{module_name}.{provider.file_extensions.__iter__().__next__()[1:]}"
                    test_file_path = tests_dir / test_filename

                    with open(test_file_path, "w", encoding="utf-8") as f:
                        f.write(test_code)

                    result.test_files.append(str(test_file_path))

                except Exception as e:
                    result.warnings.append(
                        f"Failed to generate test for {generated_file}: {str(e)}"
                    )

            self.logger.info(f"Generated {len(result.test_files)} test files")

        except Exception as e:
            result.warnings.append(f"Test generation failed: {str(e)}")

    def _generate_filename(
        self, requirement: Dict[str, Any], provider, context: Dict[str, Any]
    ) -> str:
        """
        Generate an appropriate filename for a requirement.

        Args:
            requirement: Requirement dictionary
            provider: Language provider
            context: Generation context

        Returns:
            Generated filename
        """
        requirement_id = requirement.get("id", "unknown")
        description = requirement.get("description", "")

        # Clean the requirement ID or description for filename
        if requirement_id and requirement_id != "unknown":
            base_name = requirement_id.lower().replace(" ", "_").replace("-", "_")
        else:
            # Use first few words of description
            words = description.lower().split()[:3]
            base_name = "_".join(words).replace(" ", "_")

        # Remove non-alphanumeric characters except underscores
        import re

        base_name = re.sub(r"[^a-zA-Z0-9_]", "", base_name)

        # Ensure it starts with a letter
        if base_name and base_name[0].isdigit():
            base_name = "req_" + base_name

        if not base_name:
            base_name = "generated_code"

        # Add appropriate extension
        extensions = list(provider.file_extensions)
        extension = extensions[0] if extensions else ".txt"

        return f"{base_name}{extension}"

    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported programming languages.

        Returns:
            List of supported language names
        """
        return self.registry.get_supported_languages()

    def get_generation_report(self, result: GenerationResult) -> str:
        """
        Generate a human-readable generation report.

        Args:
            result: Generation result to generate report for

        Returns:
            Formatted generation report
        """
        lines = []
        lines.append("=" * 60)
        lines.append("CODE GENERATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Status: {result.status.value.upper()}")
        lines.append(f"Target Language: {result.target_language}")
        lines.append(f"Requirements Implemented: {result.requirements_implemented}")
        lines.append(f"Requirements Failed: {result.requirements_failed}")
        lines.append(f"Generated Files: {len(result.generated_files)}")
        lines.append(f"Test Files: {len(result.test_files)}")
        lines.append(f"Execution Time: {result.execution_time:.2f}s")
        if result.ai_tokens_used > 0:
            lines.append(f"AI Tokens Used: {result.ai_tokens_used}")
        lines.append("")

        if result.generated_files:
            lines.append("GENERATED FILES:")
            lines.append("-" * 30)
            for file_path in result.generated_files:
                lines.append(f"  {file_path}")
            lines.append("")

        if result.test_files:
            lines.append("TEST FILES:")
            lines.append("-" * 30)
            for file_path in result.test_files:
                lines.append(f"  {file_path}")
            lines.append("")

        if result.errors:
            lines.append("ERRORS:")
            lines.append("-" * 30)
            for error in result.errors:
                lines.append(f"  {error}")
            lines.append("")

        if result.warnings:
            lines.append("WARNINGS:")
            lines.append("-" * 30)
            for warning in result.warnings:
                lines.append(f"  {warning}")
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)
