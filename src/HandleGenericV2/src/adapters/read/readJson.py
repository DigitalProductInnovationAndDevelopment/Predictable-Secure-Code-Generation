import os
import json
from typing import Dict, Any, Optional


def read_json_file(json_file_path: str, workspace: str = "LOCAL") -> Dict[str, Any]:
    """
    Read a JSON file and return its content based on workspace type.

    Args:
        json_file_path (str): Path to the JSON file.
        workspace (str): Workspace type (LOCAL, CLOUD, etc.) - currently supports LOCAL.

    Returns:
        Dict[str, Any]: JSON content as a Python dictionary.
    """

    # Handle different workspace types
    if workspace.upper() == "LOCAL":
        return _read_local_json_file(json_file_path)
    elif workspace.upper() == "CLOUD":
        # Future implementation for cloud-based file systems
        raise NotImplementedError("CLOUD workspace not yet implemented")
    else:
        # Default to LOCAL for unknown workspace types
        return _read_local_json_file(json_file_path)


def _read_local_json_file(json_file_path: str) -> Dict[str, Any]:
    """
    Read JSON file from LOCAL workspace and return its content.
    """
    try:
        with open(json_file_path, "r", encoding="utf-8") as jsonfile:
            data = json.load(jsonfile)
            return data

    except FileNotFoundError:
        error_structure = {
            "error": "File not found",
            "file_path": json_file_path,
            "message": f"Could not find the JSON file at {json_file_path}",
        }
        return error_structure

    except json.JSONDecodeError as e:
        error_structure = {
            "error": "JSON parsing error",
            "file_path": json_file_path,
            "message": f"Error parsing JSON file: {str(e)}",
        }
        return error_structure

    except Exception as e:
        error_structure = {
            "error": "File reading error",
            "file_path": json_file_path,
            "message": f"Error reading JSON file: {str(e)}",
        }
        return error_structure


def read_json_file_filtered(
    json_file_path: str, filter_keys: Optional[list] = None, workspace: str = "LOCAL"
) -> Dict[str, Any]:
    """
    Read a JSON file and return filtered content based on specified keys.

    Args:
        json_file_path (str): Path to the JSON file.
        filter_keys (list): List of keys to include in the result (None for all keys).
        workspace (str): Workspace type (LOCAL, CLOUD, etc.).

    Returns:
        Dict[str, Any]: Filtered JSON content as a Python dictionary.
    """

    if workspace.upper() == "LOCAL":
        return _read_local_json_file_filtered(json_file_path, filter_keys)
    elif workspace.upper() == "CLOUD":
        raise NotImplementedError("CLOUD workspace not yet implemented")
    else:
        return _read_local_json_file_filtered(json_file_path, filter_keys)


def _read_local_json_file_filtered(
    json_file_path: str, filter_keys: Optional[list] = None
) -> Dict[str, Any]:
    """
    Read and filter JSON file from LOCAL workspace.
    """
    try:
        with open(json_file_path, "r", encoding="utf-8") as jsonfile:
            data = json.load(jsonfile)

            # Apply filtering if keys are specified
            if filter_keys and isinstance(data, dict):
                filtered_data = {}
                for key in filter_keys:
                    if key in data:
                        filtered_data[key] = data[key]
                return filtered_data
            else:
                return data

    except FileNotFoundError:
        error_structure = {
            "error": "File not found",
            "file_path": json_file_path,
            "message": f"Could not find the JSON file at {json_file_path}",
        }
        return error_structure

    except json.JSONDecodeError as e:
        error_structure = {
            "error": "JSON parsing error",
            "file_path": json_file_path,
            "message": f"Error parsing JSON file: {str(e)}",
        }
        return error_structure

    except Exception as e:
        error_structure = {
            "error": "File reading error",
            "file_path": json_file_path,
            "message": f"Error reading JSON file: {str(e)}",
        }
        return error_structure


# Example usage and testing
if __name__ == "__main__":
    # Test with a sample JSON file
    json_path = "../../../output/PythonExample/Example1/environment/metadata.json"

    if os.path.exists(json_path):
        print("=== Basic JSON Reading ===")
        result = read_json_file(json_path)
        print(
            f"File read successfully. Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}"
        )

        print("\n=== Filtered JSON Reading (files key only) ===")
        filtered_result = read_json_file_filtered(json_path, filter_keys=["files"])
        print(
            f"Filtered result keys: {list(filtered_result.keys()) if isinstance(filtered_result, dict) else 'Not a dict'}"
        )
    else:
        print(f"Test file not found at: {json_path}")
        print("Please ensure the metadata.json file exists at the specified path.")
