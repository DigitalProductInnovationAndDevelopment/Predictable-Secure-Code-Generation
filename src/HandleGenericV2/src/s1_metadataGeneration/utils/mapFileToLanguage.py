import os
import json
import re
import logging
import sys
from typing import Dict, Any, List

# Add the HandleGenericV2 directory to the path so we can import config
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from config import Config


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

config = Config()


def directory_to_json_with_lang(
    directory_path: str, include_subdirs: bool = True, workspace: str = "LOCAL"
) -> str:
    """
    Convert a directory structure into a JSON string and include programming language
    based on file extensions.

    Args:
        directory_path (str): Path to the directory.
        include_subdirs (bool): Whether to include subdirectories recursively.
        workspace (str): Workspace type (LOCAL, CLOUD, etc.) - currently supports LOCAL.

    Returns:
        str: JSON string representing the directory structure with languages.
    """

    if workspace.upper() == "LOCAL":
        return _build_local_directory_structure_with_lang(
            directory_path, include_subdirs
        )
    else:
        raise NotImplementedError(f"{workspace} workspace not yet implemented")


def _build_local_directory_structure_with_lang(path: str, include_subdirs: bool) -> str:
    """
    Build directory structure for LOCAL workspace with language detection.
    """

    def build_structure(current_path: str) -> dict:
        structure = {"name": os.path.basename(current_path)}
        SUPPORTED_EXTENSIONS = config.SUPPORTED_EXTENSIONS

        if os.path.isdir(current_path):
            structure["type"] = "directory"
            structure["children"] = []
            for entry in sorted(os.listdir(current_path)):
                full_path = os.path.join(current_path, entry)
                if os.path.isdir(full_path) and include_subdirs:
                    structure["children"].append(build_structure(full_path))
                elif os.path.isfile(full_path):
                    ext = os.path.splitext(entry)[1].lower()
                    language = SUPPORTED_EXTENSIONS.get(ext, "UNKNOWN")
                    structure["children"].append(
                        {"name": entry, "type": "file", "language": language}
                    )
        else:
            structure["type"] = "file"
            ext = os.path.splitext(current_path)[1].lower()
            structure["language"] = SUPPORTED_EXTENSIONS.get(ext, "UNKNOWN")
        return structure

    dir_structure = build_structure(path)
    return json.dumps(dir_structure, indent=4)


if __name__ == "__main__":
    # Example usage
    example_path = "/Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/input/PythonExamples/Example1/code"
    result = directory_to_json_with_lang(example_path)
    print(result)
