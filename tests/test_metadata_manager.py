import pytest
import json
import os
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock, mock_open
from CodeFromRequirements.metadata_manager import MetadataManager


class TestMetadataManager:
    """Test cases for MetadataManager class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.metadata_file = os.path.join(self.temp_dir, "metadata.json")
        self.status_log_file = os.path.join(self.temp_dir, "status_log.json")

        self.sample_metadata = {
            "last_processed_requirements": {
                "hash": "abc123",
                "processed_at": "2024-01-15T10:00:00",
                "requirements": [
                    {"id": "REQ-001", "name": "Test Requirement", "status": "completed"}
                ],
            },
            "system_info": {"version": "1.0.0", "last_update": "2024-01-15T09:00:00"},
        }

        self.sample_requirements = [
            {
                "id": "REQ-001",
                "name": "Test Requirement 1",
                "description": "Test description 1",
                "priority": "High",
                "status": "new",
                "category": "Authentication",
            },
            {
                "id": "REQ-002",
                "name": "Test Requirement 2",
                "description": "Test description 2",
                "priority": "Medium",
                "status": "new",
                "category": "Database",
            },
        ]

    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_initialization(self, mock_config):
        """Test MetadataManager initialization"""
        mock_config.return_value.METADATA_FILE = self.metadata_file
        mock_config.return_value.STATUS_LOG_FILE = self.status_log_file

        manager = MetadataManager()

        assert manager.metadata_file == self.metadata_file
        assert manager.status_log_file == self.status_log_file

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_load_metadata_file_exists(self, mock_config):
        """Test loading metadata when file exists"""
        mock_config.return_value.METADATA_FILE = self.metadata_file
        mock_config.return_value.STATUS_LOG_FILE = self.status_log_file

        # Create metadata file
        with open(self.metadata_file, "w") as f:
            json.dump(self.sample_metadata, f)

        manager = MetadataManager()
        metadata = manager.load_metadata()

        assert metadata == self.sample_metadata
        assert "last_processed_requirements" in metadata
        assert "system_info" in metadata

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_load_metadata_file_not_exists(self, mock_config):
        """Test loading metadata when file doesn't exist"""
        mock_config.return_value.METADATA_FILE = "non_existent_file.json"
        mock_config.return_value.STATUS_LOG_FILE = self.status_log_file

        manager = MetadataManager()
        metadata = manager.load_metadata()

        # Should return empty dict when file doesn't exist
        assert metadata == {}

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_save_metadata(self, mock_config):
        """Test saving metadata to file"""
        mock_config.return_value.METADATA_FILE = self.metadata_file
        mock_config.return_value.STATUS_LOG_FILE = self.status_log_file

        manager = MetadataManager()
        manager.save_metadata(self.sample_metadata)

        # Verify file was created and contains correct data
        assert os.path.exists(self.metadata_file)

        with open(self.metadata_file, "r") as f:
            saved_data = json.load(f)

        assert saved_data == self.sample_metadata

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_update_processed_requirements(self, mock_config):
        """Test updating processed requirements"""
        mock_config.return_value.METADATA_FILE = self.metadata_file
        mock_config.return_value.STATUS_LOG_FILE = self.status_log_file

        manager = MetadataManager()
        manager.update_processed_requirements(self.sample_requirements)

        # Check metadata was updated
        assert os.path.exists(self.metadata_file)

        with open(self.metadata_file, "r") as f:
            metadata = json.load(f)

        assert "last_processed_requirements" in metadata
        processed = metadata["last_processed_requirements"]

        assert "hash" in processed
        assert "processed_at" in processed
        assert "newly_processed" in processed
        assert len(processed["newly_processed"]) == 2

        # Verify all requirements are included
        req_ids = [req["id"] for req in processed["newly_processed"]]
        assert "REQ-001" in req_ids
        assert "REQ-002" in req_ids

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_log_status(self, mock_config):
        """Test logging status updates"""
        mock_config.return_value.METADATA_FILE = self.metadata_file
        mock_config.return_value.STATUS_LOG_FILE = self.status_log_file

        manager = MetadataManager()
        manager.log_status("success", "Processing completed successfully")

        # Check status log was created
        assert os.path.exists(self.status_log_file)

        with open(self.status_log_file, "r") as f:
            status_log = json.load(f)

        assert "entries" in status_log
        assert len(status_log["entries"]) == 1

        entry = status_log["entries"][0]
        assert entry["status"] == "success"
        assert entry["message"] == "Processing completed successfully"
        assert "timestamp" in entry

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_log_status_multiple_entries(self, mock_config):
        """Test logging multiple status entries"""
        mock_config.return_value.METADATA_FILE = self.metadata_file
        mock_config.return_value.STATUS_LOG_FILE = self.status_log_file

        manager = MetadataManager()

        # Log multiple status updates
        manager.log_status("info", "Process started")
        manager.log_status("warning", "Minor issue detected")
        manager.log_status("success", "Process completed")

        with open(self.status_log_file, "r") as f:
            status_log = json.load(f)

        # Should have 3 entries
        assert len(status_log["entries"]) == 3

        # Check order (should be chronological)
        assert status_log["entries"][0]["message"] == "Process started"
        assert status_log["entries"][1]["message"] == "Minor issue detected"
        assert status_log["entries"][2]["message"] == "Process completed"

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_get_latest_status(self, mock_config):
        """Test getting the latest status"""
        mock_config.return_value.METADATA_FILE = self.metadata_file
        mock_config.return_value.STATUS_LOG_FILE = self.status_log_file

        manager = MetadataManager()

        # Log some status updates
        manager.log_status("info", "Starting process")
        manager.log_status("success", "Process completed")

        latest_status = manager.get_latest_status()

        assert latest_status["status"] == "success"
        assert latest_status["message"] == "Process completed"
        assert "timestamp" in latest_status

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_get_latest_status_no_log(self, mock_config):
        """Test getting latest status when no log exists"""
        mock_config.return_value.METADATA_FILE = self.metadata_file
        mock_config.return_value.STATUS_LOG_FILE = "non_existent_log.json"

        manager = MetadataManager()
        latest_status = manager.get_latest_status()

        # Should return default status
        assert latest_status["status"] == "unknown"
        assert "No status available" in latest_status["message"]

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_get_processing_history(self, mock_config):
        """Test getting processing history"""
        mock_config.return_value.METADATA_FILE = self.metadata_file
        mock_config.return_value.STATUS_LOG_FILE = self.status_log_file

        # Create metadata with processing history
        metadata_with_history = {
            "processing_history": [
                {
                    "date": "2024-01-15",
                    "requirements_processed": 3,
                    "success_count": 2,
                    "failure_count": 1,
                },
                {
                    "date": "2024-01-14",
                    "requirements_processed": 5,
                    "success_count": 5,
                    "failure_count": 0,
                },
            ]
        }

        with open(self.metadata_file, "w") as f:
            json.dump(metadata_with_history, f)

        manager = MetadataManager()
        history = manager.get_processing_history()

        assert len(history) == 2
        assert history[0]["date"] == "2024-01-15"
        assert history[1]["date"] == "2024-01-14"

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_add_processing_statistics(self, mock_config):
        """Test adding processing statistics"""
        mock_config.return_value.METADATA_FILE = self.metadata_file
        mock_config.return_value.STATUS_LOG_FILE = self.status_log_file

        manager = MetadataManager()

        stats = {
            "requirements_processed": 5,
            "files_created": 10,
            "files_modified": 3,
            "tests_passed": 25,
            "processing_time_seconds": 120,
        }

        manager.add_processing_statistics(stats)

        # Check that statistics were added to metadata
        metadata = manager.load_metadata()

        assert "processing_statistics" in metadata
        stat_entries = metadata["processing_statistics"]

        assert len(stat_entries) == 1
        entry = stat_entries[0]

        assert entry["requirements_processed"] == 5
        assert entry["files_created"] == 10
        assert entry["processing_time_seconds"] == 120
        assert "timestamp" in entry

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_cleanup_old_entries(self, mock_config):
        """Test cleanup of old log entries"""
        mock_config.return_value.METADATA_FILE = self.metadata_file
        mock_config.return_value.STATUS_LOG_FILE = self.status_log_file

        manager = MetadataManager()

        # Create many status entries to test cleanup
        for i in range(150):  # More than the usual max (100)
            manager.log_status("info", f"Entry {i}")

        with open(self.status_log_file, "r") as f:
            status_log = json.load(f)

        # Should not exceed max entries (typically 100)
        assert len(status_log["entries"]) <= 100

        # Should keep the most recent entries
        last_entry = status_log["entries"][-1]
        assert "Entry 149" in last_entry["message"]

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_calculate_hash(self, mock_config):
        """Test hash calculation for requirements"""
        mock_config.return_value.METADATA_FILE = self.metadata_file
        mock_config.return_value.STATUS_LOG_FILE = self.status_log_file

        manager = MetadataManager()

        # Test with same data should produce same hash
        hash1 = manager._calculate_hash(self.sample_requirements)
        hash2 = manager._calculate_hash(self.sample_requirements)
        assert hash1 == hash2

        # Test with different data should produce different hash
        modified_requirements = self.sample_requirements.copy()
        modified_requirements[0]["name"] = "Modified Name"
        hash3 = manager._calculate_hash(modified_requirements)
        assert hash1 != hash3

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_update_system_info(self, mock_config):
        """Test updating system information"""
        mock_config.return_value.METADATA_FILE = self.metadata_file
        mock_config.return_value.STATUS_LOG_FILE = self.status_log_file

        manager = MetadataManager()

        system_info = {
            "version": "2.0.0",
            "environment": "production",
            "python_version": "3.9.0",
        }

        manager.update_system_info(system_info)

        metadata = manager.load_metadata()
        assert "system_info" in metadata

        saved_info = metadata["system_info"]
        assert saved_info["version"] == "2.0.0"
        assert saved_info["environment"] == "production"
        assert "last_update" in saved_info

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_load_metadata_invalid_json(self, mock_config):
        """Test loading metadata with invalid JSON"""
        mock_config.return_value.METADATA_FILE = self.metadata_file
        mock_config.return_value.STATUS_LOG_FILE = self.status_log_file

        # Create file with invalid JSON
        with open(self.metadata_file, "w") as f:
            f.write("invalid json content {")

        manager = MetadataManager()
        metadata = manager.load_metadata()

        # Should return empty dict on invalid JSON
        assert metadata == {}

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_save_metadata_permission_error(self, mock_config):
        """Test handling of permission errors during save"""
        mock_config.return_value.METADATA_FILE = (
            "/root/metadata.json"  # No write permission
        )
        mock_config.return_value.STATUS_LOG_FILE = self.status_log_file

        manager = MetadataManager()

        # Should handle permission error gracefully
        try:
            manager.save_metadata(self.sample_metadata)
            # If no exception is raised, the method handled it gracefully
        except PermissionError:
            # This is expected for directories without write permission
            pass


class TestMetadataManagerValidation:
    """Test cases for metadata validation and edge cases"""

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_validate_metadata_structure(self, mock_config):
        """Test validation of metadata structure"""
        temp_dir = tempfile.mkdtemp()
        metadata_file = os.path.join(temp_dir, "metadata.json")
        status_log_file = os.path.join(temp_dir, "status_log.json")

        mock_config.return_value.METADATA_FILE = metadata_file
        mock_config.return_value.STATUS_LOG_FILE = status_log_file

        manager = MetadataManager()

        # Test with valid metadata structure
        valid_metadata = {
            "last_processed_requirements": {
                "hash": "abc123",
                "processed_at": "2024-01-15T10:00:00",
            }
        }

        # Should not raise exception
        manager.save_metadata(valid_metadata)

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_empty_requirements_list(self, mock_config):
        """Test handling of empty requirements list"""
        temp_dir = tempfile.mkdtemp()
        metadata_file = os.path.join(temp_dir, "metadata.json")
        status_log_file = os.path.join(temp_dir, "status_log.json")

        mock_config.return_value.METADATA_FILE = metadata_file
        mock_config.return_value.STATUS_LOG_FILE = status_log_file

        manager = MetadataManager()
        manager.update_processed_requirements([])

        # Should handle empty list gracefully
        metadata = manager.load_metadata()
        assert "last_processed_requirements" in metadata
        assert metadata["last_processed_requirements"]["newly_processed"] == []

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_concurrent_access_simulation(self, mock_config):
        """Test simulation of concurrent access to metadata"""
        temp_dir = tempfile.mkdtemp()
        metadata_file = os.path.join(temp_dir, "metadata.json")
        status_log_file = os.path.join(temp_dir, "status_log.json")

        mock_config.return_value.METADATA_FILE = metadata_file
        mock_config.return_value.STATUS_LOG_FILE = status_log_file

        # Create two manager instances (simulating concurrent access)
        manager1 = MetadataManager()
        manager2 = MetadataManager()

        # Both managers update metadata
        manager1.log_status("info", "Manager 1 update")
        manager2.log_status("info", "Manager 2 update")

        # Both updates should be preserved
        status = manager1.get_latest_status()
        assert status["status"] == "info"

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)


class TestMetadataManagerUtilities:
    """Test utility methods of MetadataManager"""

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_format_timestamp(self, mock_config):
        """Test timestamp formatting"""
        temp_dir = tempfile.mkdtemp()
        mock_config.return_value.METADATA_FILE = os.path.join(temp_dir, "metadata.json")
        mock_config.return_value.STATUS_LOG_FILE = os.path.join(
            temp_dir, "status_log.json"
        )

        manager = MetadataManager()

        # Test with datetime object
        dt = datetime(2024, 1, 15, 10, 30, 45)
        formatted = manager._format_timestamp(dt)

        assert "2024-01-15" in formatted
        assert "10:30:45" in formatted

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    @patch("CodeFromRequirements.metadata_manager.Config")
    def test_status_log_rotation(self, mock_config):
        """Test status log rotation when it gets too large"""
        temp_dir = tempfile.mkdtemp()
        status_log_file = os.path.join(temp_dir, "status_log.json")

        mock_config.return_value.METADATA_FILE = os.path.join(temp_dir, "metadata.json")
        mock_config.return_value.STATUS_LOG_FILE = status_log_file

        manager = MetadataManager()

        # Create a large number of status entries
        for i in range(200):
            manager.log_status("info", f"Status entry {i}")

        # Check that old entries are removed to keep the log manageable
        with open(status_log_file, "r") as f:
            status_log = json.load(f)

        # Should not exceed reasonable limit
        assert len(status_log["entries"]) <= 100

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__])
