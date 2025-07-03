import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from config import Config


class TestConfig:
    """Test cases for Config class"""

    def test_config_initialization(self):
        """Test Config can be initialized"""
        config = Config()
        assert config is not None

    def test_config_has_required_attributes(self):
        """Test Config has all required attributes"""
        config = Config()

        # File paths
        assert hasattr(config, "REQUIREMENTS_FILE")
        assert hasattr(config, "METADATA_FILE")
        assert hasattr(config, "CODEBASE_ROOT")
        assert hasattr(config, "STATUS_LOG_FILE")

        # AI Configuration
        assert hasattr(config, "OPENAI_API_KEY")
        assert hasattr(config, "OPENAI_MODEL")
        assert hasattr(config, "REGION")
        assert hasattr(config, "AI_MAX_TOKENS")
        assert hasattr(config, "AI_TEMPERATURE")

        # Validation settings
        assert hasattr(config, "MAX_RETRIES")
        assert hasattr(config, "VALIDATION_TIMEOUT")

        # Code style settings
        assert hasattr(config, "PYTHON_FORMATTER")
        assert hasattr(config, "LINTER")
        assert hasattr(config, "TEST_COMMAND")

        # Extensions and directories
        assert hasattr(config, "SUPPORTED_EXTENSIONS")
        assert hasattr(config, "EXCLUDE_DIRS")

    def test_default_values(self):
        """Test default configuration values"""
        config = Config()

        assert config.REQUIREMENTS_FILE == "data/requirements.csv"
        assert config.METADATA_FILE == "data/metadata.json"
        assert config.CODEBASE_ROOT == "."
        assert config.STATUS_LOG_FILE == "data/status_log.json"
        assert config.OPENAI_MODEL == "gpt-4"
        assert config.REGION == "swedencentral"
        assert config.AI_MAX_TOKENS == 4000
        assert config.AI_TEMPERATURE == 0.1
        assert config.MAX_RETRIES == 3
        assert config.VALIDATION_TIMEOUT == 300
        assert config.PYTHON_FORMATTER == "black"
        assert config.LINTER == "flake8"
        assert config.TEST_COMMAND == "pytest"

    @patch.dict(
        os.environ,
        {
            "REQUIREMENTS_FILE": "custom/requirements.xlsx",
            "OPENAI_MODEL": "gpt-3.5-turbo",
            "MAX_RETRIES": "5",
        },
    )
    def test_environment_variable_override(self):
        """Test that environment variables override defaults"""
        config = Config()

        assert config.REQUIREMENTS_FILE == "custom/requirements.xlsx"
        assert config.OPENAI_MODEL == "gpt-3.5-turbo"
        assert config.MAX_RETRIES == 5

    def test_supported_extensions(self):
        """Test supported file extensions"""
        config = Config()

        expected_extensions = [".py", ".js", ".ts"]
        assert config.SUPPORTED_EXTENSIONS == expected_extensions

    def test_exclude_dirs(self):
        """Test excluded directories"""
        config = Config()

        expected_dirs = [
            "__pycache__",
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "env",
            ".env",
            "dist",
            "build",
        ]
        assert config.EXCLUDE_DIRS == expected_dirs

    def test_validate_config_with_missing_api_key(self):
        """Test configuration validation with missing API key"""
        with patch.object(Config, "OPENAI_API_KEY", ""):
            errors = Config.validate_config()
            assert len(errors) == 1
            assert "OPENAI_API_KEY is required but not set" in errors

    def test_validate_config_creates_directories(self):
        """Test that validate_config creates necessary directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "subdir", "test.json")

            with patch.object(Config, "REQUIREMENTS_FILE", test_file):
                with patch.object(Config, "METADATA_FILE", test_file):
                    with patch.object(Config, "STATUS_LOG_FILE", test_file):
                        errors = Config.validate_config()

                        # Directory should be created
                        assert os.path.exists(os.path.dirname(test_file))

    def test_get_ignored_patterns(self):
        """Test get_ignored_patterns returns correct patterns"""
        patterns = Config.get_ignored_patterns()

        expected_patterns = [
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "__pycache__/*",
            "*.so",
            ".DS_Store",
            "*.log",
            "*.tmp",
            ".git/*",
            "node_modules/*",
            "venv/*",
            ".venv/*",
        ]

        assert patterns == expected_patterns

    def test_type_conversions(self):
        """Test that environment variables are properly converted to correct types"""
        with patch.dict(
            os.environ,
            {
                "AI_MAX_TOKENS": "8000",
                "AI_TEMPERATURE": "0.5",
                "MAX_RETRIES": "10",
                "VALIDATION_TIMEOUT": "600",
                "AZURE_FUNCTION_TIMEOUT": "1200",
            },
        ):
            config = Config()

            assert isinstance(config.AI_MAX_TOKENS, int)
            assert config.AI_MAX_TOKENS == 8000

            assert isinstance(config.AI_TEMPERATURE, float)
            assert config.AI_TEMPERATURE == 0.5

            assert isinstance(config.MAX_RETRIES, int)
            assert config.MAX_RETRIES == 10

            assert isinstance(config.VALIDATION_TIMEOUT, int)
            assert config.VALIDATION_TIMEOUT == 600

            assert isinstance(config.FUNCTION_TIMEOUT, int)
            assert config.FUNCTION_TIMEOUT == 1200


class TestConfigValidation:
    """Test cases for configuration validation"""

    def test_validate_config_success(self):
        """Test successful configuration validation"""
        with patch.object(Config, "OPENAI_API_KEY", "test-key"):
            errors = Config.validate_config()
            # Should have no errors if API key is set and directories can be created
            assert isinstance(errors, list)

    def test_validate_config_creates_missing_directories(self):
        """Test that validation creates missing directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set paths to non-existent directories
            requirements_dir = os.path.join(temp_dir, "data1")
            metadata_dir = os.path.join(temp_dir, "data2")
            status_dir = os.path.join(temp_dir, "data3")

            requirements_file = os.path.join(requirements_dir, "req.csv")
            metadata_file = os.path.join(metadata_dir, "meta.json")
            status_file = os.path.join(status_dir, "status.json")

            with patch.object(Config, "REQUIREMENTS_FILE", requirements_file):
                with patch.object(Config, "METADATA_FILE", metadata_file):
                    with patch.object(Config, "STATUS_LOG_FILE", status_file):
                        with patch.object(Config, "OPENAI_API_KEY", "test-key"):

                            # Directories shouldn't exist initially
                            assert not os.path.exists(requirements_dir)
                            assert not os.path.exists(metadata_dir)
                            assert not os.path.exists(status_dir)

                            # Run validation
                            errors = Config.validate_config()

                            # Directories should be created
                            assert os.path.exists(requirements_dir)
                            assert os.path.exists(metadata_dir)
                            assert os.path.exists(status_dir)

                            # Should have no errors
                            assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__])
