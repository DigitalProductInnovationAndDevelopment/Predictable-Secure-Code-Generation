import os
import json
import csv
from typing import Dict, Any, List


def requirements_csv_to_json(csv_file_path: str, workspace: str = "LOCAL") -> str:
    """
    Convert a requirements CSV file into a JSON string based on workspace type.

    Args:
        csv_file_path (str): Path to the CSV file.
        workspace (str): Workspace type (LOCAL, CLOUD, etc.) - currently supports LOCAL.

    Returns:
        str: JSON string representing the requirements structure.
    """

    # Handle different workspace types
    if workspace.upper() == "LOCAL":
        return _read_local_requirements_csv(csv_file_path)
    elif workspace.upper() == "CLOUD":
        # Future implementation for cloud-based file systems
        raise NotImplementedError("CLOUD workspace not yet implemented")
    else:
        # Default to LOCAL for unknown workspace types
        return _read_local_requirements_csv(csv_file_path)


def _read_local_requirements_csv(csv_file_path: str) -> str:
    """
    Read requirements CSV file from LOCAL workspace and convert to JSON.
    """
    try:
        requirements = []

        with open(csv_file_path, "r", encoding="utf-8") as csvfile:
            csv_reader = csv.DictReader(csvfile)

            for row in csv_reader:
                requirement = {
                    "id": row.get("id", ""),
                    "description": row.get("description", ""),
                    "status": "pending",  # Default status
                    "priority": "medium",  # Default priority
                    "type": "functional",  # Default type
                }
                requirements.append(requirement)

        # Create the final structure
        requirements_structure = {
            "file_type": "requirements",
            "source_file": os.path.basename(csv_file_path),
            "total_requirements": len(requirements),
            "requirements": requirements,
        }

        return json.dumps(requirements_structure, indent=4)

    except FileNotFoundError:
        error_structure = {
            "error": "File not found",
            "file_path": csv_file_path,
            "message": f"Could not find the requirements file at {csv_file_path}",
        }
        return json.dumps(error_structure, indent=4)

    except Exception as e:
        error_structure = {
            "error": "File reading error",
            "file_path": csv_file_path,
            "message": f"Error reading requirements file: {str(e)}",
        }
        return json.dumps(error_structure, indent=4)


def requirements_csv_to_json_filtered(
    csv_file_path: str,
    filter_by_status: str = None,
    filter_by_priority: str = None,
    filter_by_type: str = None,
    workspace: str = "LOCAL",
) -> str:
    """
    Convert a requirements CSV file to JSON with optional filtering.

    Args:
        csv_file_path (str): Path to the CSV file.
        filter_by_status (str): Filter requirements by status (e.g., "pending", "completed").
        filter_by_priority (str): Filter requirements by priority (e.g., "high", "medium", "low").
        filter_by_type (str): Filter requirements by type (e.g., "functional", "non-functional").
        workspace (str): Workspace type (LOCAL, CLOUD, etc.).

    Returns:
        str: JSON string representing the filtered requirements structure.
    """

    if workspace.upper() == "LOCAL":
        return _read_local_requirements_csv_filtered(
            csv_file_path, filter_by_status, filter_by_priority, filter_by_type
        )
    elif workspace.upper() == "CLOUD":
        raise NotImplementedError("CLOUD workspace not yet implemented")
    else:
        return _read_local_requirements_csv_filtered(
            csv_file_path, filter_by_status, filter_by_priority, filter_by_type
        )


def _read_local_requirements_csv_filtered(
    csv_file_path: str,
    filter_by_status: str = None,
    filter_by_priority: str = None,
    filter_by_type: str = None,
) -> str:
    """
    Read and filter requirements CSV file from LOCAL workspace.
    """
    try:
        requirements = []

        with open(csv_file_path, "r", encoding="utf-8") as csvfile:
            csv_reader = csv.DictReader(csvfile)

            for row in csv_reader:
                requirement = {
                    "id": row.get("id", ""),
                    "description": row.get("description", ""),
                    "status": row.get("status", "pending"),
                    "priority": row.get("priority", "medium"),
                    "type": row.get("type", "functional"),
                }

                # Apply filters if specified
                if filter_by_status and requirement["status"] != filter_by_status:
                    continue
                if filter_by_priority and requirement["priority"] != filter_by_priority:
                    continue
                if filter_by_type and requirement["type"] != filter_by_type:
                    continue

                requirements.append(requirement)

        # Create the final structure
        requirements_structure = {
            "file_type": "requirements",
            "source_file": os.path.basename(csv_file_path),
            "total_requirements": len(requirements),
            "filters_applied": {
                "status": filter_by_status,
                "priority": filter_by_priority,
                "type": filter_by_type,
            },
            "requirements": requirements,
        }

        return json.dumps(requirements_structure, indent=4)

    except FileNotFoundError:
        error_structure = {
            "error": "File not found",
            "file_path": csv_file_path,
            "message": f"Could not find the requirements file at {csv_file_path}",
        }
        return json.dumps(error_structure, indent=4)

    except Exception as e:
        error_structure = {
            "error": "File reading error",
            "file_path": csv_file_path,
            "message": f"Error reading requirements file: {str(e)}",
        }
        return json.dumps(error_structure, indent=4)


# Example usage and testing
if __name__ == "__main__":
    # Test with the requirements.csv file
    csv_path = "../../../input/PythonExamples/Example1/environment/requirements.csv"

    if os.path.exists(csv_path):
        print("=== Basic Requirements Reading ===")
        result = requirements_csv_to_json(csv_path)
        print(result)

        print("\n=== Filtered Requirements (High Priority) ===")
        filtered_result = requirements_csv_to_json_filtered(
            csv_path, filter_by_priority="high"
        )
        print(filtered_result)
    else:
        print(f"Test file not found at: {csv_path}")
        print("Please ensure the requirements.csv file exists at the specified path.")
