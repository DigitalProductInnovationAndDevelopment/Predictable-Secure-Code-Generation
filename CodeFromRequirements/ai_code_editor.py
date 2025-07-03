import os
import json
from typing import Dict, List, Any, Optional
from config import Config
import logging

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI package not available. Install with: pip install openai")


class AICodeEditor:
    """Uses AI to generate and edit code based on requirements"""

    def __init__(self):
        self.config = Config()
        self.setup_openai()

    def setup_openai(self):
        """Initialize OpenAI client"""
        if not OPENAI_AVAILABLE:
            logging.error(
                "OpenAI package not available. Please install with: pip install openai"
            )
            return

        if self.config.OPENAI_API_KEY:
            openai.api_key = self.config.OPENAI_API_KEY
        else:
            logging.warning("OpenAI API key not configured")

    def apply_changes(
        self, requirement: Dict[str, Any], required_changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply changes for a specific requirement using AI

        Returns:
            Dict containing information about changes made
        """
        req_id = requirement.get("id", "")
        req_changes = required_changes.get("requirements_mapping", {}).get(req_id, {})

        changes_made = {
            "requirement_id": req_id,
            "files_created": [],
            "files_modified": [],
            "errors": [],
            "success": False,
        }

        try:
            # Create new files
            for file_path in req_changes.get("files_to_create", []):
                if self._create_file_with_ai(file_path, requirement):
                    changes_made["files_created"].append(file_path)
                else:
                    changes_made["errors"].append(f"Failed to create file: {file_path}")

            # Modify existing files
            for file_path in req_changes.get("files_to_modify", []):
                if self._modify_file_with_ai(file_path, requirement):
                    changes_made["files_modified"].append(file_path)
                else:
                    changes_made["errors"].append(f"Failed to modify file: {file_path}")

            changes_made["success"] = len(changes_made["errors"]) == 0

        except Exception as e:
            logging.error(f"Error applying changes for requirement {req_id}: {str(e)}")
            changes_made["errors"].append(str(e))

        return changes_made

    def _create_file_with_ai(self, file_path: str, requirement: Dict[str, Any]) -> bool:
        """Create a new file using AI based on the requirement"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Generate prompt for file creation
            prompt = self._generate_creation_prompt(file_path, requirement)

            # Get AI response
            ai_response = self._get_ai_response(prompt)

            if ai_response:
                # Extract code from AI response
                code = self._extract_code_from_response(ai_response)

                if code:
                    # Write file
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(code)

                    logging.info(f"Created file: {file_path}")
                    return True
                else:
                    logging.error(
                        f"No valid code extracted from AI response for {file_path}"
                    )

        except Exception as e:
            logging.error(f"Error creating file {file_path}: {str(e)}")

        return False

    def _modify_file_with_ai(self, file_path: str, requirement: Dict[str, Any]) -> bool:
        """Modify an existing file using AI based on the requirement"""
        try:
            if not os.path.exists(file_path):
                logging.warning(f"File {file_path} doesn't exist, cannot modify")
                return False

            # Read current file content
            with open(file_path, "r", encoding="utf-8") as f:
                current_content = f.read()

            # Generate prompt for modification
            prompt = self._generate_modification_prompt(
                file_path, current_content, requirement
            )

            # Get AI response
            ai_response = self._get_ai_response(prompt)

            if ai_response:
                # Extract modified code from AI response
                modified_code = self._extract_code_from_response(ai_response)

                if modified_code and modified_code != current_content:
                    # Create backup
                    backup_path = f"{file_path}.backup"
                    with open(backup_path, "w", encoding="utf-8") as f:
                        f.write(current_content)

                    # Write modified file
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(modified_code)

                    logging.info(f"Modified file: {file_path}")
                    return True
                else:
                    logging.info(f"No changes needed for file: {file_path}")
                    return True

        except Exception as e:
            logging.error(f"Error modifying file {file_path}: {str(e)}")

        return False

    def _generate_creation_prompt(
        self, file_path: str, requirement: Dict[str, Any]
    ) -> str:
        """Generate AI prompt for creating a new file"""
        req_name = requirement.get("name", "")
        req_description = requirement.get("description", "")
        req_category = requirement.get("category", "")

        file_extension = os.path.splitext(file_path)[1]
        file_name = os.path.basename(file_path)

        prompt = f"""
Create a {file_extension} file named '{file_name}' for the following requirement:

**Requirement:** {req_name}
**Category:** {req_category}
**Description:** {req_description}

**File Path:** {file_path}

Please generate complete, production-ready code that:
1. Implements the requirement functionality
2. Follows Python best practices and PEP 8 style guidelines
3. Includes proper error handling
4. Has comprehensive docstrings and comments
5. Includes type hints where appropriate
6. Is compatible with Azure Functions framework
7. Follows security best practices

The code should be immediately runnable and well-structured.
Only respond with the code content, no explanations or markdown formatting.
"""

        return prompt.strip()

    def _generate_modification_prompt(
        self, file_path: str, current_content: str, requirement: Dict[str, Any]
    ) -> str:
        """Generate AI prompt for modifying an existing file"""
        req_name = requirement.get("name", "")
        req_description = requirement.get("description", "")
        req_category = requirement.get("category", "")

        prompt = f"""
Modify the following existing code to implement this requirement:

**Requirement:** {req_name}
**Category:** {req_category}
**Description:** {req_description}

**Current File Content:**
```
{current_content}
```

Please modify the code to:
1. Implement the new requirement functionality
2. Maintain existing functionality
3. Follow Python best practices and PEP 8 style guidelines
4. Include proper error handling
5. Add comprehensive docstrings for new functions/classes
6. Include type hints where appropriate
7. Maintain compatibility with Azure Functions framework

Return the complete modified file content.
Only respond with the code content, no explanations or markdown formatting.
"""

        return prompt.strip()

    def _get_ai_response(self, prompt: str) -> Optional[str]:
        """Get response from AI service"""
        if not OPENAI_AVAILABLE:
            logging.error("OpenAI package not available. Cannot generate AI response.")
            return None

        try:
            if not self.config.OPENAI_API_KEY:
                logging.error("OpenAI API key not configured")
                return None

            response = openai.ChatCompletion.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software engineer who writes clean, efficient, and well-documented code. You always follow best practices and security guidelines.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.config.AI_MAX_TOKENS,
                temperature=self.config.AI_TEMPERATURE,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logging.error(f"Error getting AI response: {str(e)}")
            return None

    def _extract_code_from_response(self, response: str) -> Optional[str]:
        """Extract code from AI response, handling various formats"""
        if not response:
            return None

        # Remove markdown code blocks if present
        if "```" in response:
            # Find code between ```
            parts = response.split("```")
            if len(parts) >= 3:
                # Take the content between first set of ```
                code = parts[1]
                # Remove language identifier if present (e.g., "python")
                lines = code.split("\n")
                if lines and not lines[0].strip().startswith(
                    ("import", "from", "def", "class", "#")
                ):
                    lines = lines[1:]  # Remove language identifier line
                return "\n".join(lines).strip()

        # If no markdown blocks, assume entire response is code
        return response.strip()

    def generate_test_file(self, source_file: str, requirement: Dict[str, Any]) -> bool:
        """Generate a test file for the given source file"""
        try:
            test_file_path = self._get_test_file_path(source_file)

            # Read source file to understand what to test
            if os.path.exists(source_file):
                with open(source_file, "r", encoding="utf-8") as f:
                    source_content = f.read()
            else:
                source_content = ""

            prompt = self._generate_test_creation_prompt(
                source_file, source_content, requirement
            )

            ai_response = self._get_ai_response(prompt)

            if ai_response:
                code = self._extract_code_from_response(ai_response)

                if code:
                    os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
                    with open(test_file_path, "w", encoding="utf-8") as f:
                        f.write(code)

                    logging.info(f"Created test file: {test_file_path}")
                    return True

        except Exception as e:
            logging.error(f"Error generating test file for {source_file}: {str(e)}")

        return False

    def _get_test_file_path(self, source_file: str) -> str:
        """Generate test file path from source file path"""
        dir_name = os.path.dirname(source_file)
        base_name = os.path.basename(source_file)
        name_without_ext = os.path.splitext(base_name)[0]

        # Create test file in tests directory
        test_dir = "tests" if not dir_name or dir_name == "." else f"tests/{dir_name}"
        return f"{test_dir}/test_{name_without_ext}.py"

    def _generate_test_creation_prompt(
        self, source_file: str, source_content: str, requirement: Dict[str, Any]
    ) -> str:
        """Generate prompt for creating test files"""
        req_name = requirement.get("name", "")
        req_description = requirement.get("description", "")

        prompt = f"""
Create comprehensive unit tests for the following source file implementing this requirement:

**Requirement:** {req_name}
**Description:** {req_description}
**Source File:** {source_file}

**Source Code:**
```
{source_content}
```

Please create a complete test file that:
1. Uses pytest framework
2. Tests all public functions and methods
3. Includes edge cases and error conditions
4. Has proper test fixtures and setup/teardown
5. Follows naming conventions (test_function_name)
6. Includes docstrings for test functions
7. Has good test coverage
8. Tests both positive and negative scenarios

Return only the test code content.
"""

        return prompt.strip()
