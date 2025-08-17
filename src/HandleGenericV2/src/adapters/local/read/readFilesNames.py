import os
import json


def directory_to_json(
    directory_path: str, include_subdirs: bool = True, workspace: str = "LOCAL"
) -> str:
    """
    Convert a directory structure into a JSON string based on workspace type.

    Args:
        directory_path (str): Path to the directory.
        include_subdirs (bool): Whether to include subdirectories recursively.
        workspace (str): Workspace type (LOCAL, CLOUD, etc.) - currently supports LOCAL.

    Returns:
        str: JSON string representing the directory structure.
    """

    # Handle different workspace types
    if workspace.upper() == "LOCAL":
        return _build_local_directory_structure(directory_path, include_subdirs)
    elif workspace.upper() == "CLOUD":
        # Future implementation for cloud-based file systems
        raise NotImplementedError("CLOUD workspace not yet implemented")
    else:
        # Default to LOCAL for unknown workspace types
        return _build_local_directory_structure(directory_path, include_subdirs)


def _build_local_directory_structure(path: str, include_subdirs: bool) -> str:
    """
    Build directory structure for LOCAL workspace.
    """

    def build_structure(current_path: str) -> dict:
        structure = {"name": os.path.basename(current_path)}

        if os.path.isdir(current_path):
            structure["type"] = "directory"
            structure["children"] = []
            for entry in sorted(os.listdir(current_path)):
                full_path = os.path.join(current_path, entry)
                if os.path.isdir(full_path) and include_subdirs:
                    structure["children"].append(build_structure(full_path))
                elif os.path.isfile(full_path):
                    structure["children"].append({"name": entry, "type": "file"})
        else:
            structure["type"] = "file"
        return structure

    # Build structure starting from root
    dir_structure = build_structure(path)
    return json.dumps(dir_structure, indent=4)
