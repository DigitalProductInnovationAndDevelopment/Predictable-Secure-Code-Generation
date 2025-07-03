import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from config import Config
import logging


class MetadataManager:
    """Manages metadata, status logging, and tracking of processed requirements"""

    def __init__(self):
        self.config = Config()
        self.metadata_file = self.config.METADATA_FILE
        self.status_log_file = self.config.STATUS_LOG_FILE

    def load_metadata(self) -> Dict[str, Any]:
        """Load existing metadata from file"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Error loading metadata: {str(e)}")

        return self._get_default_metadata()

    def save_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Save metadata to file"""
        try:
            os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)

            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, default=str)

            logging.info(f"Metadata saved to {self.metadata_file}")
            return True

        except Exception as e:
            logging.error(f"Error saving metadata: {str(e)}")
            return False

    def log_status(
        self, status: str, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log status information"""
        status_entry = {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "message": message,
            "details": details or {},
        }

        try:
            # Load existing status log
            status_log = []
            if os.path.exists(self.status_log_file):
                with open(self.status_log_file, "r", encoding="utf-8") as f:
                    status_log = json.load(f)

            # Add new entry
            status_log.append(status_entry)

            # Keep only last 100 entries
            status_log = status_log[-100:]

            # Save updated log
            os.makedirs(os.path.dirname(self.status_log_file), exist_ok=True)
            with open(self.status_log_file, "w", encoding="utf-8") as f:
                json.dump(status_log, f, indent=2, default=str)

            logging.info(f"Status logged: {status} - {message}")

        except Exception as e:
            logging.error(f"Error logging status: {str(e)}")

    def get_latest_status(self) -> Dict[str, Any]:
        """Get the latest status information"""
        try:
            if os.path.exists(self.status_log_file):
                with open(self.status_log_file, "r", encoding="utf-8") as f:
                    status_log = json.load(f)

                if status_log:
                    latest = status_log[-1]

                    # Add summary information
                    summary = self._generate_status_summary(
                        status_log[-10:]
                    )  # Last 10 entries

                    return {
                        "latest_status": latest,
                        "summary": summary,
                        "metadata": self.load_metadata(),
                    }
        except Exception as e:
            logging.error(f"Error getting latest status: {str(e)}")

        return {
            "latest_status": {
                "timestamp": datetime.now().isoformat(),
                "status": "unknown",
                "message": "No status information available",
            },
            "summary": {},
            "metadata": self._get_default_metadata(),
        }

    def update_processed_requirements(self, requirements: List[Dict[str, Any]]) -> None:
        """Update metadata with newly processed requirements"""
        try:
            metadata = self.load_metadata()

            # Update processed requirements tracking
            if "processed_requirements" not in metadata:
                metadata["processed_requirements"] = []

            # Add new requirements with processing timestamp
            for req in requirements:
                processed_req = req.copy()
                processed_req["processed_at"] = datetime.now().isoformat()
                metadata["processed_requirements"].append(processed_req)

            # Update statistics
            metadata["statistics"]["total_processed"] = len(
                metadata["processed_requirements"]
            )
            metadata["statistics"]["last_processed_count"] = len(requirements)
            metadata["statistics"]["last_update"] = datetime.now().isoformat()

            # Save updated metadata
            self.save_metadata(metadata)

            logging.info(
                f"Updated metadata with {len(requirements)} processed requirements"
            )

        except Exception as e:
            logging.error(f"Error updating processed requirements: {str(e)}")

    def update_codebase_analysis(self, analysis: Dict[str, Any]) -> None:
        """Update metadata with codebase analysis results"""
        try:
            metadata = self.load_metadata()

            metadata["codebase_analysis"] = {
                "last_analyzed": datetime.now().isoformat(),
                "file_count": analysis.get("file_count", 0),
                "total_lines": analysis.get("total_lines", 0),
                "functions_count": len(analysis.get("functions", {})),
                "classes_count": len(analysis.get("classes", {})),
                "dependencies": analysis.get("dependencies", []),
                "directories": analysis.get("directories", []),
            }

            self.save_metadata(metadata)
            logging.info("Updated metadata with codebase analysis")

        except Exception as e:
            logging.error(f"Error updating codebase analysis: {str(e)}")

    def update_validation_results(self, validation_results: Dict[str, Any]) -> None:
        """Update metadata with validation results"""
        try:
            metadata = self.load_metadata()

            if "validation_history" not in metadata:
                metadata["validation_history"] = []

            validation_entry = {
                "timestamp": datetime.now().isoformat(),
                "results": validation_results,
            }

            metadata["validation_history"].append(validation_entry)

            # Keep only last 50 validation results
            metadata["validation_history"] = metadata["validation_history"][-50:]

            # Update latest validation status
            metadata["latest_validation"] = validation_entry

            self.save_metadata(metadata)
            logging.info("Updated metadata with validation results")

        except Exception as e:
            logging.error(f"Error updating validation results: {str(e)}")

    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing statistics and metrics"""
        try:
            metadata = self.load_metadata()

            stats = {
                "total_requirements_processed": len(
                    metadata.get("processed_requirements", [])
                ),
                "last_processing_date": None,
                "success_rate": 0.0,
                "average_processing_time": 0.0,
                "recent_activity": [],
            }

            # Load status log for detailed statistics
            if os.path.exists(self.status_log_file):
                with open(self.status_log_file, "r", encoding="utf-8") as f:
                    status_log = json.load(f)

                # Calculate success rate
                recent_statuses = [entry["status"] for entry in status_log[-20:]]
                if recent_statuses:
                    success_count = recent_statuses.count("success")
                    stats["success_rate"] = (success_count / len(recent_statuses)) * 100

                # Get recent activity
                stats["recent_activity"] = status_log[-10:]

                # Find last processing date
                processing_entries = [
                    entry
                    for entry in status_log
                    if entry["status"] in ["success", "failed"]
                ]
                if processing_entries:
                    stats["last_processing_date"] = processing_entries[-1]["timestamp"]

            return stats

        except Exception as e:
            logging.error(f"Error getting processing statistics: {str(e)}")
            return {}

    def cleanup_old_data(self, days_to_keep: int = 30) -> None:
        """Clean up old data to prevent files from growing too large"""
        try:
            cutoff_date = datetime.now()
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)
            cutoff_str = cutoff_date.isoformat()

            # Clean status log
            if os.path.exists(self.status_log_file):
                with open(self.status_log_file, "r", encoding="utf-8") as f:
                    status_log = json.load(f)

                # Filter out old entries
                filtered_log = [
                    entry
                    for entry in status_log
                    if entry.get("timestamp", "") > cutoff_str
                ]

                with open(self.status_log_file, "w", encoding="utf-8") as f:
                    json.dump(filtered_log, f, indent=2, default=str)

                logging.info(
                    f"Cleaned up {len(status_log) - len(filtered_log)} old status entries"
                )

            # Clean metadata validation history
            metadata = self.load_metadata()
            if "validation_history" in metadata:
                filtered_validation = [
                    entry
                    for entry in metadata["validation_history"]
                    if entry.get("timestamp", "") > cutoff_str
                ]

                metadata["validation_history"] = filtered_validation
                self.save_metadata(metadata)

                logging.info("Cleaned up old validation history")

        except Exception as e:
            logging.error(f"Error cleaning up old data: {str(e)}")

    def _get_default_metadata(self) -> Dict[str, Any]:
        """Get default metadata structure"""
        return {
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "processed_requirements": [],
            "codebase_analysis": {},
            "validation_history": [],
            "latest_validation": {},
            "statistics": {
                "total_processed": 0,
                "last_processed_count": 0,
                "last_update": datetime.now().isoformat(),
            },
            "configuration": {
                "requirements_file": self.config.REQUIREMENTS_FILE,
                "ai_model": self.config.OPENAI_MODEL,
                "max_retries": self.config.MAX_RETRIES,
            },
        }

    def _generate_status_summary(
        self, recent_statuses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a summary of recent statuses"""
        if not recent_statuses:
            return {}

        status_counts = {}
        for entry in recent_statuses:
            status = entry.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_entries": len(recent_statuses),
            "status_distribution": status_counts,
            "latest_timestamp": recent_statuses[-1].get("timestamp", ""),
            "success_rate": (
                (status_counts.get("success", 0) / len(recent_statuses)) * 100
                if recent_statuses
                else 0
            ),
        }
