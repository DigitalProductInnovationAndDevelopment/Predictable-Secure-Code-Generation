import pytest
import os
import tempfile
import ast
from unittest.mock import patch, MagicMock, mock_open
from CodeFromRequirements.code_analyzer import CodeAnalyzer


class TestCodeAnalyzer:
    """Test cases for CodeAnalyzer class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

        # Sample Python code for testing
        self.sample_python_code = '''
import os
import json
from typing import Dict, List

class TestClass:
    """A test class"""
    
    def __init__(self):
        self.value = 42
    
    def test_method(self, param: str) -> bool:
        """Test method with type hints"""
        return True

def test_function(name: str, age: int = 25) -> Dict[str, any]:
    """Test function with default parameters"""
    return {"name": name, "age": age}

if __name__ == "__main__":
    pass
'''

        # Sample JavaScript code for testing
        self.sample_js_code = """
function testFunction(param) {
    return param + 1;
}

class TestClass {
    constructor(value) {
        this.value = value;
    }
}
"""

        # Sample requirements for testing
        self.sample_requirements = [
            {
                "id": "REQ-001",
                "name": "Add User Authentication",
                "description": "Implement JWT-based user authentication system",
                "priority": "High",
                "status": "new",
                "category": "Authentication",
            },
            {
                "id": "REQ-002",
                "name": "Database Migration Tool",
                "description": "Create automated database migration scripts",
                "priority": "Medium",
                "status": "new",
                "category": "Database",
            },
        ]

    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("CodeFromRequirements.code_analyzer.Config")
    def test_initialization(self, mock_config):
        """Test CodeAnalyzer initialization"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.SUPPORTED_EXTENSIONS = [".py", ".js"]
        mock_config.return_value.EXCLUDE_DIRS = ["__pycache__", ".git"]

        analyzer = CodeAnalyzer()
        assert analyzer.codebase_root == self.temp_dir
        assert analyzer.supported_extensions == [".py", ".js"]
        assert analyzer.exclude_dirs == ["__pycache__", ".git"]

    @patch("CodeFromRequirements.code_analyzer.Config")
    def test_should_analyze_file(self, mock_config):
        """Test file analysis filtering"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.SUPPORTED_EXTENSIONS = [".py", ".js"]
        mock_config.return_value.EXCLUDE_DIRS = []
        mock_config.return_value.get_ignored_patterns.return_value = ["*.pyc", "*.log"]

        analyzer = CodeAnalyzer()

        # Should analyze supported extensions
        assert analyzer._should_analyze_file("test.py") is True
        assert analyzer._should_analyze_file("test.js") is True

        # Should not analyze unsupported extensions
        assert analyzer._should_analyze_file("test.txt") is False
        assert analyzer._should_analyze_file("test.cpp") is False

        # Should not analyze ignored patterns
        assert analyzer._should_analyze_file("test.pyc") is False
        assert analyzer._should_analyze_file("debug.log") is False

    @patch("CodeFromRequirements.code_analyzer.Config")
    def test_analyze_python_file(self, mock_config):
        """Test Python file analysis"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.SUPPORTED_EXTENSIONS = [".py"]
        mock_config.return_value.EXCLUDE_DIRS = []

        analyzer = CodeAnalyzer()
        result = analyzer._analyze_python_file(self.sample_python_code)

        # Check functions were detected
        assert "test_function" in result["functions"]
        function_info = result["functions"]["test_function"]
        assert function_info["name"] == "test_function"
        assert "name" in function_info["args"]
        assert "age" in function_info["args"]

        # Check classes were detected
        assert "TestClass" in result["classes"]
        class_info = result["classes"]["TestClass"]
        assert class_info["name"] == "TestClass"
        assert "__init__" in class_info["methods"]
        assert "test_method" in class_info["methods"]

        # Check imports were detected
        assert any("os" in imp for imp in result["imports"])
        assert any("json" in imp for imp in result["imports"])

        # Check dependencies were detected
        assert "os" in result["dependencies"]
        assert "json" in result["dependencies"]
        assert "typing" in result["dependencies"]

    @patch("CodeFromRequirements.code_analyzer.Config")
    def test_analyze_generic_file(self, mock_config):
        """Test generic file analysis"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.SUPPORTED_EXTENSIONS = [".js"]
        mock_config.return_value.EXCLUDE_DIRS = []

        analyzer = CodeAnalyzer()
        result = analyzer._analyze_generic_file(self.sample_js_code)

        # Should detect function patterns
        assert len(result["functions"]) > 0

        # Check that function detection works
        function_found = any(
            "testFunction" in func_info.get("name", "")
            for func_info in result["functions"].values()
        )
        assert function_found

    @patch("CodeFromRequirements.code_analyzer.Config")
    def test_analyze_single_file(self, mock_config):
        """Test analysis of a single file"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.SUPPORTED_EXTENSIONS = [".py"]
        mock_config.return_value.EXCLUDE_DIRS = []

        # Create a test Python file
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write(self.sample_python_code)

        analyzer = CodeAnalyzer()
        result = analyzer._analyze_file(test_file)

        assert result is not None
        assert result["path"] == test_file
        assert result["size"] > 0
        assert result["line_count"] > 0
        assert "functions" in result
        assert "classes" in result
        assert "imports" in result

    @patch("CodeFromRequirements.code_analyzer.Config")
    def test_analyze_codebase(self, mock_config):
        """Test full codebase analysis"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.SUPPORTED_EXTENSIONS = [".py", ".js"]
        mock_config.return_value.EXCLUDE_DIRS = ["__pycache__"]

        # Create test files
        py_file = os.path.join(self.temp_dir, "test.py")
        js_file = os.path.join(self.temp_dir, "test.js")

        with open(py_file, "w") as f:
            f.write(self.sample_python_code)

        with open(js_file, "w") as f:
            f.write(self.sample_js_code)

        # Create excluded directory
        excluded_dir = os.path.join(self.temp_dir, "__pycache__")
        os.makedirs(excluded_dir)
        excluded_file = os.path.join(excluded_dir, "excluded.py")
        with open(excluded_file, "w") as f:
            f.write("# This should be excluded")

        analyzer = CodeAnalyzer()
        result = analyzer.analyze_codebase()

        assert result["file_count"] == 2  # Only py and js files, not excluded
        assert result["total_lines"] > 0
        assert len(result["files"]) == 2
        assert "functions" in result
        assert "classes" in result
        assert "dependencies" in result

    @patch("CodeFromRequirements.code_analyzer.Config")
    def test_identify_changes_auth_requirement(self, mock_config):
        """Test identifying changes for authentication requirement"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.SUPPORTED_EXTENSIONS = [".py"]
        mock_config.return_value.EXCLUDE_DIRS = []

        analyzer = CodeAnalyzer()

        code_structure = {"files": {}, "functions": {}, "classes": {}}
        metadata = {}

        auth_requirement = [self.sample_requirements[0]]  # Authentication requirement

        changes = analyzer.identify_changes(code_structure, metadata, auth_requirement)

        assert "files_to_create" in changes
        assert "files_to_modify" in changes
        assert "dependencies_to_add" in changes

        # Should suggest creating authentication-related files
        created_files = changes["files_to_create"]
        assert any("auth" in file.lower() for file in created_files)

        # Should suggest adding authentication dependencies
        dependencies = changes["dependencies_to_add"]
        assert any(dep in ["pyjwt", "bcrypt"] for dep in dependencies)

    @patch("CodeFromRequirements.code_analyzer.Config")
    def test_identify_changes_database_requirement(self, mock_config):
        """Test identifying changes for database requirement"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.SUPPORTED_EXTENSIONS = [".py"]
        mock_config.return_value.EXCLUDE_DIRS = []

        analyzer = CodeAnalyzer()

        code_structure = {"files": {}, "functions": {}, "classes": {}}
        metadata = {}

        db_requirement = [self.sample_requirements[1]]  # Database requirement

        changes = analyzer.identify_changes(code_structure, metadata, db_requirement)

        # Should suggest creating database-related files
        created_files = changes["files_to_create"]
        assert any(
            "database" in file.lower() or "migration" in file.lower()
            for file in created_files
        )

        # Should suggest adding database dependencies
        dependencies = changes["dependencies_to_add"]
        assert any(dep in ["sqlalchemy", "alembic"] for dep in dependencies)

    @patch("CodeFromRequirements.code_analyzer.Config")
    def test_map_requirement_to_changes(self, mock_config):
        """Test mapping a single requirement to changes"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.SUPPORTED_EXTENSIONS = [".py"]
        mock_config.return_value.EXCLUDE_DIRS = []

        analyzer = CodeAnalyzer()

        code_structure = {"files": {}, "functions": {}, "classes": {}}
        metadata = {}

        # Test API requirement
        api_requirement = {
            "id": "REQ-003",
            "name": "REST API Endpoints",
            "description": "Create REST API endpoints for user management",
            "category": "API",
        }

        changes = analyzer._map_requirement_to_changes(
            api_requirement, code_structure, metadata
        )

        assert "files_to_create" in changes
        assert "files_to_modify" in changes

        # Should suggest modifying function_app.py for API requirements
        modified_files = changes["files_to_modify"]
        assert "function_app.py" in modified_files

        # Should suggest creating API-related files
        created_files = changes["files_to_create"]
        assert any("api" in file.lower() for file in created_files)

    @patch("CodeFromRequirements.code_analyzer.Config")
    def test_get_decorator_name(self, mock_config):
        """Test extracting decorator names from AST nodes"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.SUPPORTED_EXTENSIONS = [".py"]
        mock_config.return_value.EXCLUDE_DIRS = []

        analyzer = CodeAnalyzer()

        # Test with Name node
        name_node = ast.Name(id="property", ctx=ast.Load())
        assert analyzer._get_decorator_name(name_node) == "property"

        # Test with Attribute node
        attr_node = ast.Attribute(
            value=ast.Name(id="app", ctx=ast.Load()), attr="route", ctx=ast.Load()
        )
        assert analyzer._get_decorator_name(attr_node) == "app.route"

    @patch("CodeFromRequirements.code_analyzer.Config")
    def test_get_base_name(self, mock_config):
        """Test extracting base class names from AST nodes"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.SUPPORTED_EXTENSIONS = [".py"]
        mock_config.return_value.EXCLUDE_DIRS = []

        analyzer = CodeAnalyzer()

        # Test with Name node
        name_node = ast.Name(id="BaseClass", ctx=ast.Load())
        assert analyzer._get_base_name(name_node) == "BaseClass"

        # Test with Attribute node
        attr_node = ast.Attribute(
            value=ast.Name(id="module", ctx=ast.Load()),
            attr="BaseClass",
            ctx=ast.Load(),
        )
        assert analyzer._get_base_name(attr_node) == "module.BaseClass"

    @patch("CodeFromRequirements.code_analyzer.Config")
    def test_analyze_file_with_syntax_error(self, mock_config):
        """Test handling of Python files with syntax errors"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.SUPPORTED_EXTENSIONS = [".py"]
        mock_config.return_value.EXCLUDE_DIRS = []

        # Create file with syntax error
        invalid_file = os.path.join(self.temp_dir, "invalid.py")
        with open(invalid_file, "w") as f:
            f.write("def invalid_syntax(\n")  # Missing closing parenthesis

        analyzer = CodeAnalyzer()
        result = analyzer._analyze_file(invalid_file)

        # Should return result even with syntax error
        assert result is not None
        assert result["path"] == invalid_file

    @patch("CodeFromRequirements.code_analyzer.Config")
    def test_analyze_file_not_found(self, mock_config):
        """Test handling of non-existent files"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.SUPPORTED_EXTENSIONS = [".py"]
        mock_config.return_value.EXCLUDE_DIRS = []

        analyzer = CodeAnalyzer()
        result = analyzer._analyze_file("non_existent_file.py")

        # Should return None for non-existent files
        assert result is None

    @patch("CodeFromRequirements.code_analyzer.Config")
    def test_requirements_mapping_structure(self, mock_config):
        """Test that requirements mapping has correct structure"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.SUPPORTED_EXTENSIONS = [".py"]
        mock_config.return_value.EXCLUDE_DIRS = []

        analyzer = CodeAnalyzer()

        code_structure = {"files": {}, "functions": {}, "classes": {}}
        metadata = {}

        changes = analyzer.identify_changes(
            code_structure, metadata, self.sample_requirements
        )

        assert "requirements_mapping" in changes

        # Check that each requirement is mapped
        for req in self.sample_requirements:
            req_id = req["id"]
            assert req_id in changes["requirements_mapping"]

            # Check that each mapping has the expected structure
            mapping = changes["requirements_mapping"][req_id]
            expected_keys = [
                "files_to_modify",
                "files_to_create",
                "dependencies_to_add",
                "functions_to_add",
                "classes_to_add",
                "tests_to_create",
            ]
            for key in expected_keys:
                assert key in mapping


class TestCodeAnalyzerEdgeCases:
    """Test edge cases and error handling"""

    @patch("CodeFromRequirements.code_analyzer.Config")
    def test_empty_requirements_list(self, mock_config):
        """Test handling of empty requirements list"""
        mock_config.return_value.CODEBASE_ROOT = "."
        mock_config.return_value.SUPPORTED_EXTENSIONS = [".py"]
        mock_config.return_value.EXCLUDE_DIRS = []

        analyzer = CodeAnalyzer()

        code_structure = {"files": {}, "functions": {}, "classes": {}}
        metadata = {}

        changes = analyzer.identify_changes(code_structure, metadata, [])

        # Should handle empty requirements gracefully
        assert changes["files_to_create"] == []
        assert changes["files_to_modify"] == []
        assert changes["requirements_mapping"] == {}

    @patch("CodeFromRequirements.code_analyzer.Config")
    def test_analyze_codebase_exception_handling(self, mock_config):
        """Test exception handling in analyze_codebase"""
        mock_config.return_value.CODEBASE_ROOT = "/non_existent_directory"
        mock_config.return_value.SUPPORTED_EXTENSIONS = [".py"]
        mock_config.return_value.EXCLUDE_DIRS = []

        analyzer = CodeAnalyzer()

        # Should handle non-existent directory gracefully
        result = analyzer.analyze_codebase()

        assert result["file_count"] == 0
        assert result["total_lines"] == 0
        assert result["files"] == {}


if __name__ == "__main__":
    pytest.main([__file__])
