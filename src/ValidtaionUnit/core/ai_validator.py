"""
AI-powered validation component for logic analysis.
"""

import time
import logging
import json
from typing import Dict, Any, List, Optional

from ..models.validation_result import ValidationResult, ValidationStatus
from ..utils.helpers import ValidationHelper
from ..utils.config import ValidationConfig


class AIValidator:
    """AI-powered validator for logic analysis."""

    def __init__(self, config: ValidationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.ai_client = None
        self._initialize_ai_client()

    def _initialize_ai_client(self):
        """Initialize AI client if available."""
        try:
            # Try to import and initialize the existing AI system
            import sys
            import os

            # Add the project root to path to import ai module
            project_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../..")
            )
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            from src.AI.ai import ai_client

            self.ai_client = ai_client
            self.logger.info("AI client initialized successfully")

        except Exception as e:
            self.logger.warning(f"Could not initialize AI client: {e}")
            self.ai_client = None

    def validate(
        self, codebase_path: str, metadata: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate logic using AI analysis.

        Args:
            codebase_path: Path to the codebase directory
            metadata: Metadata about the codebase

        Returns:
            ValidationResult with AI validation results
        """
        start_time = time.time()
        result = ValidationResult(
            step_name="AI Logic Validation",
            status=ValidationStatus.VALID,
            is_valid=True,
        )

        try:
            self.logger.info("Starting AI logic validation")

            if not self.ai_client:
                result.add_warning("AI client not available - skipping AI validation")
                result.status = ValidationStatus.SKIPPED
                result.metadata["ai_available"] = False
                return result

            # Prepare data for AI analysis
            analysis_data = self._prepare_analysis_data(codebase_path, metadata)

            if (
                not analysis_data["file_functions"]
                and not analysis_data["requirements"]
            ):
                result.add_warning("No code or requirements found for AI analysis")
                result.metadata["analysis_performed"] = False
                return result

            # Perform AI analysis
            ai_response = self._perform_ai_analysis(analysis_data, result)

            if ai_response:
                self._process_ai_response(ai_response, result)

            # Set metadata
            result.metadata.update(
                {
                    "ai_available": True,
                    "analysis_performed": True,
                    "files_analyzed": len(metadata.get("files", [])),
                    "requirements_analyzed": len(analysis_data.get("requirements", [])),
                    "ai_model_used": "Azure OpenAI",
                    "analysis_data": {
                        "functions_count": analysis_data.get("functions_count", 0),
                        "classes_count": analysis_data.get("classes_count", 0),
                        "total_files": len(metadata.get("files", [])),
                    },
                }
            )

            self.logger.info("AI logic validation completed")

        except Exception as e:
            result.add_error(f"AI validation failed: {str(e)}")
            result.status = ValidationStatus.ERROR
            self.logger.error(f"AI validation error: {e}")

        finally:
            result.execution_time = time.time() - start_time

        return result

    def _prepare_analysis_data(
        self, codebase_path: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare data for AI analysis."""
        # Create file and function summary
        file_functions = ValidationHelper.create_file_function_summary(metadata)

        # Get requirements if available
        requirements_path = f"{codebase_path.rstrip('/')}/requirements.csv"
        if not requirements_path.endswith("/requirements.csv"):
            # Look for requirements in parent directories
            import os

            parent_dir = os.path.dirname(codebase_path)
            requirements_path = os.path.join(
                parent_dir, "enviroment", "requirements.csv"
            )

        requirements = ValidationHelper.extract_requirements_from_csv(requirements_path)

        # Count functions and classes
        functions_count = 0
        classes_count = 0

        for file_data in metadata.get("files", []):
            functions_count += len(file_data.get("functions", []))
            classes_count += len(file_data.get("classes", []))

            for cls in file_data.get("classes", []):
                functions_count += len(cls.get("methods", []))

        return {
            "file_functions": file_functions,
            "requirements": requirements,
            "functions_count": functions_count,
            "classes_count": classes_count,
            "entry_points": metadata.get("entry_points", []),
            "dependencies": metadata.get("dependencies", {}),
        }

    def _perform_ai_analysis(
        self, analysis_data: Dict[str, Any], result: ValidationResult
    ) -> Optional[Dict[str, Any]]:
        """Perform AI analysis on the code."""
        try:
            # Format requirements for the prompt
            requirements_text = ""
            if analysis_data["requirements"]:
                requirements_text = "\n".join(
                    [
                        f"- {req.get('id', '')}: {req.get('description', '')}"
                        for req in analysis_data["requirements"]
                    ]
                )
            else:
                requirements_text = "No specific requirements provided. Please analyze general code quality and logic."

            # Create the analysis prompt
            prompt = self.config.ai_validation_prompt_template.format(
                file_functions=analysis_data["file_functions"],
                requirements=requirements_text,
            )

            # Call AI client
            self.logger.debug("Sending request to AI client")

            response = self.ai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert code reviewer and software architect. "
                            "Analyze the provided code for logic correctness, implementation quality, "
                            "and requirement fulfillment. Respond with valid JSON only."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.config.ai_max_tokens,
                temperature=self.config.ai_temperature,
            )

            ai_response_text = response.choices[0].message.content.strip()
            self.logger.debug(f"AI response length: {len(ai_response_text)}")

            # Try to parse JSON response
            try:
                # Clean up response if needed
                if ai_response_text.startswith("```json"):
                    ai_response_text = ai_response_text[7:]
                if ai_response_text.endswith("```"):
                    ai_response_text = ai_response_text[:-3]

                ai_response = json.loads(ai_response_text.strip())
                return ai_response

            except json.JSONDecodeError as e:
                result.add_warning(f"Could not parse AI response as JSON: {str(e)}")
                # Return a basic response based on text analysis
                return self._parse_text_response(ai_response_text)

        except Exception as e:
            self.logger.error(f"Error calling AI client: {e}")
            result.add_warning(f"AI analysis failed: {str(e)}")
            return None

    def _parse_text_response(self, text_response: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails."""
        # Basic text analysis to extract insights
        response = {"valid": True, "problems": [], "suggestions": []}

        # Look for negative indicators
        negative_indicators = [
            "error",
            "incorrect",
            "wrong",
            "bug",
            "issue",
            "problem",
            "missing",
            "incomplete",
            "invalid",
            "fail",
        ]

        text_lower = text_response.lower()

        for indicator in negative_indicators:
            if indicator in text_lower:
                response["valid"] = False
                response["problems"].append(
                    f"AI detected potential issues related to: {indicator}"
                )
                break

        # Extract suggestions if present
        if "suggest" in text_lower or "recommend" in text_lower:
            response["suggestions"].append(
                "AI provided suggestions for improvement (see full response)"
            )

        response["raw_response"] = text_response
        return response

    def _process_ai_response(
        self, ai_response: Dict[str, Any], result: ValidationResult
    ):
        """Process the AI response and update validation result."""
        try:
            # Check if code is valid according to AI
            is_valid = ai_response.get("valid", True)

            if not is_valid:
                result.is_valid = False
                result.status = ValidationStatus.INVALID

            # Process problems
            problems = ai_response.get("problems", [])
            for problem in problems:
                if isinstance(problem, str):
                    result.add_error(
                        f"AI detected issue: {problem}", error_code="AI_LOGIC_ERROR"
                    )
                elif isinstance(problem, dict):
                    problem_msg = problem.get("description", str(problem))
                    severity = problem.get("severity", "error").lower()

                    if severity == "error":
                        result.add_error(
                            f"AI detected issue: {problem_msg}",
                            error_code="AI_LOGIC_ERROR",
                        )
                    else:
                        result.add_warning(
                            f"AI detected concern: {problem_msg}",
                            error_code="AI_LOGIC_WARNING",
                        )

            # Process suggestions
            suggestions = ai_response.get("suggestions", [])
            for suggestion in suggestions:
                if isinstance(suggestion, str):
                    result.add_info(f"AI suggestion: {suggestion}")
                elif isinstance(suggestion, dict):
                    suggestion_msg = suggestion.get("description", str(suggestion))
                    result.add_info(f"AI suggestion: {suggestion_msg}")

            # Add additional insights if available
            if "insights" in ai_response:
                result.metadata["ai_insights"] = ai_response["insights"]

            if "confidence" in ai_response:
                result.metadata["ai_confidence"] = ai_response["confidence"]

            if "raw_response" in ai_response:
                result.metadata["ai_raw_response"] = ai_response["raw_response"]

            self.logger.info(
                f"AI analysis completed - Valid: {is_valid}, Problems: {len(problems)}, Suggestions: {len(suggestions)}"
            )

        except Exception as e:
            result.add_warning(f"Error processing AI response: {str(e)}")
            self.logger.error(f"Error processing AI response: {e}")

    def _extract_keywords(self, requirement_text: str) -> List[str]:
        """Extract key words from requirement text."""
        # Simple keyword extraction
        common_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "must",
            "shall",
        }

        words = requirement_text.replace(",", " ").replace(".", " ").split()
        keywords = []

        for word in words:
            word = word.strip().lower()
            if len(word) > 3 and word not in common_words:
                keywords.append(word)

        return keywords[:5]  # Limit to top 5 keywords
