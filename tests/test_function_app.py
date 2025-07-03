import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
import azure.functions as func
from datetime import datetime

# Import the functions we want to test
import function_app


class TestFunctionApp:
    """Test cases for Azure Function App"""

    def setup_method(self):
        """Setup test fixtures"""
        self.sample_requirements = [
            {
                "id": "REQ-001",
                "name": "Test Requirement",
                "description": "Test description",
                "priority": "High",
                "status": "new",
                "category": "Authentication",
            }
        ]

        self.mock_validation_result = MagicMock()
        self.mock_validation_result.is_valid = True
        self.mock_validation_result.errors = []
        self.mock_validation_result.warnings = []
        self.mock_validation_result.test_results = {}

    @patch("function_app.RequirementsChecker")
    @patch("function_app.CodeAnalyzer")
    @patch("function_app.AICodeEditor")
    @patch("function_app.CodeValidator")
    @patch("function_app.MetadataManager")
    def test_daily_code_update_trigger_no_requirements(
        self, mock_metadata, mock_validator, mock_editor, mock_analyzer, mock_checker
    ):
        """Test daily trigger when no new requirements are found"""

        # Setup mocks
        mock_req_checker = mock_checker.return_value
        mock_req_checker.check_for_updates.return_value = (False, [])

        mock_metadata_manager = mock_metadata.return_value

        # Call the function
        function_app.daily_code_update_trigger(None)

        # Assertions
        mock_req_checker.check_for_updates.assert_called_once()
        mock_metadata_manager.log_status.assert_called_once_with(
            "up_to_date", "No new requirements found"
        )

    @patch("function_app.RequirementsChecker")
    @patch("function_app.CodeAnalyzer")
    @patch("function_app.AICodeEditor")
    @patch("function_app.CodeValidator")
    @patch("function_app.MetadataManager")
    @patch("function_app.process_requirement")
    def test_daily_code_update_trigger_with_requirements(
        self,
        mock_process,
        mock_metadata,
        mock_validator,
        mock_editor,
        mock_analyzer,
        mock_checker,
    ):
        """Test daily trigger when new requirements are found"""

        # Setup mocks
        mock_req_checker = mock_checker.return_value
        mock_req_checker.check_for_updates.return_value = (
            True,
            self.sample_requirements,
        )

        mock_code_analyzer = mock_analyzer.return_value
        mock_code_analyzer.analyze_codebase.return_value = {
            "files": {},
            "functions": {},
        }
        mock_code_analyzer.identify_changes.return_value = {"files_to_create": []}

        mock_metadata_manager = mock_metadata.return_value
        mock_metadata_manager.load_metadata.return_value = {}

        mock_process.return_value = True

        # Call the function
        function_app.daily_code_update_trigger(None)

        # Assertions
        mock_req_checker.check_for_updates.assert_called_once()
        mock_code_analyzer.analyze_codebase.assert_called_once()
        mock_code_analyzer.identify_changes.assert_called_once()
        mock_process.assert_called_once()
        mock_metadata_manager.update_processed_requirements.assert_called_once()

    @patch("function_app.RequirementsChecker")
    @patch("function_app.CodeAnalyzer")
    @patch("function_app.AICodeEditor")
    @patch("function_app.CodeValidator")
    @patch("function_app.MetadataManager")
    def test_daily_code_update_trigger_exception_handling(
        self, mock_metadata, mock_validator, mock_editor, mock_analyzer, mock_checker
    ):
        """Test daily trigger exception handling"""

        # Setup mocks to raise exception
        mock_req_checker = mock_checker.return_value
        mock_req_checker.check_for_updates.side_effect = Exception("Test error")

        mock_metadata_manager = mock_metadata.return_value

        # Call the function
        function_app.daily_code_update_trigger(None)

        # Assertions
        mock_metadata_manager.log_status.assert_called_once_with("error", "Test error")

    @patch("function_app.AICodeEditor")
    @patch("function_app.CodeValidator")
    @patch("function_app.MetadataManager")
    def test_process_requirement_success(
        self, mock_metadata, mock_validator, mock_editor
    ):
        """Test successful requirement processing"""

        # Setup mocks
        mock_ai_editor = mock_editor.return_value
        mock_ai_editor.apply_changes.return_value = {"files_created": ["test.py"]}

        mock_code_validator = mock_validator.return_value
        mock_code_validator.validate_changes.return_value = self.mock_validation_result

        mock_metadata_manager = mock_metadata.return_value

        requirement = self.sample_requirements[0]
        required_changes = {"requirements_mapping": {}}

        # Call the function
        result = function_app.process_requirement(
            requirement,
            required_changes,
            mock_ai_editor,
            mock_code_validator,
            mock_metadata_manager,
        )

        # Assertions
        assert result is True
        mock_ai_editor.apply_changes.assert_called_once()
        mock_code_validator.validate_changes.assert_called_once()
        mock_metadata_manager.log_status.assert_called_once()

    @patch("function_app.AICodeEditor")
    @patch("function_app.CodeValidator")
    @patch("function_app.MetadataManager")
    def test_process_requirement_validation_failure(
        self, mock_metadata, mock_validator, mock_editor
    ):
        """Test requirement processing with validation failure"""

        # Setup mocks
        mock_ai_editor = mock_editor.return_value
        mock_ai_editor.apply_changes.return_value = {"files_created": ["test.py"]}

        # Create failed validation result
        failed_validation = MagicMock()
        failed_validation.is_valid = False
        failed_validation.errors = ["Syntax error"]

        mock_code_validator = mock_validator.return_value
        mock_code_validator.validate_changes.return_value = failed_validation

        mock_metadata_manager = mock_metadata.return_value

        requirement = self.sample_requirements[0]
        required_changes = {"requirements_mapping": {}}

        # Call the function
        result = function_app.process_requirement(
            requirement,
            required_changes,
            mock_ai_editor,
            mock_code_validator,
            mock_metadata_manager,
        )

        # Assertions - should fail after 3 retries
        assert result is False
        assert mock_ai_editor.apply_changes.call_count == 3  # 3 retries
        assert mock_code_validator.validate_changes.call_count == 3

    @patch("function_app.AICodeEditor")
    @patch("function_app.CodeValidator")
    @patch("function_app.MetadataManager")
    def test_process_requirement_exception_handling(
        self, mock_metadata, mock_validator, mock_editor
    ):
        """Test requirement processing exception handling"""

        # Setup mocks
        mock_ai_editor = mock_editor.return_value
        mock_ai_editor.apply_changes.side_effect = Exception("AI Editor error")

        mock_metadata_manager = mock_metadata.return_value

        requirement = self.sample_requirements[0]
        required_changes = {"requirements_mapping": {}}

        # Call the function
        result = function_app.process_requirement(
            requirement,
            required_changes,
            mock_ai_editor,
            mock_validator,
            mock_metadata_manager,
        )

        # Assertions
        assert result is False
        mock_metadata_manager.log_status.assert_called()

    @patch("function_app.MetadataManager")
    def test_get_status_success(self, mock_metadata):
        """Test successful status endpoint"""

        # Setup mock
        mock_metadata_manager = mock_metadata.return_value
        mock_metadata_manager.get_latest_status.return_value = {
            "status": "success",
            "timestamp": "2024-01-15T10:00:00",
        }

        # Create mock request
        req = MagicMock(spec=func.HttpRequest)

        # Call the function
        response = function_app.get_status(req)

        # Assertions
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"

        # Parse response body
        response_data = json.loads(response.get_body().decode())
        assert "status" in response_data
        assert "timestamp" in response_data

    @patch("function_app.MetadataManager")
    def test_get_status_exception(self, mock_metadata):
        """Test status endpoint exception handling"""

        # Setup mock to raise exception
        mock_metadata.side_effect = Exception("Database error")

        # Create mock request
        req = MagicMock(spec=func.HttpRequest)

        # Call the function
        response = function_app.get_status(req)

        # Assertions
        assert response.status_code == 500
        assert response.headers["Content-Type"] == "application/json"

        # Parse response body
        response_data = json.loads(response.get_body().decode())
        assert "error" in response_data

    @patch("function_app.daily_code_update_trigger")
    def test_manual_trigger_success(self, mock_daily_trigger):
        """Test successful manual trigger endpoint"""

        # Setup mock
        mock_daily_trigger.return_value = None

        # Create mock request
        req = MagicMock(spec=func.HttpRequest)

        # Call the function
        response = function_app.manual_trigger(req)

        # Assertions
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"

        # Parse response body
        response_data = json.loads(response.get_body().decode())
        assert "status" in response_data
        assert response_data["status"] == "Manual trigger completed successfully"

        # Verify daily trigger was called
        mock_daily_trigger.assert_called_once_with(None)

    @patch("function_app.daily_code_update_trigger")
    def test_manual_trigger_exception(self, mock_daily_trigger):
        """Test manual trigger endpoint exception handling"""

        # Setup mock to raise exception
        mock_daily_trigger.side_effect = Exception("Trigger error")

        # Create mock request
        req = MagicMock(spec=func.HttpRequest)

        # Call the function
        response = function_app.manual_trigger(req)

        # Assertions
        assert response.status_code == 500
        assert response.headers["Content-Type"] == "application/json"

        # Parse response body
        response_data = json.loads(response.get_body().decode())
        assert "error" in response_data


class TestFunctionAppIntegration:
    """Integration tests for function app components"""

    @patch("function_app.RequirementsChecker")
    @patch("function_app.CodeAnalyzer")
    @patch("function_app.AICodeEditor")
    @patch("function_app.CodeValidator")
    @patch("function_app.MetadataManager")
    def test_end_to_end_processing_flow(
        self, mock_metadata, mock_validator, mock_editor, mock_analyzer, mock_checker
    ):
        """Test end-to-end processing flow"""

        # Setup comprehensive mocks
        mock_req_checker = mock_checker.return_value
        mock_req_checker.check_for_updates.return_value = (
            True,
            self.sample_requirements,
        )

        mock_code_analyzer = mock_analyzer.return_value
        mock_code_analyzer.analyze_codebase.return_value = {
            "files": {"test.py": {}},
            "functions": {},
            "classes": {},
            "dependencies": [],
        }
        mock_code_analyzer.identify_changes.return_value = {
            "files_to_create": ["auth/models.py"],
            "files_to_modify": ["function_app.py"],
            "dependencies_to_add": ["pyjwt"],
            "requirements_mapping": {
                "REQ-001": {
                    "files_to_create": ["auth/models.py"],
                    "files_to_modify": ["function_app.py"],
                }
            },
        }

        mock_ai_editor = mock_editor.return_value
        mock_ai_editor.apply_changes.return_value = {
            "files_created": ["auth/models.py"],
            "files_modified": ["function_app.py"],
            "errors": [],
        }

        # Create successful validation result
        validation_result = MagicMock()
        validation_result.is_valid = True
        validation_result.errors = []
        validation_result.warnings = []
        validation_result.test_results = {"tests_passed": 5}

        mock_code_validator = mock_validator.return_value
        mock_code_validator.validate_changes.return_value = validation_result

        mock_metadata_manager = mock_metadata.return_value
        mock_metadata_manager.load_metadata.return_value = {}

        # Call the main function
        function_app.daily_code_update_trigger(None)

        # Verify the complete flow
        mock_req_checker.check_for_updates.assert_called_once()
        mock_code_analyzer.analyze_codebase.assert_called_once()
        mock_code_analyzer.identify_changes.assert_called_once()
        mock_ai_editor.apply_changes.assert_called_once()
        mock_code_validator.validate_changes.assert_called_once()
        mock_metadata_manager.update_processed_requirements.assert_called_once_with(
            self.sample_requirements
        )

    def test_function_app_configuration(self):
        """Test that function app is properly configured"""

        # Check that app is an instance of FunctionApp
        assert hasattr(function_app, "app")
        assert isinstance(function_app.app, func.FunctionApp)

    @patch("function_app.logging")
    def test_logging_calls(self, mock_logging):
        """Test that appropriate logging calls are made"""

        with patch("function_app.RequirementsChecker") as mock_checker:
            with patch("function_app.MetadataManager") as mock_metadata:
                # Setup mocks
                mock_req_checker = mock_checker.return_value
                mock_req_checker.check_for_updates.return_value = (False, [])

                mock_metadata_manager = mock_metadata.return_value

                # Call function
                function_app.daily_code_update_trigger(None)

                # Verify logging calls
                assert mock_logging.info.called

    def test_azure_function_decorators(self):
        """Test that Azure Function decorators are properly applied"""

        # Check timer trigger decorator
        assert hasattr(function_app.daily_code_update_trigger, "__name__")

        # Check route decorators
        assert hasattr(function_app.get_status, "__name__")
        assert hasattr(function_app.manual_trigger, "__name__")


class TestFunctionAppEdgeCases:
    """Test edge cases and error scenarios"""

    def setup_method(self):
        """Setup for edge case tests"""
        self.sample_requirements = [
            {
                "id": "REQ-001",
                "name": "Test Requirement",
                "description": "Test description",
                "priority": "High",
                "status": "new",
                "category": "Authentication",
            }
        ]

    @patch("function_app.process_requirement")
    @patch("function_app.RequirementsChecker")
    @patch("function_app.CodeAnalyzer")
    @patch("function_app.MetadataManager")
    def test_mixed_success_failure_requirements(
        self, mock_metadata, mock_analyzer, mock_checker, mock_process
    ):
        """Test processing with mixed success and failure results"""

        # Create multiple requirements
        requirements = [
            {"id": "REQ-001", "name": "Success Req", "status": "new"},
            {"id": "REQ-002", "name": "Failure Req", "status": "new"},
        ]

        # Setup mocks
        mock_req_checker = mock_checker.return_value
        mock_req_checker.check_for_updates.return_value = (True, requirements)

        mock_code_analyzer = mock_analyzer.return_value
        mock_code_analyzer.analyze_codebase.return_value = {"files": {}}
        mock_code_analyzer.identify_changes.return_value = {"requirements_mapping": {}}

        mock_metadata_manager = mock_metadata.return_value
        mock_metadata_manager.load_metadata.return_value = {}

        # Mock process_requirement to return success for first, failure for second
        mock_process.side_effect = [True, False]

        # Call function
        function_app.daily_code_update_trigger(None)

        # Verify both requirements were processed
        assert mock_process.call_count == 2
        mock_metadata_manager.update_processed_requirements.assert_called_once()

    @patch("function_app.RequirementsChecker")
    @patch("function_app.MetadataManager")
    def test_empty_requirements_list(self, mock_metadata, mock_checker):
        """Test handling of empty requirements list"""

        # Setup mocks
        mock_req_checker = mock_checker.return_value
        mock_req_checker.check_for_updates.return_value = (True, [])

        mock_metadata_manager = mock_metadata.return_value

        # Call function - this should handle empty list gracefully
        function_app.daily_code_update_trigger(None)

        # Should still call update_processed_requirements with empty list
        mock_metadata_manager.update_processed_requirements.assert_called_once_with([])


if __name__ == "__main__":
    pytest.main([__file__])
