"""
Generate Metadata for Code Files

This module analyzes code files in a codebase, uses AI to generate detailed metadata
for each file, and saves the results as JSON. Works with any programming language.
"""

import os
import json
import logging
import sys
from typing import Dict, Any, List
from pathlib import Path
import re  # Added for _extract_partial_metadata

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


def extract_code_files_from_structure(
    directory_structure: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Extract code files from the directory structure JSON.

    Args:
        directory_structure (Dict[str, Any]): The directory structure JSON

    Returns:
        List[Dict[str, Any]]: List of code file information
    """
    code_files = []

    def traverse_structure(structure: Dict[str, Any], current_path: str = "") -> None:
        if structure.get("type") == "file" and structure.get("language") != "UNKNOWN":
            # For files, just use the filename since we'll construct the full path later
            file_info = {
                "name": structure["name"],
                "path": structure["name"],  # Just the filename, not the full path
                "type": "file",
                "language": structure["language"],
            }
            code_files.append(file_info)
        elif structure.get("type") == "directory" and structure.get("children"):
            for child in structure["children"]:
                # Recursively traverse child directories
                traverse_structure(child, current_path)

    traverse_structure(directory_structure)
    return code_files


def read_code_file_content(file_path: str) -> str:
    """
    Read the content of a code file.

    Args:
        file_path (str): Path to the code file

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
    file_content: str, file_name: str, language: str, ai_client: AzureOpenAIClient
) -> Dict[str, Any]:
    """
    Use AI to generate metadata for a code file.

    Args:
        file_content (str): Content of the code file
        file_name (str): Name of the file
        language (str): Programming language of the file
        ai_client (AzureOpenAIClient): AI client instance

    Returns:
        Dict[str, Any]: Generated metadata
    """
    prompt = f"""
Analyze this {language} file and provide detailed metadata in JSON format.

File: {file_name}
Language: {language}

Code:
{file_content}

Return ONLY a JSON object with the following structure (no explanations, no markdown):
{{
    "file_name": "{file_name}",
    "language": "{language}",
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
If the file doesn't have functions or classes, leave those arrays empty.
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

                # Try to parse the cleaned response
                try:
                    metadata = json.loads(cleaned_response.strip())
                    return metadata
                except json.JSONDecodeError:
                    # If still failing, try to extract partial metadata
                    logger.warning(
                        "Attempting to extract partial metadata from truncated response"
                    )
                    partial_metadata = _extract_partial_metadata(
                        cleaned_response, file_name, language
                    )
                    if partial_metadata:
                        return partial_metadata
                    else:
                        raise json.JSONDecodeError(
                            "Could not extract any valid metadata"
                        )

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                logger.error(f"Response was: {ai_response[:200]}...")
                return _create_fallback_metadata(file_name, file_content, language)
        else:
            logger.error(f"AI request failed: {result.get('error', 'Unknown error')}")
            return _create_fallback_metadata(file_name, file_content, language)

    except Exception as e:
        logger.error(f"Error generating metadata for {file_name}: {e}")
        return _create_fallback_metadata(file_name, file_content, language)


def _extract_partial_metadata(
    truncated_response: str, file_name: str, language: str
) -> Dict[str, Any]:
    """
    Extract partial metadata from a truncated AI response.

    Args:
        truncated_response (str): The truncated AI response
        file_name (str): Name of the file
        language (str): Programming language

    Returns:
        Dict[str, Any]: Partial metadata extracted from the response
    """
    try:
        # Try to find key-value pairs in the truncated response
        metadata = {
            "file_name": file_name,
            "language": language,
            "description": "Partial metadata from truncated response",
            "main_purpose": "Unknown",
            "functions": [],
            "classes": [],
            "imports": [],
            "dependencies": [],
            "complexity": "UNKNOWN",
            "key_features": [],
            "warning": "Response was truncated, metadata may be incomplete",
        }

        # Extract description if available
        desc_match = re.search(r'"description":\s*"([^"]*)"', truncated_response)
        if desc_match:
            metadata["description"] = desc_match.group(1)

        # Extract main_purpose if available
        purpose_match = re.search(r'"main_purpose":\s*"([^"]*)"', truncated_response)
        if purpose_match:
            metadata["main_purpose"] = purpose_match.group(1)

        # Extract complexity if available
        complexity_match = re.search(r'"complexity":\s*"([^"]*)"', truncated_response)
        if complexity_match:
            metadata["complexity"] = complexity_match.group(1)

        # Extract key features if available
        features_match = re.search(
            r'"key_features":\s*\[(.*?)\]', truncated_response, re.DOTALL
        )
        if features_match:
            features_text = features_match.group(1)
            # Extract individual features
            features = re.findall(r'"([^"]*)"', features_text)
            metadata["key_features"] = features

        # Extract imports if available
        imports_match = re.search(
            r'"imports":\s*\[(.*?)\]', truncated_response, re.DOTALL
        )
        if imports_match:
            imports_text = imports_match.group(1)
            imports = re.findall(r'"([^"]*)"', imports_text)
            metadata["imports"] = imports

        # Extract dependencies if available
        deps_match = re.search(
            r'"dependencies":\s*\[(.*?)\]', truncated_response, re.DOTALL
        )
        if deps_match:
            deps_text = deps_match.group(1)
            dependencies = re.findall(r'"([^"]*)"', deps_text)
            metadata["dependencies"] = dependencies

        # Check if we got any useful information
        if (
            metadata["description"] != "Partial metadata from truncated response"
            or metadata["main_purpose"] != "Unknown"
            or metadata["complexity"] != "UNKNOWN"
            or metadata["key_features"]
            or metadata["imports"]
            or metadata["dependencies"]
        ):
            return metadata
        else:
            return None

    except Exception as e:
        logger.error(f"Error extracting partial metadata: {e}")
        return None


def _create_fallback_metadata(
    file_name: str, file_content: str, language: str
) -> Dict[str, Any]:
    """
    Create fallback metadata when AI generation fails.

    Args:
        file_name (str): Name of the file
        file_content (str): Content of the file
        language (str): Programming language

    Returns:
        Dict[str, Any]: Basic fallback metadata
    """
    return {
        "file_name": file_name,
        "language": language,
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
    Generate comprehensive metadata for all code files in a codebase.

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

    # Step 1: Get filtered directory structure (only code files)
    try:
        directory_json = directory_to_json_filtered(codebase_path, workspace=workspace)
        directory_structure = json.loads(directory_json)
        logger.info("Directory structure filtered successfully")
    except Exception as e:
        logger.error(f"Failed to get directory structure: {e}")
        raise

    # Step 2: Extract code files
    code_files = extract_code_files_from_structure(directory_structure)
    logger.info(f"Found {len(code_files)} code files to analyze")

    if not code_files:
        logger.warning("No code files found in the codebase")
        # Return a valid metadata structure even when no files are found
        final_metadata = {
            "codebase_path": codebase_path,
            "workspace": workspace,
            "total_files": 0,
            "generation_timestamp": str(Path().cwd()),
            "files": [],
            "warning": "No code files found in the codebase",
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

    # Step 4: Generate metadata for each code file
    metadata_results = []

    for file_info in code_files:
        # Construct the correct file path
        if file_info["path"].startswith("/"):
            # Absolute path
            file_path = file_info["path"]
        else:
            # Relative path - join with codebase_path
            file_path = os.path.join(codebase_path, file_info["path"])

        logger.info(
            f"Analyzing file: {file_info['name']} ({file_info['language']}) at path: {file_path}"
        )

        # Read file content
        file_content = read_code_file_content(file_path)
        if not file_content:
            logger.warning(f"Skipping empty file: {file_info['name']}")
            continue

        # Generate metadata using AI
        file_metadata = generate_file_metadata_with_ai(
            file_content, file_info["name"], file_info["language"], ai_client
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
        description="Generate metadata for codebase (any programming language)"
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
