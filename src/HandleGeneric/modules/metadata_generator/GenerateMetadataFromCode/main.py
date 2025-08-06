#!/usr/bin/env python3
"""
Main CLI script for generating metadata from code projects.
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.dirname(parent_dir)
sys.path.insert(0, src_dir)

from core.generator import MetadataGenerator
from utils.config import Config
from utils.helpers import PathHelper

# Import AI client if available
try:
    from AIBrain.ai import AzureOpenAIClient

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class MetadataEnhancer:
    """Enhances metadata using AI capabilities."""

    def __init__(self):
        """Initialize the enhancer with AI client if available."""
        self.ai_client = None
        if AI_AVAILABLE:
            try:
                self.ai_client = AzureOpenAIClient()
            except Exception as e:
                print(f"Warning: Could not initialize AI client: {e}")

    def enhance_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance metadata with AI-generated insights.

        Args:
            metadata: Original metadata dictionary

        Returns:
            Enhanced metadata with AI insights
        """
        if not self.ai_client:
            print("AI enhancement not available")
            return metadata

        print("Enhancing metadata with AI insights...")

        try:
            # Create a summary of the codebase for AI analysis
            summary = self._create_codebase_summary(metadata)

            # Ask AI for insights
            prompt = f"""
            Analyze this Python codebase metadata and provide insights:

            {json.dumps(summary, indent=2)}

            Please provide:
            1. A brief description of what this codebase does
            2. Key architectural patterns used
            3. Potential areas for improvement
            4. Code quality assessment

            Respond in JSON format with keys: description, patterns, improvements, quality_assessment
            """

            result = self.ai_client.ask_question(prompt, max_tokens=1000)

            if result["status"] == "success":
                try:
                    ai_insights = json.loads(result["answer"])
                    metadata["ai_insights"] = ai_insights
                    print("AI insights added successfully")
                except json.JSONDecodeError:
                    # If AI doesn't return valid JSON, store as text
                    metadata["ai_insights"] = {
                        "analysis": result["answer"],
                        "note": "AI response was not in JSON format",
                    }
                    print("AI insights added (as text)")
            else:
                print(f"AI analysis failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"Error during AI enhancement: {e}")

        return metadata

    def _create_codebase_summary(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summarized version of metadata for AI analysis.

        Args:
            metadata: Full metadata dictionary

        Returns:
            Summarized metadata for AI analysis
        """
        summary = {
            "total_files": metadata.get("metrics", {}).get("total_files", 0),
            "total_functions": metadata.get("metrics", {}).get("total_functions", 0),
            "total_classes": metadata.get("metrics", {}).get("total_classes", 0),
            "entry_points": metadata.get("entry_points", []),
            "external_dependencies": metadata.get("dependencies", {}).get(
                "external_dependencies", []
            ),
            "file_overview": [],
        }

        # Add simplified file information
        for file_data in metadata.get("files", [])[:10]:  # Limit to first 10 files
            file_summary = {
                "path": file_data["path"],
                "functions": [f["name"] for f in file_data.get("functions", [])],
                "classes": [c["name"] for c in file_data.get("classes", [])],
                "imports": file_data.get("imports", [])[:5],  # Limit imports
            }
            summary["file_overview"].append(file_summary)

        return summary


def create_config_from_args(args) -> Config:
    """
    Create configuration from command line arguments.

    Args:
        args: Parsed command line arguments

    Returns:
        Configuration object
    """
    config = Config()

    if args.include_private:
        config.include_private_methods = True

    if args.exclude_docstrings:
        config.extract_docstrings = False

    if args.exclude_type_hints:
        config.extract_type_hints = False

    if args.exclude_decorators:
        config.extract_decorators = False

    if args.log_level:
        config.log_level = args.log_level.upper()

    if args.output_filename:
        config.output_filename = args.output_filename

    return config


def main():
    """Main function for the CLI."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive metadata from Python code projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/project /output/dir
  %(prog)s /path/to/project /output/dir --ai-enhance
  %(prog)s /path/to/file.py /output/dir --single-file
  %(prog)s /path/to/project /output/dir --output-filename my_metadata.json
        """,
    )

    # Required arguments
    parser.add_argument(
        "project_path", help="Path to the project directory or Python file"
    )
    parser.add_argument("output_path", help="Path to save the metadata.json file")

    # Optional arguments
    parser.add_argument(
        "--output-filename",
        "-o",
        help="Name of the output file (default: metadata.json)",
    )
    parser.add_argument(
        "--single-file",
        "-f",
        action="store_true",
        help="Generate metadata for a single Python file",
    )
    parser.add_argument(
        "--ai-enhance",
        "-ai",
        action="store_true",
        help="Enhance metadata with AI insights (requires AI configuration)",
    )

    # Configuration options
    parser.add_argument(
        "--include-private",
        action="store_true",
        help="Include private methods and classes (starting with _)",
    )
    parser.add_argument(
        "--exclude-docstrings", action="store_true", help="Don't extract docstrings"
    )
    parser.add_argument(
        "--exclude-type-hints", action="store_true", help="Don't extract type hints"
    )
    parser.add_argument(
        "--exclude-decorators", action="store_true", help="Don't extract decorators"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )
    parser.add_argument("--config-file", help="Path to JSON configuration file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually generating metadata",
    )

    args = parser.parse_args()

    try:
        # Load configuration
        if args.config_file:
            config_path = Path(args.config_file)
            if config_path.exists():
                with open(config_path, "r") as f:
                    config_dict = json.load(f)
                config = Config.from_dict(config_dict)
            else:
                print(f"Warning: Config file not found: {config_path}")
                config = create_config_from_args(args)
        else:
            config = create_config_from_args(args)

        # Show configuration if dry run
        if args.dry_run:
            print("Configuration:")
            print(json.dumps(config.to_dict(), indent=2))
            print(f"\nWould process: {args.project_path}")
            print(f"Would save to: {args.output_path}")
            if args.single_file:
                print("Mode: Single file")
            else:
                print("Mode: Project directory")
            if args.ai_enhance:
                print("AI enhancement: Enabled")
            return

        # Initialize generator
        generator = MetadataGenerator(config)

        # Generate metadata
        if args.single_file:
            metadata = generator.generate_from_single_file(
                args.project_path, args.output_path, args.output_filename
            )
        else:
            metadata = generator.generate_metadata(
                args.project_path, args.output_path, args.output_filename
            )

        # AI enhancement if requested
        if args.ai_enhance:
            if not AI_AVAILABLE:
                print("Warning: AI enhancement requested but AI module not available")
            else:
                enhancer = MetadataEnhancer()
                metadata = enhancer.enhance_metadata(metadata)

                # Save enhanced metadata
                output_filename = args.output_filename or config.output_filename
                output_file_path = (
                    PathHelper.normalize_path(args.output_path) / output_filename
                )

                file_helper = generator.file_helper
                file_helper.save_json(metadata, output_file_path)

        # Print summary
        print("\n" + "=" * 60)
        print("METADATA GENERATION COMPLETE")
        print("=" * 60)
        print(f"Project: {args.project_path}")
        print(f"Output: {args.output_path}")
        print(f"Files processed: {len(metadata.get('files', []))}")
        print(
            f"Functions found: {metadata.get('metrics', {}).get('total_functions', 0)}"
        )
        print(f"Classes found: {metadata.get('metrics', {}).get('total_classes', 0)}")
        print(f"Entry points: {len(metadata.get('entry_points', []))}")

        if args.ai_enhance and "ai_insights" in metadata:
            print("AI enhancement: ✓ Completed")

        print("=" * 60)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
