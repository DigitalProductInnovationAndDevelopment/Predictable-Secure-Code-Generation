import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock, mock_open
from CodeFromRequirements.ai_code_editor import AICodeEditor


class TestAICodeEditor:
    """Test cases for AICodeEditor class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

        self.sample_requirement = {
            "id": "REQ-001",
            "name": "Add User Authentication",
            "description": "Implement JWT-based user authentication system",
            "priority": "High",
            "status": "new",
            "category": "Authentication",
        }

        self.sample_changes = {
            "files_to_create": ["auth/models.py", "auth/services.py"],
            "files_to_modify": ["function_app.py"],
            "dependencies_to_add": ["pyjwt", "bcrypt"],
            "requirements_mapping": {
                "REQ-001": {
                    "files_to_create": ["auth/models.py"],
                    "files_to_modify": ["function_app.py"],
                    "functions_to_add": ["authenticate_user"],
                    "classes_to_add": ["User"],
                }
            },
        }

        self.sample_openai_response = {
            "choices": [
                {
                    "message": {
                        "content": """
```python
# auth/models.py
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def authenticate(self):
        return True
```

```python
# function_app.py - Add this function
@app.route("auth/login", methods=["POST"])
def login(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Login endpoint")
```
"""
                    }
                }
            ]
        }

    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("CodeFromRequirements.ai_code_editor.Config")
    def test_initialization(self, mock_config):
        """Test AICodeEditor initialization"""
        mock_config.return_value.OPENAI_API_KEY = "test-key"
        mock_config.return_value.OPENAI_MODEL = "gpt-4"
        mock_config.return_value.AI_MAX_TOKENS = 4000
        mock_config.return_value.AI_TEMPERATURE = 0.1
        mock_config.return_value.REGION = "swedencentral"

        editor = AICodeEditor()

        assert editor.api_key == "test-key"
        assert editor.model == "gpt-4"
        assert editor.max_tokens == 4000
        assert editor.temperature == 0.1
        assert editor.region == "swedencentral"

    @patch("CodeFromRequirements.ai_code_editor.Config")
    @patch("CodeFromRequirements.ai_code_editor.AzureOpenAI")
    def test_apply_changes_success(self, mock_openai_class, mock_config):
        """Test successful application of changes"""
        # Setup config mock
        mock_config.return_value.OPENAI_API_KEY = "test-key"
        mock_config.return_value.OPENAI_MODEL = "gpt-4"
        mock_config.return_value.AI_MAX_TOKENS = 4000
        mock_config.return_value.AI_TEMPERATURE = 0.1
        mock_config.return_value.REGION = "swedencentral"
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir

        # Setup OpenAI mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            **self.sample_openai_response
        )

        # Create test file to modify
        test_file = os.path.join(self.temp_dir, "function_app.py")
        with open(test_file, "w") as f:
            f.write("# Existing function app code\n")

        editor = AICodeEditor()
        result = editor.apply_changes(self.sample_requirement, self.sample_changes)

        # Assertions
        assert "files_created" in result
        assert "files_modified" in result
        assert "errors" in result
        assert len(result["errors"]) == 0

        # Verify OpenAI was called
        mock_client.chat.completions.create.assert_called()

    @patch("CodeFromRequirements.ai_code_editor.Config")
    @patch("CodeFromRequirements.ai_code_editor.AzureOpenAI")
    def test_generate_code_for_requirement(self, mock_openai_class, mock_config):
        """Test code generation for a requirement"""
        # Setup mocks
        mock_config.return_value.OPENAI_API_KEY = "test-key"
        mock_config.return_value.OPENAI_MODEL = "gpt-4"
        mock_config.return_value.AI_MAX_TOKENS = 4000
        mock_config.return_value.AI_TEMPERATURE = 0.1
        mock_config.return_value.REGION = "swedencentral"

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            **self.sample_openai_response
        )

        editor = AICodeEditor()

        # Test data
        context = {"existing_files": ["function_app.py"]}
        changes = self.sample_changes["requirements_mapping"]["REQ-001"]

        result = editor._generate_code_for_requirement(
            self.sample_requirement, changes, context
        )

        # Assertions
        assert result is not None
        assert "models.py" in result  # Part of the generated content

        # Verify OpenAI call
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-4"
        assert call_args[1]["max_tokens"] == 4000
        assert call_args[1]["temperature"] == 0.1

    @patch("CodeFromRequirements.ai_code_editor.Config")
    def test_parse_ai_response(self, mock_config):
        """Test parsing AI response into file changes"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir

        editor = AICodeEditor()

        ai_response = """
Here's the implementation:

```python
# auth/models.py
class User:
    def __init__(self, username):
        self.username = username
```

```python
# auth/services.py
def authenticate_user(username, password):
    return True
```

```python
# function_app.py - ADD THIS FUNCTION
@app.route("login", methods=["POST"])
def login():
    return "Login"
```
"""

        result = editor._parse_ai_response(ai_response)

        # Should identify files to create and modify
        assert "auth/models.py" in result["files_to_create"]
        assert "auth/services.py" in result["files_to_create"]
        assert "function_app.py" in result["files_to_modify"]

        # Should have content for each file
        assert len(result["file_contents"]["auth/models.py"]) > 0
        assert "class User" in result["file_contents"]["auth/models.py"]

    @patch("CodeFromRequirements.ai_code_editor.Config")
    def test_create_file(self, mock_config):
        """Test file creation"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir

        editor = AICodeEditor()

        file_path = "auth/models.py"
        content = "class User:\n    pass\n"

        success = editor._create_file(file_path, content)

        # Assertions
        assert success is True

        # Check file was created
        full_path = os.path.join(self.temp_dir, file_path)
        assert os.path.exists(full_path)

        # Check content
        with open(full_path, "r") as f:
            file_content = f.read()
        assert file_content == content

    @patch("CodeFromRequirements.ai_code_editor.Config")
    def test_modify_file(self, mock_config):
        """Test file modification"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir

        # Create original file
        original_file = os.path.join(self.temp_dir, "function_app.py")
        original_content = """
import azure.functions as func

app = func.FunctionApp()

@app.route("hello")
def hello():
    return "Hello"
"""
        with open(original_file, "w") as f:
            f.write(original_content)

        editor = AICodeEditor()

        # New content to add
        new_content = """
@app.route("login", methods=["POST"])
def login():
    return "Login endpoint"
"""

        success = editor._modify_file("function_app.py", new_content)

        # Assertions
        assert success is True

        # Check file was modified
        with open(original_file, "r") as f:
            modified_content = f.read()

        assert "login" in modified_content
        assert (
            original_content.strip() in modified_content
        )  # Original content preserved

    @patch("CodeFromRequirements.ai_code_editor.Config")
    def test_create_backup(self, mock_config):
        """Test backup creation"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir

        # Create original file
        original_file = os.path.join(self.temp_dir, "test.py")
        original_content = "print('Hello, World!')"
        with open(original_file, "w") as f:
            f.write(original_content)

        editor = AICodeEditor()
        backup_path = editor._create_backup("test.py")

        # Assertions
        assert backup_path is not None
        assert os.path.exists(backup_path)
        assert ".backup." in backup_path

        # Check backup content
        with open(backup_path, "r") as f:
            backup_content = f.read()
        assert backup_content == original_content

    @patch("CodeFromRequirements.ai_code_editor.Config")
    def test_build_context_from_codebase(self, mock_config):
        """Test building context from existing codebase"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir

        # Create some test files
        test_files = {
            "function_app.py": "import azure.functions as func\napp = func.FunctionApp()",
            "models.py": "class User:\n    pass",
            "config.py": "API_KEY = 'secret'",
        }

        for filename, content in test_files.items():
            with open(os.path.join(self.temp_dir, filename), "w") as f:
                f.write(content)

        editor = AICodeEditor()
        context = editor._build_context_from_codebase()

        # Assertions
        assert "existing_files" in context
        assert "file_summaries" in context

        # Should include all test files
        assert "function_app.py" in context["existing_files"]
        assert "models.py" in context["existing_files"]
        assert "config.py" in context["existing_files"]

    @patch("CodeFromRequirements.ai_code_editor.Config")
    def test_generate_prompt_for_requirement(self, mock_config):
        """Test prompt generation for requirements"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir

        editor = AICodeEditor()

        context = {
            "existing_files": ["function_app.py"],
            "file_summaries": {"function_app.py": "Azure Functions app"},
        }

        changes = {
            "files_to_create": ["auth/models.py"],
            "files_to_modify": ["function_app.py"],
            "functions_to_add": ["authenticate_user"],
            "classes_to_add": ["User"],
        }

        prompt = editor._generate_prompt_for_requirement(
            self.sample_requirement, changes, context
        )

        # Assertions
        assert "Add User Authentication" in prompt
        assert "auth/models.py" in prompt
        assert "function_app.py" in prompt
        assert "authenticate_user" in prompt
        assert "User" in prompt

    @patch("CodeFromRequirements.ai_code_editor.Config")
    @patch("CodeFromRequirements.ai_code_editor.AzureOpenAI")
    def test_openai_api_error_handling(self, mock_openai_class, mock_config):
        """Test handling of OpenAI API errors"""
        # Setup config mock
        mock_config.return_value.OPENAI_API_KEY = "test-key"
        mock_config.return_value.OPENAI_MODEL = "gpt-4"
        mock_config.return_value.AI_MAX_TOKENS = 4000
        mock_config.return_value.AI_TEMPERATURE = 0.1
        mock_config.return_value.REGION = "swedencentral"
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir

        # Setup OpenAI mock to raise exception
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        editor = AICodeEditor()
        result = editor.apply_changes(self.sample_requirement, self.sample_changes)

        # Should handle error gracefully
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert "API Error" in str(result["errors"])

    @patch("CodeFromRequirements.ai_code_editor.Config")
    def test_file_creation_permission_error(self, mock_config):
        """Test handling of file creation permission errors"""
        mock_config.return_value.CODEBASE_ROOT = (
            "/root"  # Directory with no write permission
        )

        editor = AICodeEditor()
        success = editor._create_file("test.py", "print('test')")

        # Should handle permission error gracefully
        assert success is False

    @patch("CodeFromRequirements.ai_code_editor.Config")
    def test_extract_code_blocks(self, mock_config):
        """Test extraction of code blocks from AI response"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir

        editor = AICodeEditor()

        text_with_code_blocks = """
Here's the implementation:

```python
# auth/models.py
class User:
    def __init__(self, username):
        self.username = username
```

Some explanation text.

```python
# function_app.py
def new_function():
    return "Hello"
```

More text.
"""

        code_blocks = editor._extract_code_blocks(text_with_code_blocks)

        # Should extract both code blocks
        assert len(code_blocks) == 2
        assert "class User" in code_blocks[0]
        assert "def new_function" in code_blocks[1]

    @patch("CodeFromRequirements.ai_code_editor.Config")
    def test_empty_requirement_handling(self, mock_config):
        """Test handling of empty or invalid requirements"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir

        editor = AICodeEditor()

        # Test with empty requirement
        empty_requirement = {}
        empty_changes = {"requirements_mapping": {}}

        result = editor.apply_changes(empty_requirement, empty_changes)

        # Should handle gracefully
        assert "files_created" in result
        assert "files_modified" in result
        assert "errors" in result


class TestAICodeEditorEdgeCases:
    """Test edge cases and error scenarios"""

    @patch("CodeFromRequirements.ai_code_editor.Config")
    def test_malformed_ai_response(self, mock_config):
        """Test handling of malformed AI responses"""
        mock_config.return_value.CODEBASE_ROOT = tempfile.mkdtemp()

        editor = AICodeEditor()

        # Test with malformed response
        malformed_response = "This is not properly formatted code"

        result = editor._parse_ai_response(malformed_response)

        # Should handle gracefully
        assert "files_to_create" in result
        assert "files_to_modify" in result
        assert "file_contents" in result

    @patch("CodeFromRequirements.ai_code_editor.Config")
    def test_very_long_file_paths(self, mock_config):
        """Test handling of very long file paths"""
        temp_dir = tempfile.mkdtemp()
        mock_config.return_value.CODEBASE_ROOT = temp_dir

        editor = AICodeEditor()

        # Create a very long file path
        long_path = "a" * 200 + "/very/long/path/file.py"

        success = editor._create_file(long_path, "print('test')")

        # Should handle long paths appropriately
        # Result depends on filesystem limitations
        assert isinstance(success, bool)

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    @patch("CodeFromRequirements.ai_code_editor.Config")
    def test_unicode_content_handling(self, mock_config):
        """Test handling of Unicode content in files"""
        temp_dir = tempfile.mkdtemp()
        mock_config.return_value.CODEBASE_ROOT = temp_dir

        editor = AICodeEditor()

        # Test with Unicode content
        unicode_content = "# -*- coding: utf-8 -*-\nprint('Hello, 世界!')\n"

        success = editor._create_file("unicode_test.py", unicode_content)

        assert success is True

        # Verify content was written correctly
        file_path = os.path.join(temp_dir, "unicode_test.py")
        with open(file_path, "r", encoding="utf-8") as f:
            read_content = f.read()

        assert read_content == unicode_content

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__])
