"""S3 - Validation Use Cases with Pipeline."""

from typing import List, Optional
from pathlib import Path
from platform.domain.models.requirements import Requirement
from platform.domain.models.metadata import ProjectMetadata
from platform.domain.models.validation import (
    SyntaxResult,
    TestResult,
    AILogicReport,
    AILogicFinding,
)
from platform.ports.fs import FileSystem
from platform.ports.runners import TestRunner, Sandbox
from platform.ports.ai import LLMClient, LLMMessage
from platform.ports.providers import SyntaxValidator
from platform.kernel.registry import registry
from platform.kernel.config import config
from platform.kernel.logging import get_logger

logger = get_logger(__name__)


class ValidationPipeline:
    """Pipeline for comprehensive validation: syntax → tests → AI logic."""

    def __init__(
        self,
        file_system: FileSystem,
        test_runner: TestRunner,
        sandbox: Sandbox,
        llm_client: LLMClient,
    ):
        self.file_system = file_system
        self.test_runner = test_runner
        self.sandbox = sandbox
        self.llm_client = llm_client

    def execute(
        self,
        project_path: Path,
        requirements: Optional[List[Requirement]] = None,
        metadata: Optional[ProjectMetadata] = None,
        run_tests: bool = True,
        ai_check: bool = False,
    ) -> "ValidationReport":
        """Execute the validation pipeline."""
        logger.info(
            "Starting validation pipeline",
            project_path=str(project_path),
            run_tests=run_tests,
            ai_check=ai_check,
        )

        # Stage 1: Syntax Validation
        syntax_results = self._validate_syntax(project_path)

        # Short-circuit if syntax validation fails and policy requires it
        if self._should_fail_on_syntax(syntax_results):
            logger.warning("Validation failed at syntax stage")
            return ValidationReport(
                syntax_results=syntax_results,
                test_result=None,
                ai_logic_report=None,
                overall_status="failed",
            )

        # Stage 2: Test Execution
        test_result = None
        if run_tests:
            test_result = self._run_tests(project_path)

            if self._should_fail_on_tests(test_result):
                logger.warning("Validation failed at test stage")
                return ValidationReport(
                    syntax_results=syntax_results,
                    test_result=test_result,
                    ai_logic_report=None,
                    overall_status="failed",
                )

        # Stage 3: AI Logic Check
        ai_logic_report = None
        if ai_check and requirements:
            ai_logic_report = self._check_ai_logic(requirements, metadata, project_path)

        # Determine overall status
        overall_status = self._determine_overall_status(
            syntax_results, test_result, ai_logic_report
        )

        report = ValidationReport(
            syntax_results=syntax_results,
            test_result=test_result,
            ai_logic_report=ai_logic_report,
            overall_status=overall_status,
        )

        logger.info(
            "Validation pipeline completed",
            overall_status=overall_status,
            syntax_issues=sum(len(r.issues) for r in syntax_results),
            tests_run=test_result.passed + test_result.failed if test_result else 0,
            ai_findings=len(ai_logic_report.findings) if ai_logic_report else 0,
        )

        return report

    def _validate_syntax(self, project_path: Path) -> List[SyntaxResult]:
        """Validate syntax for all supported files."""
        results = []

        # Scan for files
        files = self.file_system.scan(
            project_path,
            exclude_dirs=config.ignored_directories,
            max_size_mb=config.max_file_size_mb,
        )

        for file_path in files:
            try:
                # Find syntax validator
                validator = self._find_validator_for_file(file_path)
                if not validator:
                    continue

                # Read content
                content = self.file_system.read_text(file_path)

                # Validate
                result = validator.validate(file_path, content)
                results.append(result)

                if result.issues:
                    logger.debug(
                        "Syntax issues found", file=str(file_path), issues=len(result.issues)
                    )

            except Exception as e:
                logger.error("Syntax validation failed for file", file=str(file_path), error=str(e))
                continue

        return results

    def _run_tests(self, project_path: Path) -> Optional[TestResult]:
        """Run tests using available test runners."""
        try:
            if self.test_runner.can_handle(project_path):
                return self.test_runner.run(project_path, timeout_seconds=config.test_timeout)
            else:
                logger.info("No suitable test runner found for project")
                return None

        except Exception as e:
            logger.error("Test execution failed", error=str(e))
            return TestResult(status="error", errors=1)

    def _check_ai_logic(
        self,
        requirements: List[Requirement],
        metadata: Optional[ProjectMetadata],
        project_path: Path,
    ) -> AILogicReport:
        """Check logic consistency using AI."""
        try:
            # Build prompt for AI logic check
            prompt = self._build_ai_logic_prompt(requirements, metadata, project_path)

            messages = [
                LLMMessage(
                    role="system",
                    content="You are an expert code reviewer. Analyze if the code satisfies the given requirements.",
                ),
                LLMMessage(role="user", content=prompt),
            ]

            response = self.llm_client.complete(messages, temperature=0.1)

            # Parse AI response into findings
            findings = self._parse_ai_findings(response.content, requirements)

            # Determine overall status
            contradicted = any(f.verdict == "contradicted" for f in findings)
            status = "fail" if contradicted else "ok"

            return AILogicReport(status=status, findings=findings)

        except Exception as e:
            logger.error("AI logic check failed", error=str(e))
            return AILogicReport(
                status="fail",
                findings=[
                    AILogicFinding(
                        requirement_id="unknown",
                        verdict="uncertain",
                        rationale=f"AI check failed: {str(e)}",
                    )
                ],
            )

    def _build_ai_logic_prompt(
        self,
        requirements: List[Requirement],
        metadata: Optional[ProjectMetadata],
        project_path: Path,
    ) -> str:
        """Build prompt for AI logic checking."""
        prompt_parts = [
            "Please analyze if the code satisfies the given requirements.",
            "",
            "## Requirements:",
        ]

        for req in requirements:
            prompt_parts.append(f"**{req.id}**: {req.title}")
            prompt_parts.append(f"Description: {req.description}")
            if req.acceptance:
                prompt_parts.append("Acceptance Criteria:")
                for criteria in req.acceptance:
                    prompt_parts.append(f"- {criteria}")
            prompt_parts.append("")

        if metadata:
            prompt_parts.append("## Code Structure:")
            prompt_parts.append(f"Languages: {', '.join(metadata.languages)}")
            prompt_parts.append(f"Total files: {len(metadata.files)}")
            prompt_parts.append("")

            for file_meta in metadata.files[:10]:  # Limit to first 10 files
                prompt_parts.append(f"**{file_meta.path}** ({file_meta.language}):")
                prompt_parts.append(f"- Functions: {', '.join(file_meta.functions[:5])}")
                prompt_parts.append(f"- Classes: {', '.join(file_meta.classes[:5])}")
                prompt_parts.append("")

        prompt_parts.extend(
            [
                "## Instructions:",
                "For each requirement, provide your verdict as one of:",
                "- 'supported': Code clearly implements this requirement",
                "- 'contradicted': Code contradicts or violates this requirement",
                "- 'uncertain': Cannot determine from available information",
                "",
                "Respond in this format:",
                "REQUIREMENT_ID: verdict - rationale",
            ]
        )

        return "\n".join(prompt_parts)

    def _parse_ai_findings(
        self, ai_response: str, requirements: List[Requirement]
    ) -> List[AILogicFinding]:
        """Parse AI response into structured findings."""
        findings = []
        lines = ai_response.split("\n")

        for line in lines:
            line = line.strip()
            if ":" in line and any(
                verdict in line.lower() for verdict in ["supported", "contradicted", "uncertain"]
            ):
                try:
                    req_id, rest = line.split(":", 1)
                    req_id = req_id.strip()

                    # Extract verdict and rationale
                    rest = rest.strip()
                    for verdict in ["supported", "contradicted", "uncertain"]:
                        if verdict in rest.lower():
                            rationale = rest.replace(verdict, "").replace("-", "").strip()
                            findings.append(
                                AILogicFinding(
                                    requirement_id=req_id,
                                    verdict=verdict,
                                    rationale=rationale or f"Marked as {verdict}",
                                )
                            )
                            break
                except Exception as e:
                    logger.debug("Failed to parse AI finding line", line=line, error=str(e))
                    continue

        # Ensure all requirements have findings
        found_req_ids = {f.requirement_id for f in findings}
        for req in requirements:
            if req.id not in found_req_ids:
                findings.append(
                    AILogicFinding(
                        requirement_id=req.id,
                        verdict="uncertain",
                        rationale="No analysis provided by AI",
                    )
                )

        return findings

    def _find_validator_for_file(self, file_path: Path) -> Optional[SyntaxValidator]:
        """Find syntax validator for a file."""
        for language in registry.syntax.get_supported_languages():
            validator = registry.syntax.get(language)
            if validator and validator.can_handle(file_path):
                return validator
        return None

    def _should_fail_on_syntax(self, results: List[SyntaxResult]) -> bool:
        """Check if pipeline should fail due to syntax issues."""
        return any(r.status == "invalid" for r in results)

    def _should_fail_on_tests(self, result: Optional[TestResult]) -> bool:
        """Check if pipeline should fail due to test failures."""
        return result is not None and result.status == "failed"

    def _determine_overall_status(
        self,
        syntax_results: List[SyntaxResult],
        test_result: Optional[TestResult],
        ai_logic_report: Optional[AILogicReport],
    ) -> str:
        """Determine overall validation status."""
        if self._should_fail_on_syntax(syntax_results):
            return "failed"

        if self._should_fail_on_tests(test_result):
            return "failed"

        if ai_logic_report and ai_logic_report.status == "fail":
            return "failed"

        # Check for warnings
        has_warnings = (
            any(r.issues for r in syntax_results)
            or (test_result and test_result.failed > 0)
            or (ai_logic_report and any(f.verdict == "uncertain" for f in ai_logic_report.findings))
        )

        return "warnings" if has_warnings else "passed"


class ValidationReport:
    """Validation pipeline report."""

    def __init__(
        self,
        syntax_results: List[SyntaxResult],
        test_result: Optional[TestResult],
        ai_logic_report: Optional[AILogicReport],
        overall_status: str,
    ):
        self.syntax_results = syntax_results
        self.test_result = test_result
        self.ai_logic_report = ai_logic_report
        self.overall_status = overall_status
