import os
import json


def directory_to_json(directory_path: str, include_subdirs: bool = True) -> str:
    """
    Convert a directory structure into a JSON string.

    Args:
        directory_path (str): Path to the directory.
        include_subdirs (bool): Whether to include subdirectories recursively.

    Returns:
        str: JSON string representing the directory structure.
    """

    def build_structure(path: str) -> dict:
        structure = {"name": os.path.basename(path)}

        if os.path.isdir(path):
            structure["type"] = "directory"
            structure["children"] = []
            for entry in sorted(os.listdir(path)):
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path) and include_subdirs:
                    structure["children"].append(build_structure(full_path))
                elif os.path.isfile(full_path):
                    structure["children"].append({"name": entry, "type": "file"})
        else:
            structure["type"] = "file"
        return structure

    # Build structure starting from root
    dir_structure = build_structure(directory_path)
    return json.dumps(dir_structure, indent=4)
