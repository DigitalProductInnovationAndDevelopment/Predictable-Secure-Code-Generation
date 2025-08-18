import os
import json
from typing import Dict, Any


def save_json_to_file(
    filename: str, data: Dict[str, Any], directory: str, workspace: str = "LOCAL"
) -> str:
    """
    Save JSON data to a file based on workspace type.

    Args:
        filename (str): The name of the JSON file (e.g. 'output.json').
        data (dict): The JSON data to save.
        directory (str): The directory where the file should be saved.
        workspace (str): Workspace type (LOCAL, CLOUD, etc.) - currently supports LOCAL.

    Returns:
        str: The full path to the saved file.
    """

    # Handle different workspace types
    if workspace.upper() == "LOCAL":
        return _save_to_local_file(filename, data, directory)
    elif workspace.upper() == "CLOUD":
        # Future implementation for cloud storage
        raise NotImplementedError("CLOUD workspace not yet implemented")
    else:
        # Default to LOCAL for unknown workspace types
        return _save_to_local_file(filename, data, directory)


def _save_to_local_file(filename: str, data: Dict[str, Any], directory: str) -> str:
    """
    Save JSON data to a local file.
    """
    # Ensure directory exists
    os.makedirs(directory, exist_ok=True)

    # Ensure filename ends with .json
    if not filename.endswith(".json"):
        filename += ".json"

    # Full file path
    file_path = os.path.join(directory, filename)

    # Write JSON to file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return file_path
