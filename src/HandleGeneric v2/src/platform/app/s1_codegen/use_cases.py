"""S1 - Code Generation Use Cases."""

import time
from typing import List, Optional
from pathlib import Path
from platform.domain.models.requirements import Requirement
from platform.domain.models.generation import GeneratedFile, CodeGenReport
from platform.ports.ai import LLMClient, LLMMessage
from platform.ports.fs import ArtifactWriter
from platform.ports.providers import CodeGenProvider, SyntaxValidator, ProjectContext
from platform.kernel.registry import registry
from platform.kernel.logging import get_logger

logger = get_logger(__name__)


class GenerateFromRequirements:
    """Use case for generating code from requirements."""

    def __init__(
        self,
        llm_client: LLMClient,
        artifact_writer: ArtifactWriter,
    ):
        self.llm_client = llm_client
        self.artifact_writer = artifact_writer

    def execute(
        self,
        requirements: List[Requirement],
        language: str,
        output_dir: Path,
        context: Optional[ProjectContext] = None,
    ) -> CodeGenReport:
        """Execute code generation from requirements."""
        start_time = time.time()

        logger.info(
            "Starting code generation",
            requirements_count=len(requirements),
            language=language,
            output_dir=str(output_dir),
        )

        # Get language provider
        provider = registry.codegen.get(language)
        if not provider:
            raise ValueError(f"No code generation provider found for language: {language}")

        # Get syntax validator for quick validation
        syntax_validator = registry.syntax.get(language)

        context = context or {}
        all_generated_files = []
        total_tokens = 0

        for requirement in requirements:
            try:
                # Build prompt
                prompt = provider.build_prompt(requirement, context)

                # Create messages for LLM
                messages = [
                    LLMMessage(role="system", content="You are an expert software developer."),
                    LLMMessage(role="user", content=prompt),
                ]

                # Call LLM
                response = self.llm_client.complete(messages)
                total_tokens += response.tokens_used

                # Parse generated files from response
                generated_files = self._parse_generated_files(
                    response.content, provider.get_file_extension()
                )

                # Post-process files
                processed_files = provider.postprocess(generated_files)

                # Quick syntax validation if available
                if syntax_validator:
                    for file in processed_files:
                        validation_result = syntax_validator.validate(Path(file.path), file.content)
                        if validation_result.status != "valid":
                            logger.warning(
                                "Generated file has syntax issues",
                                file=file.path,
                                issues=len(validation_result.issues),
                            )

                all_generated_files.extend(processed_files)

                logger.info(
                    "Generated code for requirement",
                    requirement_id=requirement.id,
                    files_generated=len(processed_files),
                    tokens_used=response.tokens_used,
                )

            except Exception as e:
                logger.error(
                    "Failed to generate code for requirement",
                    requirement_id=requirement.id,
                    error=str(e),
                )
                raise

        # Write artifacts
        self.artifact_writer.write(output_dir, all_generated_files)

        # Create report
        generation_time = time.time() - start_time
        report = CodeGenReport(
            files=all_generated_files,
            rationale=f"Generated {len(all_generated_files)} files for {len(requirements)} requirements",
            cost_tokens=total_tokens,
            generation_time_seconds=generation_time,
        )

        # Write report
        self.artifact_writer.write_report(output_dir, report.model_dump())

        logger.info(
            "Code generation completed",
            files_generated=len(all_generated_files),
            total_tokens=total_tokens,
            generation_time=generation_time,
        )

        return report

    def _parse_generated_files(self, content: str, file_extension: str) -> List[GeneratedFile]:
        """Parse generated files from LLM response."""
        files = []
        lines = content.split("\n")
        current_file = None
        current_content = []

        for line in lines:
            # Look for file markers
            if line.strip().startswith("# File:"):
                # Save previous file if exists
                if current_file:
                    files.append(
                        GeneratedFile(path=current_file, content="\n".join(current_content))
                    )

                # Start new file
                current_file = line.replace("# File:", "").strip()
                if not current_file.endswith(file_extension):
                    current_file += file_extension
                current_content = []
            elif current_file:
                current_content.append(line)

        # Save last file
        if current_file:
            files.append(GeneratedFile(path=current_file, content="\n".join(current_content)))

        # If no file markers found, create a default file
        if not files:
            files.append(GeneratedFile(path=f"generated_code{file_extension}", content=content))

        return files
