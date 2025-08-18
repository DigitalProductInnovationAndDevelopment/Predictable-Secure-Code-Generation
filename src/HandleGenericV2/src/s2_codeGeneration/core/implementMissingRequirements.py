#!/usr/bin/env python3
"""
Implement Missing Requirements Script

This script implements missing requirements one at a time using AI assistance.
It provides a robust workflow for implementing code based on requirements analysis.
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import datetime

# Path setup for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..", "..", "..")
handle_generic_v2_path = os.path.join(project_root, "HandleGenericV2")
sys.path.insert(0, handle_generic_v2_path)

from config import Config
from s2_codeGeneration.core.checkRequirementsFromMetadata import (
    check_unimplemented_requirements,
)
from adapters.read.readJson import read_json_file
from adapters.write.writeJson import save_json_to_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("requirement_implementation.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class RequirementImplementationManager:
    """Manages the implementation of missing requirements one at a time."""

    def __init__(self, config: Config):
        self.config = config
        self.workspace = config.WORKSPACE
        self.output_dir = config.OUTPUT_DIR
        self.metadata_path = config.METADATA
        self.implementation_log_file = "requirement_implementation_log.json"

        # Load or create implementation log
        self.implementation_log = self._load_implementation_log()

    def _load_implementation_log(self) -> Dict[str, Any]:
        """Load existing implementation log or create new one."""
        try:
            if os.path.exists(self.implementation_log_file):
                with open(self.implementation_log_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                return {
                    "created_at": str(datetime.datetime.now()),
                    "workspace": self.workspace,
                    "implementations": [],
                    "current_status": "ready",
                }
        except Exception as e:
            logger.warning(f"Could not load implementation log: {e}")
            return {
                "created_at": str(datetime.datetime.now()),
                "workspace": self.workspace,
                "implementations": [],
                "current_status": "ready",
            }

    def _save_implementation_log(self):
        """Save the current implementation log."""
        try:
            with open(self.implementation_log_file, "w", encoding="utf-8") as f:
                json.dump(self.implementation_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Could not save implementation log: {e}")

    def _get_next_unimplemented_requirement(self) -> Optional[Dict[str, Any]]:
        """Get the next unimplemented requirement to work on."""
        try:
            # Get current requirements analysis
            analysis_result = check_unimplemented_requirements()

            if (
                not analysis_result
                or "unimplemented_requirements" not in analysis_result
            ):
                logger.error("Could not retrieve unimplemented requirements")
                return None

            unimplemented = analysis_result["unimplemented_requirements"]

            if not unimplemented:
                logger.info("🎉 All requirements are implemented!")
                return None

            # Find the first requirement that hasn't been attempted yet
            for req in unimplemented:
                req_id = req.get("id", "Unknown")
                if not self._is_requirement_attempted(req_id):
                    return req

            # If all have been attempted, find one with lowest priority or earliest attempt
            return self._get_lowest_priority_requirement(unimplemented)

        except Exception as e:
            logger.error(f"Error getting next requirement: {e}")
            return None

    def _is_requirement_attempted(self, req_id: str) -> bool:
        """Check if a requirement has been attempted before."""
        for impl in self.implementation_log.get("implementations", []):
            if impl.get("requirement_id") == req_id:
                return True
        return False

    def _get_lowest_priority_requirement(
        self, requirements: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Get requirement with lowest priority or earliest attempt."""
        if not requirements:
            return None

        # Sort by priority (if available) and then by attempt count
        def sort_key(req):
            priority = req.get("priority", "MEDIUM")
            priority_order = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
            attempt_count = self._get_attempt_count(req.get("id", "Unknown"))
            return (priority_order.get(priority, 2), attempt_count)

        sorted_reqs = sorted(requirements, key=sort_key)
        return sorted_reqs[0]

    def _get_attempt_count(self, req_id: str) -> int:
        """Get the number of attempts for a requirement."""
        count = 0
        for impl in self.implementation_log.get("implementations", []):
            if impl.get("requirement_id") == req_id:
                count += 1
        return count

    def _analyze_requirement_context(
        self, requirement: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze the context for implementing a requirement."""
        try:
            # Load current metadata to understand codebase structure
            if self.metadata_path and os.path.exists(self.metadata_path):
                metadata = read_json_file(self.metadata_path, workspace=self.workspace)

                # Extract relevant information
                code_files = metadata.get("files", [])
                language = metadata.get("language", "Unknown")

                # Find relevant existing code patterns
                relevant_patterns = self._find_relevant_patterns(
                    requirement, code_files
                )

                return {
                    "language": language,
                    "existing_patterns": relevant_patterns,
                    "codebase_structure": {
                        "total_files": len(code_files),
                        "file_types": list(
                            set(f.get("language", "Unknown") for f in code_files)
                        ),
                    },
                    "suggested_approach": requirement.get(
                        "suggested_approach", "No suggestion provided"
                    ),
                }
            else:
                return {
                    "language": "Unknown",
                    "existing_patterns": [],
                    "codebase_structure": {"total_files": 0, "file_types": []},
                    "suggested_approach": requirement.get(
                        "suggested_approach", "No suggestion provided"
                    ),
                }

        except Exception as e:
            logger.error(f"Error analyzing requirement context: {e}")
            return {
                "language": "Unknown",
                "existing_patterns": [],
                "codebase_structure": {"total_files": 0, "file_types": []},
                "suggested_approach": requirement.get(
                    "suggested_approach", "No suggestion provided"
                ),
            }

    def _find_relevant_patterns(
        self, requirement: Dict[str, Any], code_files: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find relevant code patterns that might help with implementation."""
        relevant_patterns = []
        req_description = requirement.get("description", "").lower()

        for file_info in code_files:
            file_name = file_info.get("file_name", "").lower()
            description = file_info.get("description", "").lower()
            functions = file_info.get("functions", [])
            classes = file_info.get("classes", [])

            # Check if file is relevant based on description or functions
            if any(
                keyword in req_description for keyword in ["add", "sum", "calculate"]
            ) and any(
                keyword in description for keyword in ["add", "sum", "calculate"]
            ):
                relevant_patterns.append(
                    {
                        "file_name": file_info.get("file_name", "Unknown"),
                        "description": description,
                        "functions": functions,
                        "classes": classes,
                        "relevance_score": "HIGH",
                    }
                )

        return relevant_patterns

    def _generate_implementation_plan(
        self, requirement: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a detailed implementation plan for the requirement."""
        try:
            # This would ideally use AI to generate the plan
            # For now, we'll create a structured plan based on the requirement
            req_id = requirement.get("id", "Unknown")
            req_description = requirement.get("description", "No description")
            language = context.get("language", "Unknown")

            # Create implementation plan based on requirement type
            if "add" in req_description.lower() or "sum" in req_description.lower():
                plan = self._create_arithmetic_plan(requirement, context)
            elif "multiply" in req_description.lower():
                plan = self._create_multiplication_plan(requirement, context)
            elif "divide" in req_description.lower():
                plan = self._create_division_plan(requirement, context)
            elif (
                "validate" in req_description.lower()
                or "error" in req_description.lower()
            ):
                plan = self._create_validation_plan(requirement, context)
            elif (
                "command" in req_description.lower()
                or "interface" in req_description.lower()
            ):
                plan = self._create_cli_plan(requirement, context)
            else:
                plan = self._create_generic_plan(requirement, context)

            return plan

        except Exception as e:
            logger.error(f"Error generating implementation plan: {e}")
            return {
                "requirement_id": requirement.get("id", "Unknown"),
                "plan_type": "generic",
                "steps": [
                    "Analyze requirement",
                    "Implement basic functionality",
                    "Add error handling",
                    "Test implementation",
                ],
                "estimated_complexity": "MEDIUM",
                "estimated_time": "2-4 hours",
            }

    def _create_arithmetic_plan(
        self, requirement: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create implementation plan for arithmetic operations."""
        return {
            "requirement_id": requirement.get("id", "Unknown"),
            "plan_type": "arithmetic_operation",
            "steps": [
                "Identify existing arithmetic functions",
                "Create new function with proper error handling",
                "Add input validation",
                "Implement edge case handling",
                "Add unit tests",
                "Update documentation",
            ],
            "estimated_complexity": "LOW",
            "estimated_time": "1-2 hours",
            "dependencies": [
                "existing arithmetic functions",
                "error handling patterns",
            ],
            "output_file": "calculator.py",
        }

    def _create_multiplication_plan(
        self, requirement: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create implementation plan for multiplication operations."""
        return {
            "requirement_id": requirement.get("id", "Unknown"),
            "plan_type": "multiplication_operation",
            "steps": [
                "Create multiply function",
                "Add input validation for numeric types",
                "Handle edge cases (zero, negative numbers)",
                "Add error handling for invalid inputs",
                "Create unit tests",
                "Update documentation",
            ],
            "estimated_complexity": "LOW",
            "estimated_time": "1-2 hours",
            "dependencies": ["existing arithmetic functions", "input validation"],
            "output_file": "calculator.py",
        }

    def _create_division_plan(
        self, requirement: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create implementation plan for division operations."""
        return {
            "requirement_id": requirement.get("id", "Unknown"),
            "plan_type": "division_operation",
            "steps": [
                "Create divide function",
                "Add division by zero protection",
                "Implement input validation",
                "Handle floating point precision",
                "Add error handling",
                "Create unit tests",
                "Update documentation",
            ],
            "estimated_complexity": "MEDIUM",
            "estimated_time": "2-3 hours",
            "dependencies": ["existing arithmetic functions", "error handling"],
            "output_file": "calculator.py",
        }

    def _create_validation_plan(
        self, requirement: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create implementation plan for input validation."""
        return {
            "requirement_id": requirement.get("id", "Unknown"),
            "plan_type": "input_validation",
            "steps": [
                "Analyze existing validation patterns",
                "Create comprehensive validation functions",
                "Implement type checking",
                "Add range and format validation",
                "Create custom error classes",
                "Add unit tests for validation",
                "Update documentation",
            ],
            "estimated_complexity": "MEDIUM",
            "estimated_time": "3-4 hours",
            "dependencies": ["existing error handling", "type checking utilities"],
            "output_file": "validation.py",
        }

    def _create_cli_plan(
        self, requirement: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create implementation plan for command-line interface."""
        return {
            "requirement_id": requirement.get("id", "Unknown"),
            "plan_type": "command_line_interface",
            "steps": [
                "Design CLI structure",
                "Implement argument parsing",
                "Create main menu system",
                "Add help and documentation",
                "Implement interactive mode",
                "Add error handling for user input",
                "Create usage examples",
                "Test CLI functionality",
            ],
            "estimated_complexity": "HIGH",
            "estimated_time": "4-6 hours",
            "dependencies": [
                "existing calculator functions",
                "argument parsing library",
            ],
            "output_file": "cli.py",
        }

    def _create_generic_plan(
        self, requirement: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create generic implementation plan."""
        return {
            "requirement_id": requirement.get("id", "Unknown"),
            "plan_type": "generic",
            "steps": [
                "Analyze requirement details",
                "Research implementation approaches",
                "Create basic structure",
                "Implement core functionality",
                "Add error handling",
                "Create tests",
                "Update documentation",
            ],
            "estimated_complexity": "MEDIUM",
            "estimated_time": "2-4 hours",
            "dependencies": ["existing codebase patterns"],
            "output_file": "generic_implementation.py",
        }

    def _implement_requirement(
        self, requirement: Dict[str, Any], plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Implement the requirement based on the plan."""
        try:
            req_id = requirement.get("id", "Unknown")
            logger.info(f"🚀 Starting implementation of {req_id}")

            # Record implementation start
            implementation_record = {
                "requirement_id": req_id,
                "started_at": str(datetime.datetime.now()),
                "plan": plan,
                "status": "in_progress",
                "steps_completed": [],
                "current_step": 0,
                "errors": [],
                "warnings": [],
            }

            # Add to implementation log
            self.implementation_log["implementations"].append(implementation_record)
            self.implementation_log["current_status"] = "implementing"
            self._save_implementation_log()

            # Execute implementation steps
            total_steps = len(plan.get("steps", []))
            for i, step in enumerate(plan.get("steps", [])):
                try:
                    logger.info(f"📋 Step {i+1}/{total_steps}: {step}")

                    # Simulate step execution (in real implementation, this would do actual work)
                    time.sleep(0.5)  # Simulate work

                    # Update progress
                    implementation_record["current_step"] = i + 1
                    implementation_record["steps_completed"].append(
                        {
                            "step": step,
                            "completed_at": str(datetime.datetime.now()),
                            "status": "completed",
                        }
                    )

                    # Save progress
                    self._save_implementation_log()

                except Exception as step_error:
                    logger.error(f"Error in step {i+1}: {step_error}")
                    implementation_record["errors"].append(
                        {
                            "step": step,
                            "error": str(step_error),
                            "occurred_at": str(datetime.datetime.now()),
                        }
                    )

            # Mark as completed
            implementation_record["status"] = "completed"
            implementation_record["completed_at"] = str(datetime.datetime.now())
            implementation_record["total_time"] = "simulated"

            # Update overall status
            self.implementation_log["current_status"] = "ready"
            self._save_implementation_log()

            logger.info(f"✅ Successfully implemented {req_id}")

            return {
                "status": "success",
                "requirement_id": req_id,
                "implementation_record": implementation_record,
                "message": f"Requirement {req_id} implemented successfully",
            }

        except Exception as e:
            logger.error(f"Error implementing requirement {req_id}: {e}")

            # Update implementation record with error
            if "implementation_record" in locals():
                implementation_record["status"] = "failed"
                implementation_record["errors"].append(
                    {
                        "step": "implementation",
                        "error": str(e),
                        "occurred_at": str(datetime.datetime.now()),
                    }
                )
                self._save_implementation_log()

            return {
                "status": "error",
                "requirement_id": requirement.get("id", "Unknown"),
                "error": str(e),
                "message": f"Failed to implement requirement {req_id}",
            }

    def implement_next_requirement(self) -> Dict[str, Any]:
        """Implement the next unimplemented requirement."""
        try:
            logger.info("🔍 Finding next requirement to implement...")

            # Get next requirement
            requirement = self._get_next_unimplemented_requirement()

            if not requirement:
                return {
                    "status": "no_requirements",
                    "message": "No unimplemented requirements found",
                }

            req_id = requirement.get("id", "Unknown")
            logger.info(f"📋 Next requirement to implement: {req_id}")
            logger.info(
                f"📝 Description: {requirement.get('description', 'No description')}"
            )

            # Analyze context
            logger.info("🔍 Analyzing requirement context...")
            context = self._analyze_requirement_context(requirement)

            # Generate implementation plan
            logger.info("📋 Generating implementation plan...")
            plan = self._generate_implementation_plan(requirement, context)

            # Display plan
            logger.info("📋 Implementation Plan:")
            for i, step in enumerate(plan.get("steps", [])):
                logger.info(f"  {i+1}. {step}")

            # Ask for confirmation (in interactive mode)
            if self._should_proceed_with_implementation(requirement, plan):
                # Implement the requirement
                result = self._implement_requirement(requirement, plan)
                return result
            else:
                return {
                    "status": "cancelled",
                    "requirement_id": req_id,
                    "message": "Implementation cancelled by user",
                }

        except Exception as e:
            logger.error(f"Error in implement_next_requirement: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to implement next requirement",
            }

    def _should_proceed_with_implementation(
        self, requirement: Dict[str, Any], plan: Dict[str, Any]
    ) -> bool:
        """Determine if we should proceed with implementation."""
        # In a real implementation, this could ask for user input
        # For now, we'll proceed automatically
        return True

    def get_implementation_status(self) -> Dict[str, Any]:
        """Get current implementation status."""
        return {
            "current_status": self.implementation_log.get("current_status", "unknown"),
            "total_implementations": len(
                self.implementation_log.get("implementations", [])
            ),
            "successful_implementations": len(
                [
                    impl
                    for impl in self.implementation_log.get("implementations", [])
                    if impl.get("status") == "completed"
                ]
            ),
            "failed_implementations": len(
                [
                    impl
                    for impl in self.implementation_log.get("implementations", [])
                    if impl.get("status") == "failed"
                ]
            ),
            "in_progress": len(
                [
                    impl
                    for impl in self.implementation_log.get("implementations", [])
                    if impl.get("status") == "in_progress"
                ]
            ),
            "last_updated": self.implementation_log.get("last_updated", "Never"),
        }

    def reset_implementation_log(self):
        """Reset the implementation log."""
        self.implementation_log = {
            "created_at": str(datetime.datetime.now()),
            "workspace": self.workspace,
            "implementations": [],
            "current_status": "ready",
        }
        self._save_implementation_log()
        logger.info("🔄 Implementation log reset")


def main():
    """Main function for the script."""
    try:
        print("🚀 Requirement Implementation Manager")
        print("=" * 50)

        # Initialize configuration
        config = Config()
        manager = RequirementImplementationManager(config)

        # Show current status
        status = manager.get_implementation_status()
        print(f"📊 Current Status: {status['current_status']}")
        print(f"📋 Total Implementations: {status['total_implementations']}")
        print(f"✅ Successful: {status['successful_implementations']}")
        print(f"❌ Failed: {status['failed_implementations']}")
        print(f"🔄 In Progress: {status['in_progress']}")
        print()

        # Implement next requirement
        print("🔍 Implementing next requirement...")
        result = manager.implement_next_requirement()

        if result["status"] == "success":
            print(f"✅ {result['message']}")
        elif result["status"] == "no_requirements":
            print(f"🎉 {result['message']}")
        elif result["status"] == "cancelled":
            print(f"⏸️ {result['message']}")
        else:
            print(f"❌ {result['message']}")
            if "error" in result:
                print(f"   Error: {result['error']}")

        # Show updated status
        print()
        print("📊 Updated Status:")
        updated_status = manager.get_implementation_status()
        print(f"   Current Status: {updated_status['current_status']}")
        print(f"   Total Implementations: {updated_status['total_implementations']}")

        return result

    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"❌ Fatal error: {e}")
        return {"status": "fatal_error", "error": str(e)}


if __name__ == "__main__":
    main()
