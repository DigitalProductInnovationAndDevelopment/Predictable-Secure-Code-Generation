import os
import json
from typing import Dict, Any


def save_json_to_file(filename: str, data: Dict[str, Any], directory: str) -> str:
    """
    Save JSON data to a file in the given directory.

    Args:
        filename (str): The name of the JSON file (e.g. 'output.json').
        data (dict): The JSON data to save.
        directory (str): The directory where the file should be saved.

    Returns:
        str: The full path to the saved file.
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
