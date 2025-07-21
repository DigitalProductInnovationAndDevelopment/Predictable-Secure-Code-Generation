"""
Main code generator that orchestrates the entire code generation workflow.
"""

import json
import logging
import subprocess
import sys
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import components from other systems
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from CheckCodeRequirements.checkNewRequirments import compare_requirements
    from CheckCodeRequirements.adapters.readRequirementsFromCSV import (
        read_requirements_csv,
    )
except ImportError:
    # Fallback for testing
    def compare_requirements(current_reqs, new_reqs):
        return {"added": new_reqs, "modified": {}}

    def read_requirements_csv(file_path):
        import csv

        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return {row["id"]: row["description"].strip() for row in reader}


try:
    from AIBrain.ai import AzureOpenAIClient
except ImportError:
    # Fallback for testing
    class AzureOpenAIClient:
        def __init__(self):
            pass

        def ask_question(self, question, **kwargs):
            return {"status": "error", "error": "AI client not available"}


from .analyzer import RequirementAnalyzer
from .integrator import CodeIntegrator

sys.path.append(str(Path(__file__).parent.parent))
from models.requirement_data import RequirementData, RequirementStatus
from models.code_change import CodeChange, ChangeType
from models.generation_result import GenerationResult, GenerationStatus


class CodeGenerator:
    """Main code generation orchestrator."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the code generator."""
        self.logger = logger or logging.getLogger(__name__)
        self.analyzer = RequirementAnalyzer(logger)
        self.integrator = CodeIntegrator(logger)
        self.ai_client = None

        # Initialize AI client
        try:
            self.ai_client = AzureOpenAIClient()
            self.logger.info("AI client initialized successfully")
        except Exception as e:
            self.logger.warning(f"AI client initialization failed: {str(e)}")

    def generate_from_requirements(
        self,
        project_path: str,
        requirements_path: str,
        metadata_path: str,
        output_path: str,
        existing_requirements_path: Optional[str] = None,
    ) -> GenerationResult:
        """
        Generate code from requirements with full workflow.

        Args:
            project_path: Path to source project
            requirements_path: Path to requirements CSV file
            metadata_path: Path to project metadata JSON
            output_path: Path to output directory
            existing_requirements_path: Path to existing requirements (optional)

        Returns:
            GenerationResult with operation details
        """
        start_time = time.time()
        result = GenerationResult(GenerationStatus.IN_PROGRESS)
        result.source_path = project_path
        result.output_path = output_path
        result.requirements_path = requirements_path
        result.metadata_path = metadata_path

        try:
            self.logger.info("Starting code generation workflow")

            # Step 1: Check requirements and identify what needs implementation
            requirements_to_implement = self._check_requirements(
                requirements_path, existing_requirements_path, result
            )

            if not requirements_to_implement:
                self.logger.info("No new requirements to implement")
                result.status = GenerationStatus.SUCCESS
                result.execution_time = time.time() - start_time
                return result

            # Step 2: Load and analyze metadata
            metadata = self._load_metadata(metadata_path, result)
            if not metadata:
                result.status = GenerationStatus.FAILED
                result.execution_time = time.time() - start_time
                return result

            # Step 3: Analyze requirements against metadata
            requirement_objects = self.analyzer.analyze_requirements(
                requirements_to_implement, metadata, result
            )

            # Step 4: Prepare output directory
            if not self.integrator.prepare_output_directory(project_path, output_path):
                result.add_problem(
                    "error",
                    "integration",
                    f"Failed to prepare output directory: {output_path}",
                )
                result.status = GenerationStatus.FAILED
                result.execution_time = time.time() - start_time
                return result

            # Step 5: Generate code for each requirement
            code_changes = []
            for req_data in requirement_objects:
                if req_data.status == RequirementStatus.FAILED:
                    result.requirements_failed += 1
                    continue

                changes = self._generate_code_for_requirement(
                    req_data, metadata, result
                )
                code_changes.extend(changes)

            # Step 6: Apply code changes
            if code_changes:
                self.integrator.apply_code_changes(code_changes, output_path, result)

            # Step 7: Generate and apply tests
            self._generate_and_apply_tests(requirement_objects, output_path, result)

            # Step 8: Update metadata
            self._update_metadata(output_path, metadata_path, result)

            # Step 9: Run validation
            self._run_validation(output_path, result)

            # Determine final status
            if result.has_errors():
                result.status = (
                    GenerationStatus.PARTIAL_SUCCESS
                    if result.requirements_implemented > 0
                    else GenerationStatus.FAILED
                )
            else:
                result.status = GenerationStatus.SUCCESS

            result.execution_time = time.time() - start_time
            self.logger.info(
                f"Code generation completed in {result.execution_time:.2f}s"
            )

            return result

        except Exception as e:
            self.logger.error(f"Code generation failed: {str(e)}")
            result.add_problem("error", "generation", f"Generation failed: {str(e)}")
            result.status = GenerationStatus.FAILED
            result.execution_time = time.time() - start_time
            return result

    def _check_requirements(
        self,
        requirements_path: str,
        existing_requirements_path: Optional[str],
        result: GenerationResult,
    ) -> Dict[str, str]:
        """Check which requirements need to be implemented."""
        try:
            self.logger.info("Checking requirements for implementation needs")

            # Load new requirements
            new_requirements = read_requirements_csv(requirements_path)

            if existing_requirements_path and Path(existing_requirements_path).exists():
                # Load existing requirements and compare
                existing_requirements = read_requirements_csv(
                    existing_requirements_path
                )
                comparison = compare_requirements(
                    existing_requirements, new_requirements
                )

                # Combine added and modified requirements
                requirements_to_implement = {
                    **comparison["added"],
                    **comparison["modified"],
                }

                self.logger.info(
                    f"Found {len(comparison['added'])} new and "
                    f"{len(comparison['modified'])} modified requirements"
                )
            else:
                # All requirements are new
                requirements_to_implement = new_requirements
                self.logger.info(f"All {len(new_requirements)} requirements are new")

            return requirements_to_implement

        except Exception as e:
            error_msg = f"Failed to check requirements: {str(e)}"
            self.logger.error(error_msg)
            result.add_problem("error", "requirement", error_msg)
            return {}

    def _load_metadata(
        self, metadata_path: str, result: GenerationResult
    ) -> Optional[Dict[str, Any]]:
        """Load project metadata."""
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            self.logger.info(f"Loaded metadata from {metadata_path}")
            return metadata

        except Exception as e:
            error_msg = f"Failed to load metadata: {str(e)}"
            self.logger.error(error_msg)
            result.add_problem("error", "metadata", error_msg)
            return None

    def _generate_code_for_requirement(
        self,
        req_data: RequirementData,
        metadata: Dict[str, Any],
        result: GenerationResult,
    ) -> List[CodeChange]:
        """Generate code changes for a single requirement."""
        changes = []

        try:
            if not self.ai_client:
                self.logger.warning(
                    f"No AI client available for requirement {req_data.id}"
                )
                req_data.mark_failed("AI client not available")
                result.requirements_failed += 1
                return changes

            self.logger.info(f"Generating code for requirement {req_data.id}")

            # Create context for AI
            context = self._build_ai_context(req_data, metadata)

            # Generate code using AI
            ai_response = self.ai_client.ask_question(
                question=f"Generate Python code for this requirement: {req_data.description}\n\nContext:\n{context}",
                system_prompt=self._get_code_generation_prompt(),
                max_tokens=2000,
            )

            if ai_response["status"] != "success":
                req_data.mark_failed(
                    f"AI generation failed: {ai_response.get('error', 'Unknown error')}"
                )
                result.requirements_failed += 1
                return changes

            generated_code = ai_response["answer"]
            result.ai_tokens_used += ai_response["usage"]["total_tokens"]

            # Parse generated code and create changes
            changes = self._parse_generated_code(req_data, generated_code, metadata)

            if changes:
                req_data.mark_implemented(generated_code)
                result.requirements_implemented += 1
                self.logger.info(
                    f"Generated {len(changes)} code changes for requirement {req_data.id}"
                )
            else:
                req_data.mark_failed("No valid code changes generated")
                result.requirements_failed += 1

            return changes

        except Exception as e:
            error_msg = f"Code generation failed for {req_data.id}: {str(e)}"
            self.logger.error(error_msg)
            req_data.mark_failed(error_msg)
            result.add_problem(
                "error", "generation", error_msg, requirement_id=req_data.id
            )
            result.requirements_failed += 1
            return changes

    def _build_ai_context(
        self, req_data: RequirementData, metadata: Dict[str, Any]
    ) -> str:
        """Build context information for AI code generation."""
        context_parts = []

        # Add requirement details
        context_parts.append(f"Requirement ID: {req_data.id}")
        context_parts.append(f"Description: {req_data.description}")
        context_parts.append(f"Complexity Score: {req_data.complexity_score}")
        context_parts.append(f"Implementation Notes: {req_data.implementation_notes}")

        # Add target files information
        if req_data.target_files:
            context_parts.append(f"Target Files: {', '.join(req_data.target_files)}")

            # Add relevant file contents
            for file_path in req_data.target_files[:2]:  # Limit to first 2 files
                file_info = self._get_file_info_from_metadata(file_path, metadata)
                if file_info:
                    context_parts.append(f"\nFile: {file_path}")
                    context_parts.append(
                        f"Functions: {[f['name'] for f in file_info.get('functions', [])]}"
                    )
                    context_parts.append(
                        f"Classes: {[c['name'] for c in file_info.get('classes', [])]}"
                    )

        # Add dependencies
        if req_data.dependencies:
            context_parts.append(f"Dependencies: {', '.join(req_data.dependencies)}")

        # Add project structure overview
        if "files" in metadata:
            file_list = [
                f["path"]
                for f in metadata["files"]
                if not any(test in f["path"] for test in ["test", "__pycache__"])
            ]
            context_parts.append(
                f"Project Files: {', '.join(file_list[:10])}"
            )  # First 10 files

        return "\n".join(context_parts)

    def _get_file_info_from_metadata(
        self, file_path: str, metadata: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get file information from metadata."""
        for file_info in metadata.get("files", []):
            if file_info.get("path") == file_path:
                return file_info
        return None

    def _get_code_generation_prompt(self) -> str:
        """Get the system prompt for code generation."""
        return """You are an expert Python developer. Generate clean, well-documented Python code based on requirements.

Guidelines:
1. Follow PEP 8 style guidelines
2. Include proper docstrings for functions and classes
3. Add type hints where appropriate
4. Include error handling and validation
5. Write modular, reusable code
6. Consider existing code structure and patterns

Response format:
- Provide only the Python code
- Include comments explaining complex logic
- Ensure code is syntactically correct
- Make functions and classes self-contained when possible

Focus on creating production-ready code that integrates well with existing codebase."""

    def _parse_generated_code(
        self, req_data: RequirementData, generated_code: str, metadata: Dict[str, Any]
    ) -> List[CodeChange]:
        """Parse generated code and create appropriate code changes."""
        changes = []

        try:
            # Clean up the generated code
            code_lines = generated_code.split("\n")
            clean_lines = []
            in_code_block = False

            for line in code_lines:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block or (
                    not line.startswith("```") and "python" not in line.lower()
                ):
                    clean_lines.append(line)

            clean_code = "\n".join(clean_lines).strip()

            if not clean_code:
                self.logger.warning(
                    f"No clean code generated for requirement {req_data.id}"
                )
                return changes

            # Determine where to place the code
            if req_data.target_files:
                target_file = req_data.target_files[0]  # Use first target file

                # Check if it's a class or function
                if clean_code.strip().startswith("class "):
                    change = CodeChange(
                        change_type=ChangeType.ADD_CLASS,
                        file_path=target_file,
                        content=clean_code,
                        requirement_id=req_data.id,
                        description=f"Add class for requirement {req_data.id}",
                    )
                elif clean_code.strip().startswith("def "):
                    change = CodeChange(
                        change_type=ChangeType.ADD_FUNCTION,
                        file_path=target_file,
                        content=clean_code,
                        requirement_id=req_data.id,
                        description=f"Add function for requirement {req_data.id}",
                    )
                else:
                    # General code addition
                    change = CodeChange(
                        change_type=ChangeType.MODIFY_FILE,
                        file_path=target_file,
                        content=self._merge_code_with_existing(
                            target_file, clean_code, metadata
                        ),
                        requirement_id=req_data.id,
                        description=f"Modify file for requirement {req_data.id}",
                    )

                changes.append(change)
            else:
                # Create new file
                new_file = f"{req_data.id.lower().replace(' ', '_')}.py"
                change = CodeChange(
                    change_type=ChangeType.CREATE_FILE,
                    file_path=new_file,
                    content=clean_code,
                    requirement_id=req_data.id,
                    description=f"Create new file for requirement {req_data.id}",
                )
                changes.append(change)

            # Check for import requirements
            imports = self._extract_required_imports(clean_code)
            for target_file in req_data.target_files or [
                changes[0].file_path if changes else ""
            ]:
                for import_stmt in imports:
                    if not self._import_exists_in_file(
                        target_file, import_stmt, metadata
                    ):
                        import_change = CodeChange(
                            change_type=ChangeType.ADD_IMPORT,
                            file_path=target_file,
                            content=import_stmt,
                            requirement_id=req_data.id,
                            description=f"Add import for requirement {req_data.id}",
                        )
                        changes.append(import_change)

            return changes

        except Exception as e:
            self.logger.error(
                f"Failed to parse generated code for {req_data.id}: {str(e)}"
            )
            return []

    def _merge_code_with_existing(
        self, file_path: str, new_code: str, metadata: Dict[str, Any]
    ) -> str:
        """Merge new code with existing file content."""
        # Get existing file content from metadata or return new code
        file_info = self._get_file_info_from_metadata(file_path, metadata)
        if not file_info:
            return new_code

        # Simple merge - append new code to end
        # In a real implementation, this would be more sophisticated
        return new_code  # For now, just use new code

    def _extract_required_imports(self, code: str) -> List[str]:
        """Extract import statements that might be needed for the code."""
        imports = []

        # Common patterns that suggest imports
        import_patterns = {
            "typing": ["List", "Dict", "Optional", "Any", "Union"],
            "datetime": ["datetime", "date", "time"],
            "json": ["json."],
            "os": ["os.path", "os."],
            "sys": ["sys."],
            "pathlib": ["Path"],
            "logging": ["logging."],
            "argparse": ["ArgumentParser", "argparse"],
        }

        for module, patterns in import_patterns.items():
            if any(pattern in code for pattern in patterns):
                if module == "typing":
                    # Extract specific typing imports
                    typing_imports = [p for p in patterns if p in code]
                    if typing_imports:
                        imports.append(
                            f"from typing import {', '.join(typing_imports)}"
                        )
                else:
                    imports.append(f"import {module}")

        return imports

    def _import_exists_in_file(
        self, file_path: str, import_stmt: str, metadata: Dict[str, Any]
    ) -> bool:
        """Check if import already exists in file."""
        file_info = self._get_file_info_from_metadata(file_path, metadata)
        if not file_info:
            return False

        existing_imports = file_info.get("imports", [])
        return any(imp in import_stmt for imp in existing_imports)

    def _generate_and_apply_tests(
        self,
        requirement_objects: List[RequirementData],
        output_path: str,
        result: GenerationResult,
    ):
        """Generate and apply test cases for implemented requirements."""
        if not self.ai_client:
            self.logger.warning("No AI client available for test generation")
            return

        for req_data in requirement_objects:
            if req_data.status != RequirementStatus.IMPLEMENTED:
                continue

            try:
                self.logger.info(f"Generating tests for requirement {req_data.id}")

                test_prompt = f"""Generate pytest test cases for this requirement:
                
Requirement: {req_data.description}
Generated Code: {req_data.generated_code}
Target Files: {', '.join(req_data.target_files)}

Generate comprehensive test cases that:
1. Test normal functionality
2. Test edge cases
3. Test error conditions
4. Include proper imports and setup"""

                ai_response = self.ai_client.ask_question(
                    question=test_prompt,
                    system_prompt="You are an expert at writing Python test cases using pytest. Generate clean, comprehensive test code.",
                    max_tokens=1500,
                )

                if ai_response["status"] == "success":
                    test_code = ai_response["answer"]
                    result.ai_tokens_used += ai_response["usage"]["total_tokens"]

                    # Clean and save test code
                    test_code = self._clean_generated_code(test_code)
                    test_file = f"test_{req_data.id.lower().replace(' ', '_')}.py"

                    test_change = CodeChange(
                        change_type=ChangeType.CREATE_TEST,
                        file_path=test_file,
                        content=test_code,
                        requirement_id=req_data.id,
                        description=f"Test cases for requirement {req_data.id}",
                    )

                    if self.integrator.apply_code_changes(
                        [test_change], output_path, result
                    ):
                        req_data.test_code = test_code
                        self.logger.info(
                            f"Generated tests for requirement {req_data.id}"
                        )

            except Exception as e:
                self.logger.error(
                    f"Failed to generate tests for {req_data.id}: {str(e)}"
                )
                result.add_problem(
                    "warning",
                    "testing",
                    f"Test generation failed for {req_data.id}: {str(e)}",
                    requirement_id=req_data.id,
                )

    def _clean_generated_code(self, code: str) -> str:
        """Clean generated code by removing markdown and extra text."""
        lines = code.split("\n")
        clean_lines = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block or not line.strip().startswith("```"):
                clean_lines.append(line)

        return "\n".join(clean_lines).strip()

    def _update_metadata(
        self, output_path: str, metadata_path: str, result: GenerationResult
    ):
        """Update metadata for the generated code."""
        try:
            self.logger.info("Updating metadata for generated code")

            # Run metadata generation on output
            metadata_cmd = [
                sys.executable,
                str(
                    Path(__file__).parent.parent.parent
                    / "GenerateMetadataFromCode"
                    / "main.py"
                ),
                "--project-path",
                output_path,
                "--output-path",
                str(Path(metadata_path).parent),
                "--format",
                "json",
            ]

            subprocess.run(metadata_cmd, check=True, capture_output=True, text=True)
            result.metadata_updated = True
            self.logger.info("Metadata updated successfully")

        except Exception as e:
            self.logger.error(f"Failed to update metadata: {str(e)}")
            result.add_problem(
                "warning", "metadata", f"Metadata update failed: {str(e)}"
            )

    def _run_validation(self, output_path: str, result: GenerationResult):
        """Run validation on the generated code."""
        try:
            self.logger.info("Running validation on generated code")

            # Run validation system
            validation_cmd = [
                sys.executable,
                str(Path(__file__).parent.parent.parent / "ValidationUnit" / "main.py"),
                "--project-path",
                output_path,
                "--format",
                "json",
            ]

            validation_result = subprocess.run(
                validation_cmd, check=False, capture_output=True, text=True
            )

            if validation_result.returncode == 0:
                result.validation_passed = True
                self.logger.info("Validation passed")
            else:
                result.add_problem(
                    "warning",
                    "validation",
                    f"Validation failed: {validation_result.stderr}",
                )
                self.logger.warning("Validation failed")

        except Exception as e:
            self.logger.error(f"Failed to run validation: {str(e)}")
            result.add_problem("warning", "validation", f"Validation error: {str(e)}")
