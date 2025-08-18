"""
Generate Metadata for Python Files

This module analyzes Python files in a codebase, uses AI to generate detailed metadata
for each file, and saves the results as JSON.
"""

import os
import json
import logging
import sys
from typing import Dict, Any, List
from pathlib import Path

# Get the current file's directory and add necessary paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..", "..")  # Go to HandleGenericV2
src_dir = os.path.join(current_dir, "..", "..")  # Go to src

# Add paths to sys.path
sys.path.insert(0, project_root)
sys.path.insert(0, src_dir)

# Now import the modules using the correct paths
from s1_metadataGeneration.utils.mapFileToLanguage import directory_to_json_filtered
from aiBrain.ai import AzureOpenAIClient
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

config = Config()


def extract_python_files_from_structure(
    directory_structure: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Extract Python files from the directory structure JSON.

    Args:
        directory_structure (Dict[str, Any]): The directory structure JSON

    Returns:
        List[Dict[str, Any]]: List of Python file information
    """
    python_files = []

    def traverse_structure(structure: Dict[str, Any], current_path: str = "") -> None:
        if structure.get("type") == "file" and structure.get("language") == "PYTHON":
            # For files, just use the filename since we'll construct the full path later
            file_info = {
                "name": structure["name"],
                "path": structure["name"],  # Just the filename, not the full path
                "type": "file",
                "language": "PYTHON",
            }
            python_files.append(file_info)
        elif structure.get("type") == "directory" and structure.get("children"):
            for child in structure["children"]:
                # Recursively traverse child directories
                traverse_structure(child, current_path)

    traverse_structure(directory_structure)
    return python_files


def read_python_file_content(file_path: str) -> str:
    """
    Read the content of a Python file.

    Args:
        file_path (str): Path to the Python file

    Returns:
        str: Content of the file
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ""


def generate_file_metadata_with_ai(
    file_content: str, file_name: str, ai_client: AzureOpenAIClient
) -> Dict[str, Any]:
    """
    Use AI to generate metadata for a Python file.

    Args:
        file_content (str): Content of the Python file
        file_name (str): Name of the file
        ai_client (AzureOpenAIClient): AI client instance

    Returns:
        Dict[str, Any]: Generated metadata
    """
    prompt = f"""
Analyze this Python file and provide detailed metadata in JSON format.

File: {file_name}

Code:
{file_content}

Return ONLY a JSON object with the following structure (no explanations, no markdown):
{{
    "file_name": "{file_name}",
    "description": "Brief description of what this file does",
    "main_purpose": "Main purpose or responsibility of this file",
    "functions": [
        {{
            "name": "function_name",
            "description": "What this function does",
            "parameters": ["param1", "param2"],
            "returns": "What this function returns",
            "purpose": "Why this function exists"
        }}
    ],
    "classes": [
        {{
            "name": "class_name",
            "description": "What this class represents",
            "methods": ["method1", "method2"],
            "purpose": "Why this class exists"
        }}
    ],
    "imports": ["import1", "import2"],
    "dependencies": ["dependency1", "dependency2"],
    "complexity": "LOW|MEDIUM|HIGH",
    "key_features": ["feature1", "feature2"]
}}

Be concise but thorough. Focus on the most important aspects.
"""

    try:
        result = ai_client.ask_question(prompt, max_tokens=1000, temperature=0.1)

        if result.get("status") == "success":
            # Parse the AI response to extract JSON
            ai_response = result.get("answer", "")

            # Try to extract JSON from the response
            try:
                # Remove any markdown formatting
                cleaned_response = ai_response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]

                # Try to find complete JSON objects
                cleaned_response = cleaned_response.strip()

                # If the response is truncated, try to complete it
                if not cleaned_response.endswith("}"):
                    # Find the last complete object or array
                    brace_count = 0
                    last_complete_pos = -1
                    for i, char in enumerate(cleaned_response):
                        if char == "{":
                            brace_count += 1
                        elif char == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                last_complete_pos = i

                    if last_complete_pos > 0:
                        cleaned_response = cleaned_response[: last_complete_pos + 1]
                        logger.warning(
                            f"Response was truncated, using complete portion: {cleaned_response[:100]}..."
                        )

                metadata = json.loads(cleaned_response.strip())
                return metadata
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                logger.error(f"Response was: {ai_response[:200]}...")
                return _create_fallback_metadata(file_name, file_content)
        else:
            logger.error(f"AI request failed: {result.get('error', 'Unknown error')}")
            return _create_fallback_metadata(file_name, file_content)

    except Exception as e:
        logger.error(f"Error generating metadata for {file_name}: {e}")
        return _create_fallback_metadata(file_name, file_content)


def _create_fallback_metadata(file_name: str, file_content: str) -> Dict[str, Any]:
    """
    Create fallback metadata when AI generation fails.

    Args:
        file_name (str): Name of the file
        file_content (str): Content of the file

    Returns:
        Dict[str, Any]: Basic fallback metadata
    """
    return {
        "file_name": file_name,
        "description": "Metadata generation failed - fallback data",
        "main_purpose": "Unknown",
        "functions": [],
        "classes": [],
        "imports": [],
        "dependencies": [],
        "complexity": "UNKNOWN",
        "key_features": [],
        "raw_content_length": len(file_content),
        "error": "AI metadata generation failed",
    }


def generate_codebase_metadata(
    codebase_path: str,
    output_dir: str = None,
    workspace: str = "LOCAL",
) -> Dict[str, Any]:
    """
    Generate comprehensive metadata for all Python files in a codebase.

    Args:
        codebase_path (str): Path to the codebase directory
        output_dir (str): Directory to save metadata (uses config.OUTPUT_DIR if not provided)
        workspace (str): Workspace type (default: "LOCAL")

    Returns:
        Dict[str, Any]: Complete metadata for the codebase
    """
    logger.info(f"Starting metadata generation for codebase: {codebase_path}")

    # Get workspace from config if not provided
    if not workspace:
        workspace = getattr(config, "WORKSPACE", "LOCAL")

    # Get output directory from config if not provided
    if not output_dir:
        output_dir = getattr(config, "OUTPUT_DIR", None)
        if not output_dir:
            raise ValueError(
                "OUTPUT_DIR must be set in config or provided as parameter"
            )

    logger.info(f"Using output directory: {output_dir}")

    # Step 1: Get filtered directory structure (only Python files)
    try:
        directory_json = directory_to_json_filtered(codebase_path, workspace=workspace)
        directory_structure = json.loads(directory_json)
        logger.info("Directory structure filtered successfully")
    except Exception as e:
        logger.error(f"Failed to get directory structure: {e}")
        raise

    # Step 2: Extract Python files
    python_files = extract_python_files_from_structure(directory_structure)
    logger.info(f"Found {len(python_files)} Python files to analyze")

    if not python_files:
        logger.warning("No Python files found in the codebase")
        # Return a valid metadata structure even when no files are found
        final_metadata = {
            "codebase_path": codebase_path,
            "workspace": workspace,
            "total_files": 0,
            "generation_timestamp": str(Path().cwd()),
            "files": [],
            "warning": "No Python files found in the codebase",
        }

        # Save empty metadata to file
        try:
            os.makedirs(output_dir, exist_ok=True)
            metadata_file_path = os.path.join(output_dir, "metadata.json")

            with open(metadata_file_path, "w", encoding="utf-8") as f:
                json.dump(final_metadata, f, indent=2, ensure_ascii=False)

            logger.info(f"Empty metadata saved to: {metadata_file_path}")

        except Exception as e:
            logger.error(f"Failed to save empty metadata: {e}")
            raise

        return final_metadata

    # Step 3: Initialize AI client
    try:
        ai_client = AzureOpenAIClient()
        logger.info("AI client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AI client: {e}")
        raise

    # Step 4: Generate metadata for each Python file
    metadata_results = []

    for file_info in python_files:
        # Construct the correct file path
        if file_info["path"].startswith("/"):
            # Absolute path
            file_path = file_info["path"]
        else:
            # Relative path - join with codebase_path
            file_path = os.path.join(codebase_path, file_info["path"])

        logger.info(f"Analyzing file: {file_info['name']} at path: {file_path}")

        # Read file content
        file_content = read_python_file_content(file_path)
        if not file_content:
            logger.warning(f"Skipping empty file: {file_info['name']}")
            continue

        # Generate metadata using AI
        file_metadata = generate_file_metadata_with_ai(
            file_content, file_info["name"], ai_client
        )

        # Add file path information
        file_metadata["file_path"] = file_info["path"]
        file_metadata["file_size"] = len(file_content)

        metadata_results.append(file_metadata)

        logger.info(f"Completed metadata for: {file_info['name']}")

    # Step 5: Create final metadata structure
    final_metadata = {
        "codebase_path": codebase_path,
        "workspace": workspace,
        "total_files": len(metadata_results),
        "generation_timestamp": str(Path().cwd()),
        "files": metadata_results,
    }

    # Step 6: Save metadata to file
    try:
        os.makedirs(output_dir, exist_ok=True)
        metadata_file_path = os.path.join(output_dir, "metadata.json")

        with open(metadata_file_path, "w", encoding="utf-8") as f:
            json.dump(final_metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"Metadata saved to: {metadata_file_path}")

    except Exception as e:
        logger.error(f"Failed to save metadata: {e}")
        raise

    return final_metadata


def main():
    """
    Main function for command line usage.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate metadata for Python codebase"
    )
    parser.add_argument(
        "--codebase",
        "-c",
        type=str,
        required=True,
        help="Path to the codebase directory",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output directory for metadata (uses config.OUTPUT_DIR if not provided)",
    )
    parser.add_argument(
        "--workspace",
        "-w",
        type=str,
        default="LOCAL",
        help="Workspace type (default: LOCAL)",
    )

    args = parser.parse_args()

    try:
        metadata = generate_codebase_metadata(
            args.codebase, args.output, args.workspace
        )

        print(f"Metadata generation completed successfully!")
        print(f"Total files analyzed: {metadata['total_files']}")

        # Get the actual output directory used
        actual_output_dir = args.output or getattr(config, "OUTPUT_DIR", "Unknown")
        print(f"Output saved to: {os.path.join(actual_output_dir, 'metadata.json')}")

    except Exception as e:
        logger.error(f"Metadata generation failed: {e}")
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
