#!/usr/bin/env python3
"""
Code Validator

This module provides comprehensive code validation using AI assistance.
It validates code against requirements, monitors for problems, and tracks validation results.
"""

import os
import sys
import json
import logging
import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import time

# Path setup for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..", "..", "..")
handle_generic_v2_path = os.path.join(project_root, "HandleGenericV2")
sys.path.insert(0, handle_generic_v2_path)

from config import Config
from aiBrain.ai import AzureOpenAIClient
from adapters.read.readJson import read_json_file
from adapters.read.readRequirements import requirements_csv_to_json
from adapters.write.writeJson import save_json_to_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("code_validation.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class CodeValidator:
    """Comprehensive code validator using AI assistance"""

    def __init__(self, config: Config):
        self.config = config
        self.workspace = config.WORKSPACE
        self.output_code = config.OUTPUT_CODE
        self.requirements_path = config.REQUIREMENTS
        self.metadata_path = config.METADATA
        self.validation_log_file = "code_validation_log.json"

        # Get programming language from config first
        self.language = self._get_programming_language()

        # Initialize AI client
        try:
            self.ai_client = AzureOpenAIClient(config)
            logger.info("✅ AI client initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize AI client: {e}")
            self.ai_client = None

        # Load or create validation log
        self.validation_log = self._load_validation_log()

    def _get_programming_language(self) -> str:
        """Get the programming language from config or metadata"""
        try:
            # Try to get from config first
            if (
                hasattr(self.config, "LANGUAGE_ARCHITECTURE")
                and self.config.LANGUAGE_ARCHITECTURE
            ):
                # Check if it's a file path or just the language name
                lang_value = self.config.LANGUAGE_ARCHITECTURE
                if lang_value.endswith(".json"):
                    # It's a file path, try to read the content
                    try:
                        if os.path.exists(lang_value):
                            with open(lang_value, "r") as f:
                                lang_data = json.load(f)
                                if "programming_language" in lang_data:
                                    return lang_data["programming_language"].upper()
                        else:
                            # Try to construct the full path
                            output_dir = getattr(self.config, "OUTPUT_DIR", "")
                            if output_dir:
                                full_path = os.path.join(output_dir, lang_value)
                                if os.path.exists(full_path):
                                    with open(full_path, "r") as f:
                                        lang_data = json.load(f)
                                        if "programming_language" in lang_data:
                                            return lang_data[
                                                "programming_language"
                                            ].upper()
                    except Exception as e:
                        logger.warning(
                            f"Could not read language file {lang_value}: {e}"
                        )
                else:
                    # It's just the language name
                    return lang_value.upper()

            # Try to get from metadata
            if self.metadata_path and os.path.exists(self.metadata_path):
                metadata = read_json_file(self.metadata_path, workspace=self.workspace)
                if "language" in metadata:
                    return metadata["language"].upper()

            # Default to PYTHON
            return "PYTHON"

        except Exception as e:
            logger.warning(f"Could not determine language: {e}")
            return "PYTHON"

    def _load_validation_log(self) -> Dict[str, Any]:
        """Load existing validation log or create new one"""
        try:
            if os.path.exists(self.validation_log_file):
                with open(self.validation_log_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                return {
                    "created_at": str(datetime.datetime.now()),
                    "workspace": self.workspace,
                    "language": self.language,
                    "validations": [],
                    "total_validations": 0,
                    "passed_validations": 0,
                    "failed_validations": 0,
                    "current_status": "ready",
                }
        except Exception as e:
            logger.warning(f"Could not load validation log: {e}")
            return {
                "created_at": str(datetime.datetime.now()),
                "workspace": self.workspace,
                "language": self.language,
                "validations": [],
                "total_validations": 0,
                "passed_validations": 0,
                "failed_validations": 0,
                "current_status": "ready",
            }

    def _save_validation_log(self):
        """Save the current validation log"""
        try:
            with open(self.validation_log_file, "w", encoding="utf-8") as f:
                json.dump(self.validation_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Could not save validation log: {e}")

    def _get_code_files(self) -> List[Dict[str, Any]]:
        """Get all code files from the output directory"""
        try:
            if not self.output_code or not os.path.exists(self.output_code):
                logger.error(f"Output code directory not found: {self.output_code}")
                return []

            code_files = []
            for root, dirs, files in os.walk(self.output_code):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Check if it's a code file based on extension
                    if self._is_code_file(file):
                        code_files.append(
                            {
                                "name": file,
                                "path": file_path,
                                "relative_path": os.path.relpath(
                                    file_path, self.output_code
                                ),
                                "size": os.path.getsize(file_path),
                                "modified": datetime.datetime.fromtimestamp(
                                    os.path.getmtime(file_path)
                                ).isoformat(),
                            }
                        )

            logger.info(f"Found {len(code_files)} code files to validate")
            return code_files

        except Exception as e:
            logger.error(f"Error getting code files: {e}")
            return []

    def _is_code_file(self, filename: str) -> bool:
        """Check if a file is a code file based on extension"""
        code_extensions = {
            ".py",
            ".js",
            ".ts",
            ".java",
            ".cpp",
            ".c",
            ".cs",
            ".php",
            ".rb",
            ".go",
            ".rs",
            ".swift",
            ".kt",
            ".scala",
            ".clj",
            ".hs",
            ".ml",
        }
        return Path(filename).suffix.lower() in code_extensions

    def _get_requirements(self) -> List[Dict[str, Any]]:
        """Get requirements from CSV file"""
        try:
            if not self.requirements_path or not os.path.exists(self.requirements_path):
                logger.warning(f"Requirements file not found: {self.requirements_path}")
                return []

            requirements_json = requirements_csv_to_json(
                self.requirements_path, workspace=self.workspace
            )
            requirements_data = json.loads(requirements_json)

            if "error" in requirements_data:
                logger.error(
                    f"Error reading requirements: {requirements_data['error']}"
                )
                return []

            return requirements_data.get("requirements", [])

        except Exception as e:
            logger.error(f"Error getting requirements: {e}")
            return []

    def _validate_code_file_with_ai(
        self, code_file: Dict[str, Any], requirements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate a single code file using AI"""
        try:
            if not self.ai_client:
                return {
                    "status": "error",
                    "error": "AI client not available",
                    "validation_result": "skipped",
                }

            # Read the code file
            with open(code_file["path"], "r", encoding="utf-8") as f:
                code_content = f.read()

            # Create validation prompt
            prompt = self._create_validation_prompt(
                code_content, code_file, requirements
            )

            # Ask AI to validate the code
            logger.info(f"🔍 Validating {code_file['name']} with AI...")
            print(f"🔍 Validating {code_file['name']} with AI...")

            result = self.ai_client.ask_question(
                question=prompt, max_tokens=2000, temperature=0.1
            )

            if result["status"] == "success":
                # Parse AI response
                validation_result = self._parse_ai_validation_response(result["answer"])
                return {
                    "status": "success",
                    "validation_result": validation_result,
                    "ai_response": result["answer"],
                    "tokens_used": result["usage"]["total_tokens"],
                }
            else:
                return {
                    "status": "error",
                    "error": result.get("error", "Unknown AI error"),
                    "validation_result": "failed",
                }

        except Exception as e:
            logger.error(f"Error validating {code_file['name']}: {e}")
            return {"status": "error", "error": str(e), "validation_result": "failed"}

    def _create_validation_prompt(
        self,
        code_content: str,
        code_file: Dict[str, Any],
        requirements: List[Dict[str, Any]],
    ) -> str:
        """Create a comprehensive validation prompt for AI"""

        # Create requirements summary
        requirements_summary = "\n".join(
            [
                f"- {req.get('id', 'Unknown')}: {req.get('description', 'No description')}"
                for req in requirements
            ]
        )

        prompt = f"""
Please validate this {self.language} code file against the specified requirements.

FILE: {code_file['name']}
LANGUAGE: {self.language}
REQUIREMENTS:
{requirements_summary}

CODE TO VALIDATE:
```{self.language.lower()}
{code_content}
```

Please provide a comprehensive validation in the following JSON format:
{{
    "validation_status": "PASS" or "FAIL" or "WARNING",
    "overall_score": 0-100,
    "issues": [
        {{
            "severity": "HIGH" or "MEDIUM" or "LOW",
            "type": "ERROR" or "WARNING" or "SUGGESTION",
            "description": "Description of the issue",
            "line_number": "Line number or 'N/A'",
            "suggestion": "How to fix the issue"
        }}
    ],
    "strengths": [
        "List of positive aspects of the code"
    ],
    "requirements_coverage": {{
        "covered": ["List of requirement IDs that are implemented"],
        "missing": ["List of requirement IDs that are not implemented"],
        "coverage_percentage": 0-100
    }},
    "code_quality": {{
        "readability": "GOOD" or "FAIR" or "POOR",
        "maintainability": "GOOD" or "FAIR" or "POOR",
        "security": "GOOD" or "FAIR" or "POOR",
        "performance": "GOOD" or "FAIR" or "POOR"
    }},
    "recommendations": [
        "List of specific recommendations for improvement"
    ]
}}

Focus on:
1. Code correctness and logic
2. Requirements implementation
3. Code quality and best practices
4. Security vulnerabilities
5. Performance considerations
6. Maintainability and readability
"""

        return prompt

    def _parse_ai_validation_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI validation response and extract structured data"""
        try:
            # Try to find JSON in the response
            start_idx = ai_response.find("{")
            end_idx = ai_response.rfind("}")

            if start_idx != -1 and end_idx != -1:
                json_str = ai_response[start_idx : end_idx + 1]
                return json.loads(json_str)
            else:
                # Fallback: create a basic structure
                return {
                    "validation_status": "WARNING",
                    "overall_score": 50,
                    "issues": [
                        {
                            "severity": "MEDIUM",
                            "type": "WARNING",
                            "description": "Could not parse AI response",
                            "line_number": "N/A",
                            "suggestion": "Review AI response manually",
                        }
                    ],
                    "strengths": ["AI validation attempted"],
                    "requirements_coverage": {
                        "covered": [],
                        "missing": [],
                        "coverage_percentage": 0,
                    },
                    "code_quality": {
                        "readability": "UNKNOWN",
                        "maintainability": "UNKNOWN",
                        "security": "UNKNOWN",
                        "performance": "UNKNOWN",
                    },
                    "recommendations": [
                        "Review AI response manually for detailed analysis"
                    ],
                }

        except Exception as e:
            logger.warning(f"Could not parse AI validation response: {e}")
            # Return fallback structure
            return {
                "validation_status": "FAIL",
                "overall_score": 0,
                "issues": [
                    {
                        "severity": "HIGH",
                        "type": "ERROR",
                        "description": f"Failed to parse AI response: {e}",
                        "line_number": "N/A",
                        "suggestion": "Check AI client configuration",
                    }
                ],
                "strengths": [],
                "requirements_coverage": {
                    "covered": [],
                    "missing": [],
                    "coverage_percentage": 0,
                },
                "code_quality": {
                    "readability": "UNKNOWN",
                    "maintainability": "UNKNOWN",
                    "security": "UNKNOWN",
                    "performance": "UNKNOWN",
                },
                "recommendations": ["Fix AI client configuration and retry validation"],
            }

    def validate_all_code(self) -> Dict[str, Any]:
        """Validate all code files against requirements"""
        try:
            logger.info("🚀 Starting comprehensive code validation...")
            print("🚀 Starting comprehensive code validation...")

            # Update status
            self.validation_log["current_status"] = "validating"
            self._save_validation_log()

            # Get code files and requirements
            code_files = self._get_code_files()
            requirements = self._get_requirements()

            if not code_files:
                return {
                    "status": "error",
                    "error": "No code files found to validate",
                    "total_files": 0,
                }

            logger.info(f"📁 Found {len(code_files)} code files to validate")
            print(f"📁 Found {len(code_files)} code files to validate")
            logger.info(f"📋 Found {len(requirements)} requirements to check against")
            print(f"📋 Found {len(requirements)} requirements to check against")

            # Validate each code file
            validation_results = []
            total_score = 0
            passed_files = 0
            failed_files = 0

            for i, code_file in enumerate(code_files):
                logger.info(
                    f"🔍 Validating file {i+1}/{len(code_files)}: {code_file['name']}"
                )
                print(
                    f"🔍 Validating file {i+1}/{len(code_files)}: {code_file['name']}"
                )

                # Validate the file
                validation_result = self._validate_code_file_with_ai(
                    code_file, requirements
                )

                # Create validation record
                validation_record = {
                    "file_name": code_file["name"],
                    "file_path": code_file["relative_path"],
                    "validation_timestamp": str(datetime.datetime.now()),
                    "ai_client_available": self.ai_client is not None,
                    "validation_result": validation_result,
                }

                validation_results.append(validation_record)

                # Update statistics
                if validation_result["status"] == "success":
                    parsed_result = validation_result.get("validation_result", {})
                    status = parsed_result.get("validation_status", "UNKNOWN")
                    score = parsed_result.get("overall_score", 0)

                    if status == "PASS":
                        passed_files += 1
                    elif status == "FAIL":
                        failed_files += 1

                    total_score += score

                    # Log results
                    logger.info(f"✅ {code_file['name']}: {status} (Score: {score})")
                    print(f"✅ {code_file['name']}: {status} (Score: {score})")
                else:
                    failed_files += 1
                    logger.error(f"❌ {code_file['name']}: Validation failed")
                    print(f"❌ {code_file['name']}: Validation failed")

                # Small delay to avoid overwhelming the AI service
                time.sleep(1)

            # Calculate overall statistics
            overall_score = total_score / len(code_files) if code_files else 0
            pass_rate = (passed_files / len(code_files)) * 100 if code_files else 0

            # Create summary
            summary = {
                "total_files": len(code_files),
                "passed_files": passed_files,
                "failed_files": failed_files,
                "pass_rate": pass_rate,
                "overall_score": overall_score,
                "validation_timestamp": str(datetime.datetime.now()),
                "language": self.language,
                "workspace": self.workspace,
            }

            # Update validation log
            self.validation_log["validations"].extend(validation_results)
            self.validation_log["total_validations"] += len(validation_results)
            self.validation_log["passed_validations"] += passed_files
            self.validation_log["failed_validations"] += failed_files
            self.validation_log["current_status"] = "ready"
            self.validation_log["last_validation"] = summary
            self._save_validation_log()

            logger.info("🎉 Code validation completed successfully")
            print("🎉 Code validation completed successfully")

            return {
                "status": "success",
                "summary": summary,
                "validation_results": validation_results,
                "total_files": len(code_files),
            }

        except Exception as e:
            logger.error(f"Error during code validation: {e}")
            print(f"❌ Error during code validation: {e}")

            # Update status
            self.validation_log["current_status"] = "error"
            self._save_validation_log()

            return {"status": "error", "error": str(e), "total_files": 0}

    def get_validation_status(self) -> Dict[str, Any]:
        """Get current validation status"""
        return {
            "current_status": self.validation_log.get("current_status", "unknown"),
            "total_validations": self.validation_log.get("total_validations", 0),
            "passed_validations": self.validation_log.get("passed_validations", 0),
            "failed_validations": self.validation_log.get("failed_validations", 0),
            "last_validation": self.validation_log.get("last_validation", {}),
            "language": self.language,
            "workspace": self.workspace,
            "ai_client_available": self.ai_client is not None,
        }

    def reset_validation_log(self):
        """Reset the validation log"""
        self.validation_log = {
            "created_at": str(datetime.datetime.now()),
            "workspace": self.workspace,
            "language": self.language,
            "validations": [],
            "total_validations": 0,
            "passed_validations": 0,
            "failed_validations": 0,
            "current_status": "ready",
        }
        self._save_validation_log()
        logger.info("🔄 Validation log reset")
        print("🔄 Validation log reset")

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a comprehensive validation summary"""
        try:
            if not self.validation_log.get("last_validation"):
                return {
                    "status": "no_validations",
                    "message": "No validations have been performed yet",
                }

            last_validation = self.validation_log["last_validation"]

            # Analyze recent validations for trends
            recent_validations = self.validation_log.get("validations", [])[
                -10:
            ]  # Last 10

            # Count issues by severity
            high_issues = 0
            medium_issues = 0
            low_issues = 0

            for validation in recent_validations:
                if validation["validation_result"]["status"] == "success":
                    parsed_result = validation["validation_result"].get(
                        "validation_result", {}
                    )
                    for issue in parsed_result.get("issues", []):
                        severity = issue.get("severity", "LOW")
                        if severity == "HIGH":
                            high_issues += 1
                        elif severity == "MEDIUM":
                            medium_issues += 1
                        else:
                            low_issues += 1

            return {
                "status": "success",
                "overall_summary": last_validation,
                "issue_breakdown": {
                    "high_priority": high_issues,
                    "medium_priority": medium_issues,
                    "low_priority": low_issues,
                },
                "recommendations": self._generate_recommendations(
                    high_issues, medium_issues, low_issues
                ),
                "validation_history": {
                    "total_validations": self.validation_log.get(
                        "total_validations", 0
                    ),
                    "success_rate": (
                        self.validation_log.get("passed_validations", 0)
                        / max(self.validation_log.get("total_validations", 1), 1)
                    )
                    * 100,
                },
            }

        except Exception as e:
            logger.error(f"Error getting validation summary: {e}")
            return {"status": "error", "error": str(e)}

    def _generate_recommendations(
        self, high_issues: int, medium_issues: int, low_issues: int
    ) -> List[str]:
        """Generate recommendations based on issue counts"""
        recommendations = []

        if high_issues > 0:
            recommendations.append(
                f"🚨 Address {high_issues} high-priority issues immediately"
            )

        if medium_issues > 0:
            recommendations.append(
                f"⚠️ Review and fix {medium_issues} medium-priority issues"
            )

        if low_issues > 0:
            recommendations.append(
                f"💡 Consider addressing {low_issues} low-priority issues for code quality"
            )

        if high_issues == 0 and medium_issues == 0:
            recommendations.append("🎉 Excellent! No critical issues found")

        if self.validation_log.get("passed_validations", 0) < self.validation_log.get(
            "total_validations", 0
        ):
            recommendations.append(
                "📚 Review failed validations to understand implementation gaps"
            )

        return recommendations


def main():
    """Main function for the script"""
    try:
        print("🚀 Code Validator")
        print("=" * 50)

        # Initialize configuration
        config = Config()
        validator = CodeValidator(config)

        # Show current status
        status = validator.get_validation_status()
        print(f"📊 Current Status: {status['current_status']}")
        print(f"📋 Total Validations: {status['total_validations']}")
        print(f"✅ Passed: {status['passed_validations']}")
        print(f"❌ Failed: {status['failed_validations']}")
        print(f"🔤 Language: {status['language']}")
        print(f"🌐 Workspace: {status['workspace']}")
        print(
            f"🤖 AI Client: {'Available' if status['ai_client_available'] else 'Not Available'}"
        )
        print()

        # Perform validation
        print("🔍 Starting code validation...")
        result = validator.validate_all_code()

        if result["status"] == "success":
            summary = result["summary"]
            print(f"\n🎉 Validation completed successfully!")
            print(f"📁 Total Files: {summary['total_files']}")
            print(f"✅ Passed: {summary['passed_files']}")
            print(f"❌ Failed: {summary['failed_files']}")
            print(f"📊 Pass Rate: {summary['pass_rate']:.1f}%")
            print(f"🎯 Overall Score: {summary['overall_score']:.1f}/100")
        else:
            print(f"❌ Validation failed: {result.get('error', 'Unknown error')}")

        # Show detailed summary
        print("\n📋 Detailed Summary:")
        detailed_summary = validator.get_validation_summary()
        if detailed_summary["status"] == "success":
            issue_breakdown = detailed_summary["issue_breakdown"]
            print(f"🚨 High Priority Issues: {issue_breakdown['high_priority']}")
            print(f"⚠️ Medium Priority Issues: {issue_breakdown['medium_priority']}")
            print(f"💡 Low Priority Issues: {issue_breakdown['low_priority']}")

            print("\n💡 Recommendations:")
            for rec in detailed_summary["recommendations"]:
                print(f"  {rec}")
        else:
            print(
                f"Could not generate detailed summary: {detailed_summary.get('error', 'Unknown error')}"
            )

        return result

    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"❌ Fatal error: {e}")
        return {"status": "fatal_error", "error": str(e)}


if __name__ == "__main__":
    main()
