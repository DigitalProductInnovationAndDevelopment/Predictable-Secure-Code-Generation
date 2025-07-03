import pandas as pd
import json
import os
import hashlib
from datetime import datetime
from typing import Tuple, List, Dict, Any
from config import Config
import logging


class RequirementsChecker:
    """Handles checking for new requirements from CSV/Excel files"""

    def __init__(self):
        self.config = Config()
        self.requirements_file = self.config.REQUIREMENTS_FILE
        self.metadata_file = self.config.METADATA_FILE

    def check_for_updates(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Check if there are new requirements compared to last processed state

        Returns:
            Tuple[bool, List[Dict]]: (has_updates, new_requirements)
        """
        try:
            # Load current requirements
            current_requirements = self._load_requirements_file()

            if not current_requirements:
                logging.warning("No requirements file found or file is empty")
                return False, []

            # Load previously processed requirements
            last_processed = self._load_last_processed_requirements()

            # Calculate file hash to detect changes
            current_hash = self._calculate_requirements_hash(current_requirements)
            last_hash = last_processed.get("hash", "")

            if current_hash == last_hash:
                logging.info("Requirements file hasn't changed")
                return False, []

            # Find new requirements
            new_requirements = self._identify_new_requirements(
                current_requirements, last_processed.get("requirements", [])
            )

            if not new_requirements:
                logging.info("Requirements file changed but no new requirements found")
                return False, []

            logging.info(f"Found {len(new_requirements)} new requirements")
            return True, new_requirements

        except Exception as e:
            logging.error(f"Error checking for requirement updates: {str(e)}")
            return False, []

    def _load_requirements_file(self) -> List[Dict[str, Any]]:
        """Load requirements from CSV or Excel file"""
        if not os.path.exists(self.requirements_file):
            logging.warning(f"Requirements file not found: {self.requirements_file}")
            return []

        try:
            # Determine file type and load accordingly
            if self.requirements_file.endswith(".csv"):
                df = pd.read_csv(self.requirements_file)
            elif self.requirements_file.endswith((".xlsx", ".xls")):
                df = pd.read_excel(self.requirements_file)
            else:
                raise ValueError(f"Unsupported file format: {self.requirements_file}")

            # Convert to list of dictionaries
            requirements = df.to_dict("records")

            # Validate required columns
            required_columns = ["id", "name", "description", "priority", "status"]
            for req in requirements:
                for col in required_columns:
                    if col not in req:
                        logging.warning(
                            f"Missing required column '{col}' in requirement: {req}"
                        )

            # Filter only 'new' or 'pending' requirements
            new_requirements = [
                req
                for req in requirements
                if str(req.get("status", "")).lower() in ["new", "pending", "active"]
            ]

            return new_requirements

        except Exception as e:
            logging.error(f"Error loading requirements file: {str(e)}")
            return []

    def _load_last_processed_requirements(self) -> Dict[str, Any]:
        """Load the last processed requirements from metadata"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, "r") as f:
                    metadata = json.load(f)
                    return metadata.get("last_processed_requirements", {})
        except Exception as e:
            logging.error(f"Error loading last processed requirements: {str(e)}")

        return {}

    def _calculate_requirements_hash(self, requirements: List[Dict[str, Any]]) -> str:
        """Calculate hash of requirements for change detection"""
        # Sort requirements by ID to ensure consistent hashing
        sorted_reqs = sorted(requirements, key=lambda x: str(x.get("id", "")))

        # Create string representation for hashing
        req_string = json.dumps(sorted_reqs, sort_keys=True)

        # Calculate SHA256 hash
        return hashlib.sha256(req_string.encode()).hexdigest()

    def _identify_new_requirements(
        self, current: List[Dict[str, Any]], last_processed: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify which requirements are new compared to last processed"""
        if not last_processed:
            return current

        # Create set of previously processed requirement IDs
        processed_ids = {str(req.get("id", "")) for req in last_processed}

        # Find requirements that weren't in the last processed set
        new_requirements = [
            req for req in current if str(req.get("id", "")) not in processed_ids
        ]

        return new_requirements

    def mark_requirements_processed(self, requirements: List[Dict[str, Any]]) -> None:
        """Mark requirements as processed in metadata"""
        try:
            # Load existing metadata
            metadata = {}
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, "r") as f:
                    metadata = json.load(f)

            # Update processed requirements
            all_requirements = self._load_requirements_file()
            metadata["last_processed_requirements"] = {
                "requirements": all_requirements,
                "hash": self._calculate_requirements_hash(all_requirements),
                "processed_at": datetime.now().isoformat(),
                "newly_processed": requirements,
            }

            # Save updated metadata
            os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
            with open(self.metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            logging.info(f"Marked {len(requirements)} requirements as processed")

        except Exception as e:
            logging.error(f"Error marking requirements as processed: {str(e)}")

    def create_sample_requirements_file(self) -> None:
        """Create a sample requirements file for testing"""
        sample_data = [
            {
                "id": "REQ-001",
                "name": "Add User Authentication",
                "description": "Implement JWT-based user authentication system",
                "priority": "High",
                "status": "new",
                "category": "Authentication",
                "estimated_hours": 8,
                "created_date": "2024-01-15",
            },
            {
                "id": "REQ-002",
                "name": "Database Migration Tool",
                "description": "Create automated database migration scripts",
                "priority": "Medium",
                "status": "new",
                "category": "Database",
                "estimated_hours": 4,
                "created_date": "2024-01-16",
            },
            {
                "id": "REQ-003",
                "name": "API Rate Limiting",
                "description": "Implement rate limiting for API endpoints",
                "priority": "Medium",
                "status": "completed",
                "category": "API",
                "estimated_hours": 3,
                "created_date": "2024-01-10",
            },
        ]

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.requirements_file), exist_ok=True)

        # Save as CSV
        df = pd.DataFrame(sample_data)
        df.to_csv(self.requirements_file, index=False)

        logging.info(f"Created sample requirements file: {self.requirements_file}")
