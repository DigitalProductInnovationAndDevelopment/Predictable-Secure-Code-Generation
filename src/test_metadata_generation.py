#!/usr/bin/env python3
"""
Simple test script for metadata generation.
"""

import sys
import json
from pathlib import Path

# Add the HandleGeneric directory to the path
sys.path.insert(0, str(Path(__file__).parent / "HandleGeneric"))


def test_metadata_generation():
    """Test metadata generation with PythonExample."""

    # Define paths
    input_path = Path("../input/PythonExample/code")
    output_path = Path("../output/PythonExample/environment")

    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"🔍 Generating metadata for: {input_path}")
    print(f"📁 Output directory: {output_path}")

    # Simple metadata generation
    metadata = {
        "project_info": {
            "project_path": str(input_path),
            "total_files": 0,
            "main_language": "python",
            "generation_time": 0.0,
        },
        "languages": ["python", "java"],
        "language_summaries": {
            "python": {"file_count": 0, "total_lines": 0, "functions": 0, "classes": 0},
            "java": {"file_count": 0, "total_lines": 0, "functions": 0, "classes": 0},
        },
        "files": [],
    }

    # Count files and analyze
    if input_path.exists():
        for file_path in input_path.rglob("*"):
            if file_path.is_file():
                metadata["project_info"]["total_files"] += 1

                # Determine language based on extension
                if file_path.suffix.lower() in [".py", ".pyi", ".pyw"]:
                    lang = "python"
                elif file_path.suffix.lower() in [".java"]:
                    lang = "java"
                else:
                    continue

                # Count lines
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        line_count = len(lines)

                        if lang == "python":
                            metadata["language_summaries"]["python"][
                                "total_lines"
                            ] += line_count
                            metadata["language_summaries"]["python"]["file_count"] += 1
                        elif lang == "java":
                            metadata["language_summaries"]["java"][
                                "total_lines"
                            ] += line_count
                            metadata["language_summaries"]["java"]["file_count"] += 1

                        # Add file info
                        metadata["files"].append(
                            {
                                "path": str(file_path.relative_to(input_path)),
                                "language": lang,
                                "lines": line_count,
                                "size": file_path.stat().st_size,
                            }
                        )
                except Exception as e:
                    print(f"⚠️  Error reading {file_path}: {e}")

    # Save metadata
    output_file = output_path / "metadata.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ Metadata generation completed!")
    print(f"📁 Output saved to: {output_file}")
    print(f"📊 Project summary:")
    print(f"   - Total files processed: {metadata['project_info']['total_files']}")
    print(f"   - Languages detected: {', '.join(metadata['languages'])}")
    print(f"   - Main language: {metadata['project_info']['main_language']}")

    # Show detailed breakdown
    print(f"\n📈 Detailed breakdown:")
    for lang, summary in metadata.get("language_summaries", {}).items():
        if summary["file_count"] > 0:
            print(
                f"   {lang}: {summary['file_count']} files, {summary['total_lines']} lines"
            )

    return metadata


if __name__ == "__main__":
    test_metadata_generation()
