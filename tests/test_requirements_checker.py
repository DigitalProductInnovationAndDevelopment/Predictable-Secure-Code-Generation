import pytest
import pandas as pd
import json
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from CodeFromRequirements.requirements_checker import RequirementsChecker


class TestRequirementsChecker:
    """Test cases for RequirementsChecker class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.requirements_file = os.path.join(self.temp_dir, "requirements.csv")
        self.metadata_file = os.path.join(self.temp_dir, "metadata.json")

        # Create sample requirements data
        self.sample_requirements = [
            {
                "id": "REQ-001",
                "name": "Test Requirement 1",
                "description": "Test description 1",
                "priority": "High",
                "status": "new",
                "category": "Authentication",
                "estimated_hours": 8,
                "created_date": "2024-01-15",
            },
            {
                "id": "REQ-002",
                "name": "Test Requirement 2",
                "description": "Test description 2",
                "priority": "Medium",
                "status": "new",
                "category": "Database",
                "estimated_hours": 4,
                "created_date": "2024-01-16",
            },
        ]

    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("CodeFromRequirements.requirements_checker.Config")
    def test_initialization(self, mock_config):
        """Test RequirementsChecker initialization"""
        mock_config.return_value.REQUIREMENTS_FILE = self.requirements_file
        mock_config.return_value.METADATA_FILE = self.metadata_file

        checker = RequirementsChecker()
        assert checker.requirements_file == self.requirements_file
        assert checker.metadata_file == self.metadata_file

    @patch("CodeFromRequirements.requirements_checker.Config")
    def test_check_for_updates_no_file(self, mock_config):
        """Test check_for_updates with no requirements file"""
        mock_config.return_value.REQUIREMENTS_FILE = "non_existent_file.csv"
        mock_config.return_value.METADATA_FILE = self.metadata_file

        checker = RequirementsChecker()
        has_updates, requirements = checker.check_for_updates()

        assert has_updates is False
        assert requirements == []

    @patch("CodeFromRequirements.requirements_checker.Config")
    def test_load_requirements_file_csv(self, mock_config):
        """Test loading requirements from CSV file"""
        mock_config.return_value.REQUIREMENTS_FILE = self.requirements_file
        mock_config.return_value.METADATA_FILE = self.metadata_file

        # Create CSV file
        df = pd.DataFrame(self.sample_requirements)
        df.to_csv(self.requirements_file, index=False)

        checker = RequirementsChecker()
        requirements = checker._load_requirements_file()

        assert len(requirements) == 2
        assert requirements[0]["id"] == "REQ-001"
        assert requirements[1]["id"] == "REQ-002"

    @patch("CodeFromRequirements.requirements_checker.Config")
    def test_load_requirements_file_excel(self, mock_config):
        """Test loading requirements from Excel file"""
        excel_file = os.path.join(self.temp_dir, "requirements.xlsx")
        mock_config.return_value.REQUIREMENTS_FILE = excel_file
        mock_config.return_value.METADATA_FILE = self.metadata_file

        # Create Excel file
        df = pd.DataFrame(self.sample_requirements)
        df.to_excel(excel_file, index=False)

        checker = RequirementsChecker()
        requirements = checker._load_requirements_file()

        assert len(requirements) == 2
        assert requirements[0]["id"] == "REQ-001"

    @patch("CodeFromRequirements.requirements_checker.Config")
    def test_load_requirements_file_unsupported_format(self, mock_config):
        """Test loading requirements from unsupported file format"""
        txt_file = os.path.join(self.temp_dir, "requirements.txt")
        mock_config.return_value.REQUIREMENTS_FILE = txt_file
        mock_config.return_value.METADATA_FILE = self.metadata_file

        # Create text file
        with open(txt_file, "w") as f:
            f.write("Some text content")

        checker = RequirementsChecker()
        requirements = checker._load_requirements_file()

        assert requirements == []

    @patch("CodeFromRequirements.requirements_checker.Config")
    def test_filter_by_status(self, mock_config):
        """Test filtering requirements by status"""
        mock_config.return_value.REQUIREMENTS_FILE = self.requirements_file
        mock_config.return_value.METADATA_FILE = self.metadata_file

        # Create requirements with different statuses
        mixed_requirements = self.sample_requirements.copy()
        mixed_requirements.append(
            {
                "id": "REQ-003",
                "name": "Completed Requirement",
                "description": "Already done",
                "priority": "Low",
                "status": "completed",
                "category": "API",
            }
        )

        df = pd.DataFrame(mixed_requirements)
        df.to_csv(self.requirements_file, index=False)

        checker = RequirementsChecker()
        requirements = checker._load_requirements_file()

        # Should only return 'new' status requirements
        assert len(requirements) == 2
        for req in requirements:
            assert req["status"] in ["new", "pending", "active"]

    @patch("CodeFromRequirements.requirements_checker.Config")
    def test_calculate_requirements_hash(self, mock_config):
        """Test requirements hash calculation"""
        mock_config.return_value.REQUIREMENTS_FILE = self.requirements_file
        mock_config.return_value.METADATA_FILE = self.metadata_file

        checker = RequirementsChecker()

        # Test with same data should produce same hash
        hash1 = checker._calculate_requirements_hash(self.sample_requirements)
        hash2 = checker._calculate_requirements_hash(self.sample_requirements)
        assert hash1 == hash2

        # Test with different data should produce different hash
        modified_requirements = self.sample_requirements.copy()
        modified_requirements[0]["name"] = "Modified Name"
        hash3 = checker._calculate_requirements_hash(modified_requirements)
        assert hash1 != hash3

    @patch("CodeFromRequirements.requirements_checker.Config")
    def test_identify_new_requirements(self, mock_config):
        """Test identification of new requirements"""
        mock_config.return_value.REQUIREMENTS_FILE = self.requirements_file
        mock_config.return_value.METADATA_FILE = self.metadata_file

        checker = RequirementsChecker()

        # Test with no previous requirements
        new_reqs = checker._identify_new_requirements(self.sample_requirements, [])
        assert len(new_reqs) == 2

        # Test with some previous requirements
        previous = [self.sample_requirements[0]]  # Only first requirement processed
        new_reqs = checker._identify_new_requirements(
            self.sample_requirements, previous
        )
        assert len(new_reqs) == 1
        assert new_reqs[0]["id"] == "REQ-002"

    @patch("CodeFromRequirements.requirements_checker.Config")
    def test_check_for_updates_no_changes(self, mock_config):
        """Test check_for_updates when file hasn't changed"""
        mock_config.return_value.REQUIREMENTS_FILE = self.requirements_file
        mock_config.return_value.METADATA_FILE = self.metadata_file

        # Create requirements file
        df = pd.DataFrame(self.sample_requirements)
        df.to_csv(self.requirements_file, index=False)

        # Create metadata file with same hash
        checker = RequirementsChecker()
        current_hash = checker._calculate_requirements_hash(self.sample_requirements)
        metadata = {
            "last_processed_requirements": {
                "hash": current_hash,
                "requirements": self.sample_requirements,
            }
        }

        with open(self.metadata_file, "w") as f:
            json.dump(metadata, f)

        has_updates, requirements = checker.check_for_updates()

        assert has_updates is False
        assert requirements == []

    @patch("CodeFromRequirements.requirements_checker.Config")
    def test_check_for_updates_with_changes(self, mock_config):
        """Test check_for_updates when file has changed"""
        mock_config.return_value.REQUIREMENTS_FILE = self.requirements_file
        mock_config.return_value.METADATA_FILE = self.metadata_file

        # Create requirements file
        df = pd.DataFrame(self.sample_requirements)
        df.to_csv(self.requirements_file, index=False)

        # Create metadata file with different hash (simulating previous state)
        metadata = {
            "last_processed_requirements": {
                "hash": "different_hash",
                "requirements": [
                    self.sample_requirements[0]
                ],  # Only first req processed
            }
        }

        with open(self.metadata_file, "w") as f:
            json.dump(metadata, f)

        checker = RequirementsChecker()
        has_updates, requirements = checker.check_for_updates()

        assert has_updates is True
        assert len(requirements) == 1  # Only REQ-002 is new
        assert requirements[0]["id"] == "REQ-002"

    @patch("CodeFromRequirements.requirements_checker.Config")
    def test_mark_requirements_processed(self, mock_config):
        """Test marking requirements as processed"""
        mock_config.return_value.REQUIREMENTS_FILE = self.requirements_file
        mock_config.return_value.METADATA_FILE = self.metadata_file

        # Create requirements file
        df = pd.DataFrame(self.sample_requirements)
        df.to_csv(self.requirements_file, index=False)

        checker = RequirementsChecker()
        checker.mark_requirements_processed(self.sample_requirements)

        # Check that metadata file was created
        assert os.path.exists(self.metadata_file)

        # Check metadata content
        with open(self.metadata_file, "r") as f:
            metadata = json.load(f)

        assert "last_processed_requirements" in metadata
        assert "hash" in metadata["last_processed_requirements"]
        assert "processed_at" in metadata["last_processed_requirements"]
        assert len(metadata["last_processed_requirements"]["newly_processed"]) == 2

    @patch("CodeFromRequirements.requirements_checker.Config")
    def test_create_sample_requirements_file(self, mock_config):
        """Test creating sample requirements file"""
        mock_config.return_value.REQUIREMENTS_FILE = self.requirements_file
        mock_config.return_value.METADATA_FILE = self.metadata_file

        checker = RequirementsChecker()
        checker.create_sample_requirements_file()

        # Check that file was created
        assert os.path.exists(self.requirements_file)

        # Check file content
        df = pd.read_csv(self.requirements_file)
        assert len(df) >= 3  # Should have at least 3 sample requirements
        assert "id" in df.columns
        assert "name" in df.columns
        assert "description" in df.columns

    @patch("CodeFromRequirements.requirements_checker.Config")
    def test_load_last_processed_requirements_no_file(self, mock_config):
        """Test loading last processed requirements when metadata file doesn't exist"""
        mock_config.return_value.REQUIREMENTS_FILE = self.requirements_file
        mock_config.return_value.METADATA_FILE = "non_existent_metadata.json"

        checker = RequirementsChecker()
        result = checker._load_last_processed_requirements()

        assert result == {}

    @patch("CodeFromRequirements.requirements_checker.Config")
    def test_check_for_updates_exception_handling(self, mock_config):
        """Test exception handling in check_for_updates"""
        mock_config.return_value.REQUIREMENTS_FILE = self.requirements_file
        mock_config.return_value.METADATA_FILE = self.metadata_file

        checker = RequirementsChecker()

        # Mock _load_requirements_file to raise an exception
        with patch.object(
            checker, "_load_requirements_file", side_effect=Exception("Test error")
        ):
            has_updates, requirements = checker.check_for_updates()

            assert has_updates is False
            assert requirements == []


class TestRequirementsCheckerValidation:
    """Test cases for requirements validation"""

    @patch("CodeFromRequirements.requirements_checker.Config")
    def test_missing_required_columns(self, mock_config):
        """Test handling of missing required columns"""
        temp_dir = tempfile.mkdtemp()
        requirements_file = os.path.join(temp_dir, "requirements.csv")

        mock_config.return_value.REQUIREMENTS_FILE = requirements_file
        mock_config.return_value.METADATA_FILE = os.path.join(temp_dir, "metadata.json")

        # Create CSV with missing columns
        incomplete_data = [
            {"id": "REQ-001", "name": "Test"}
        ]  # Missing required columns
        df = pd.DataFrame(incomplete_data)
        df.to_csv(requirements_file, index=False)

        checker = RequirementsChecker()

        with patch("logging.warning") as mock_warning:
            requirements = checker._load_requirements_file()

            # Should log warnings for missing columns
            assert mock_warning.called

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__])
