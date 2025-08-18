import os
import json
import logging
import sys
from typing import Dict, Any

# Add the HandleGenericV2 directory to the path so we can import config
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

config = Config()


def directory_to_json_filtered(
    directory_path: str, include_subdirs: bool = True, workspace: str = "LOCAL"
) -> str:
    """
    Convert a directory structure into a JSON string, but ONLY include files
    that match the project's main programming language defined in config.LANGUAGE_ARCHITECTURE.

    Args:
        directory_path (str): Path to the directory.
        include_subdirs (bool): Whether to include subdirectories recursively.
        workspace (str): Workspace type (LOCAL, CLOUD, etc.) - currently supports LOCAL.

    Returns:
        str: JSON string representing the filtered directory structure.
    """
    if workspace.upper() != "LOCAL":
        raise NotImplementedError(f"{workspace} workspace not yet implemented")

    # Get target programming language from config
    lang_arch_file = getattr(config, "LANGUAGE_ARCHITECTURE", None)
    output_dir = getattr(config, "OUTPUT_DIR", None) or "./output"

    if not lang_arch_file:
        raise ValueError("Config must define LANGUAGE_ARCHITECTURE filename")

    # Ensure filename has .json extension
    if not lang_arch_file.endswith(".json"):
        lang_arch_file += ".json"

    # Read the language architecture file
    lang_arch_path = os.path.join(output_dir, lang_arch_file)
    try:
        with open(lang_arch_path, "r") as f:
            lang_info = json.load(f)
    except FileNotFoundError:
        raise ValueError(f"Language architecture file not found: {lang_arch_path}")
    except json.JSONDecodeError:
        raise ValueError(
            f"Invalid JSON in language architecture file: {lang_arch_path}"
        )

    if "programming_language" not in lang_info:
        raise ValueError(
            f"Language architecture file must contain 'programming_language' key: {lang_info}"
        )

    target_lang = lang_info["programming_language"].upper()
    logger.info(f"Filtering directory for language: {target_lang}")

    # Build the pruned structure
    dir_structure = _build_local_directory_structure_filtered(
        directory_path, include_subdirs, target_lang
    )
    return json.dumps(dir_structure, indent=4)


def _build_local_directory_structure_filtered(
    path: str, include_subdirs: bool, target_lang: str
) -> Dict[str, Any]:
    """
    Build directory structure for LOCAL workspace, including only files
    of the target programming language.
    """

    SUPPORTED_EXTENSIONS = config.SUPPORTED_EXTENSIONS

    def build_structure(current_path: str) -> Dict[str, Any]:
        structure = {"name": os.path.basename(current_path)}

        if os.path.isdir(current_path):
            structure["type"] = "directory"
            children = []
            for entry in sorted(os.listdir(current_path)):
                full_path = os.path.join(current_path, entry)

                if os.path.isdir(full_path) and include_subdirs:
                    child = build_structure(full_path)
                    # Only include directories that actually contain matching files
                    if child.get("children"):
                        children.append(child)

                elif os.path.isfile(full_path):
                    ext = os.path.splitext(entry)[1].lower()
                    language = SUPPORTED_EXTENSIONS.get(ext, "UNKNOWN")

                    if language == target_lang:
                        children.append(
                            {"name": entry, "type": "file", "language": language}
                        )

            if children:
                structure["children"] = children
            else:
                # Prune empty directories
                return {}
        else:
            structure["type"] = "file"
            ext = os.path.splitext(current_path)[1].lower()
            language = SUPPORTED_EXTENSIONS.get(ext, "UNKNOWN")
            if language == target_lang:
                structure["language"] = language
            else:
                return {}

        return structure

    return build_structure(path)


# if __name__ == "__main__":
#     # Example usage
#     example_path = "/Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/input/PythonExamples/Example1/code"
#     result = directory_to_json_filtered(example_path)
#     print(result)
