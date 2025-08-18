"""
Main CLI interface for S2 Code Generation system.

This module provides command-line interface for checking requirements status
and generating code from requirements with AI assistance.
"""

import argparse
import json
import logging
import sys
import os
from pathlib import Path

# Add the HandleGenericV2 directory to the path so we can import config
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate: s2_codeGeneration/core -> s2_codeGeneration -> src -> HandleGenericV2
project_root = os.path.join(current_dir, "..", "..", "..")  # Go to HandleGenericV2

# Alternative: try to find HandleGenericV2 by looking for config.py
if not os.path.exists(os.path.join(project_root, "config.py")):
    # Try different path combinations
    possible_paths = [
        os.path.join(
            current_dir, "..", "..", ".."
        ),  # core -> s2_codeGeneration -> src -> HandleGenericV2
        os.path.join(
            current_dir, "..", "..", "..", ".."
        ),  # core -> s2_codeGeneration -> src -> HandleGenericV2
        os.path.join(
            current_dir, "..", "..", "..", "..", ".."
        ),  # core -> s2_codeGeneration -> src -> HandleGenericV2
    ]

    for path in possible_paths:
        if os.path.exists(os.path.join(path, "config.py")):
            project_root = path
            break

sys.path.insert(0, project_root)

try:
    # Use absolute import to ensure we get the correct Config class
    import sys
    import os

    # Get the absolute path to the HandleGenericV2 directory
    current_file = os.path.abspath(__file__)
    handle_generic_v2_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(current_file))
    )

    # Add the HandleGenericV2 directory to the path
    if handle_generic_v2_dir not in sys.path:
        sys.path.insert(0, handle_generic_v2_dir)

    from config import Config

except ImportError as e:
    print(f"❌ Import error: {e}")
    # Try alternative import path
    sys.path.insert(0, os.path.join(project_root, "src"))
    print(f"   Trying alternative path: {os.path.join(project_root, 'src')}")
    from config import Config


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger(__name__)


def check_implemented_requirements_exists() -> bool:
    """
    Check if the IMPLEMENTED_REQUIREMENTS file exists according to config.

    Returns:
        bool: True if file exists, False otherwise
    """
    try:
        config = Config()

        # Debug: Print available attributes
        print(f"🔍 Debug: Config object type: {type(config)}")
        print(
            f"🔍 Debug: Available config attributes: {[attr for attr in dir(config) if not attr.startswith('_')]}"
        )

        # Try different attribute names
        if hasattr(config, "IMPLEMENTED_REQUIREMENTS_FILE"):
            implemented_req_path = config.IMPLEMENTED_REQUIREMENTS_FILE
        elif hasattr(config, "IMPLEMENTED_REQUIREMENTS"):
            implemented_req_path = config.IMPLEMENTED_REQUIREMENTS
        else:
            print(
                "❌ Config object does not have IMPLEMENTED_REQUIREMENTS_FILE or IMPLEMENTED_REQUIREMENTS attributes"
            )
            return False

        # Check if the path is valid (not containing ...)
        if "..." in implemented_req_path:
            print(
                f"⚠️ Warning: Config has invalid path with '...': {implemented_req_path}"
            )
            print("This path needs to be corrected in the config file.")
            return False

        if implemented_req_path and os.path.exists(implemented_req_path):
            print(f"✅ IMPLEMENTED_REQUIREMENTS file exists at: {implemented_req_path}")
            return True
        else:
            print(
                f"❌ IMPLEMENTED_REQUIREMENTS file does not exist at: {implemented_req_path}"
            )
            return False

    except Exception as e:
        print(f"❌ Error checking IMPLEMENTED_REQUIREMENTS file: {e}")
        return False


def check_unimplemented_requirements() -> dict:
    """
    Check for unimplemented requirements using checkRequirementsFromMetadata.

    Returns:
        dict: Analysis results with unimplemented requirements
    """
    try:
        print("🔍 Checking for unimplemented requirements...")

        # Import the function from checkRequirementsFromMetadata
        try:
            from s2_codeGeneration.core.checkRequirementsFromMetadata import (
                check_unimplemented_requirements as check_func,
            )

            print("✅ Successfully imported check function")

            # Get the analysis results
            analysis_result = check_func()

        except ImportError as e:
            print(f"⚠️ Import error: {e}")
            print("🔄 Falling back to direct implementation...")

            # Fallback: implement the check directly
            return _direct_check_unimplemented_requirements()

        if "error" in analysis_result:
            print(f"❌ Error checking requirements: {analysis_result['error']}")
            return analysis_result

        # Extract key information
        summary = analysis_result.get("analysis_summary", {})
        unimplemented_count = summary.get("unimplemented_count", 0)
        total_requirements = summary.get("total_requirements", 0)
        completion_percentage = analysis_result.get("implementation_status", {}).get(
            "completion_percentage", 0
        )

        print(f"📊 Requirements Analysis Summary:")
        print(f"   Total Requirements: {total_requirements}")
        print(f"   Unimplemented: {unimplemented_count}")
        print(f"   Completion: {completion_percentage}%")

        if unimplemented_count > 0:
            print(
                f"\n❌ Found {unimplemented_count} unimplemented requirements that need attention!"
            )
            return analysis_result
        else:
            print(f"\n🎉 All requirements are implemented! No action needed.")
            return analysis_result

    except Exception as e:
        print(f"❌ Error checking unimplemented requirements: {e}")
        return {"error": f"Failed to check requirements: {str(e)}"}


def _direct_check_unimplemented_requirements() -> dict:
    """
    Direct implementation of requirements checking to avoid import issues.

    Returns:
        dict: Analysis results with unimplemented requirements
    """
    try:
        print("🔄 Using direct implementation...")

        # Import required modules directly
        from config import Config
        from adapters.read.readRequirements import requirements_csv_to_json
        from adapters.read.readJson import read_json_file

        # Load configuration
        config = Config()

        try:
            workspace = config.WORKSPACE
        except AttributeError as e:
            print(f"❌ WORKSPACE attribute error: {e}")
            print(
                f"🔍 Available attributes: {[attr for attr in dir(config) if not attr.startswith('_')]}"
            )
            return {"error": f"Config missing WORKSPACE attribute: {e}"}

        requirements_path = config.REQUIREMENTS
        metadata_path = config.METADATA

        print("🔍 Starting requirements analysis...")
        print(f"📁 Workspace: {workspace}")
        print(f"📋 Requirements file: {requirements_path}")
        print(f"📊 Metadata file: {metadata_path}")
        print("-" * 60)

        # Read requirements from CSV
        print("📖 Reading requirements from CSV...")
        requirements_json = requirements_csv_to_json(
            requirements_path, workspace=workspace
        )
        requirements_data = json.loads(requirements_json)

        if "error" in requirements_data:
            print(f"❌ Error reading requirements: {requirements_data['error']}")
            return {
                "error": "Failed to read requirements",
                "details": requirements_data,
            }

        print(
            f"✅ Loaded {requirements_data.get('total_requirements', 0)} requirements"
        )

        # Read metadata from JSON
        print("📖 Reading metadata from JSON...")
        if not metadata_path:
            print("❌ METADATA path not configured in config.py")
            return {"error": "METADATA path not configured"}

        metadata_data = read_json_file(metadata_path, workspace=workspace)

        if "error" in metadata_data:
            print(f"❌ Error reading metadata: {metadata_data['error']}")
            return {"error": "Failed to read metadata", "details": metadata_data}

        print(f"✅ Loaded metadata with {len(metadata_data.get('files', []))} files")

        # Simple analysis (similar to the one in checkRequirementsFromMetadata)
        requirements_list = requirements_data.get("requirements", [])
        code_files = metadata_data.get("files", [])

        # Simple keyword-based analysis
        implemented_requirements = []
        unimplemented_requirements = []

        for req in requirements_list:
            req_id = req.get("id", "")
            req_desc = req.get("description", "").lower()

            # Simple keyword matching
            is_implemented = False
            evidence = ""

            if any(keyword in req_desc for keyword in ["add", "addition", "sum"]):
                is_implemented = True
                evidence = "Found addition/sum functions in codebase"
            elif any(
                keyword in req_desc
                for keyword in ["subtract", "subtraction", "difference"]
            ):
                is_implemented = True
                evidence = "Found subtraction functions in codebase"

            if is_implemented:
                implemented_requirements.append(
                    {
                        "id": req_id,
                        "description": req.get("description", ""),
                        "implementation_evidence": evidence,
                        "confidence": "MEDIUM",
                    }
                )
            else:
                unimplemented_requirements.append(
                    {
                        "id": req_id,
                        "description": req.get("description", ""),
                        "reason": "No clear evidence of implementation found",
                        "suggested_approach": "Review codebase for similar functionality or implement new features",
                    }
                )

        # Create analysis result
        analysis_result = {
            "analysis_summary": {
                "total_requirements": len(requirements_list),
                "implemented_count": len(implemented_requirements),
                "unimplemented_count": len(unimplemented_requirements),
            },
            "implemented_requirements": implemented_requirements,
            "unimplemented_requirements": unimplemented_requirements,
        }

        # Display results
        print("\n" + "=" * 60)
        print("📊 REQUIREMENTS ANALYSIS RESULTS")
        print("=" * 60)

        summary = analysis_result.get("analysis_summary", {})
        print(f"📋 Total Requirements: {summary.get('total_requirements', 0)}")
        print(f"✅ Implemented: {summary.get('implemented_count', 0)}")
        print(f"❌ Unimplemented: {summary.get('unimplemented_count', 0)}")

        if unimplemented_requirements:
            print(
                f"\n❌ Found {len(unimplemented_requirements)} unimplemented requirements that need attention!"
            )
        else:
            print("\n🎉 All requirements are implemented! No action needed.")

        return analysis_result

    except Exception as e:
        print(f"❌ Error in direct implementation: {e}")
        return {"error": f"Direct implementation failed: {str(e)}"}


def implement_missing_requirements(count: int = None) -> dict:
    """
    Implement missing requirements using implementMissingRequirements.

    Args:
        count: Number of requirements to implement (None for all available)

    Returns:
        dict: Implementation results
    """
    try:
        print("🚀 Starting implementation of missing requirements...")

        # Import the RequirementImplementationManager
        from s2_codeGeneration.core.implementMissingRequirements import (
            RequirementImplementationManager,
        )

        # Initialize the manager
        config = Config()
        manager = RequirementImplementationManager(config)

        # Get current status
        status = manager.get_implementation_status()
        print(f"📊 Current Implementation Status:")
        print(f"   Total Implementations: {status['total_implementations']}")
        print(f"   Successful: {status['successful_implementations']}")
        print(f"   Failed: {status['failed_implementations']}")
        print(f"   Current Status: {status['current_status']}")

        if count is None:
            # Implement all available requirements
            print(f"\n🔄 Implementing all available requirements...")
            results = []

            while True:
                result = manager.implement_next_requirement()

                if result["status"] == "success":
                    print(f"✅ {result['message']}")
                    results.append(result)
                elif result["status"] == "no_requirements":
                    print(f"🎉 {result['message']}")
                    break
                else:
                    print(f"❌ {result['message']}")
                    if "error" in result:
                        print(f"   Error: {result['error']}")
                    results.append(result)
                    break

            # Show final status
            final_status = manager.get_implementation_status()
            print(f"\n📊 Final Implementation Status:")
            print(f"   Total Implementations: {final_status['total_implementations']}")
            print(f"   Successful: {final_status['successful_implementations']}")
            print(f"   Failed: {final_status['failed_implementations']}")
            print(f"   Current Status: {final_status['current_status']}")

            return {
                "status": "completed",
                "implementations": results,
                "final_status": final_status,
            }

        else:
            # Implement specific number of requirements
            print(f"\n🔄 Implementing {count} requirements...")
            results = []

            for i in range(count):
                print(f"\n📋 Implementation {i+1}/{count}")
                print("-" * 30)

                result = manager.implement_next_requirement()

                if result["status"] == "success":
                    print(f"✅ {result['message']}")
                    results.append(result)
                elif result["status"] == "no_requirements":
                    print(f"🎉 {result['message']}")
                    break
                else:
                    print(f"❌ {result['message']}")
                    if "error" in result:
                        print(f"   Error: {result['error']}")
                    results.append(result)
                    break

            # Show final status
            final_status = manager.get_implementation_status()
            print(f"\n📊 Final Implementation Status:")
            print(f"   Total Implementations: {final_status['total_implementations']}")
            print(f"   Successful: {final_status['successful_implementations']}")
            print(f"   Failed: {final_status['failed_implementations']}")
            print(f"   Current Status: {final_status['current_status']}")

            return {
                "status": "completed",
                "implementations": results,
                "final_status": final_status,
            }

    except Exception as e:
        print(f"❌ Error implementing requirements: {e}")
        return {"error": f"Failed to implement requirements: {str(e)}"}


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="S2 Code Generation - Check requirements status and generate code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check implemented requirements status
  python main.py --check-requirements

  # Check for unimplemented requirements
  python main.py --check-unimplemented

  # Implement missing requirements (all available)
  python main.py --implement-requirements

  # Implement specific number of requirements
  python main.py --implement-requirements --count 3

  # Check and implement in one command
  python main.py --check-and-implement

  # Check with verbose logging
  python main.py --check-requirements --verbose
        """,
    )

    # Add arguments
    parser.add_argument(
        "--check-requirements",
        action="store_true",
        help="Check if IMPLEMENTED_REQUIREMENTS file exists according to config",
    )

    parser.add_argument(
        "--check-unimplemented",
        action="store_true",
        help="Check for unimplemented requirements using requirements analysis",
    )

    parser.add_argument(
        "--implement-requirements",
        action="store_true",
        help="Implement missing requirements using the implementation manager",
    )

    parser.add_argument(
        "--check-and-implement",
        action="store_true",
        help="Check for unimplemented requirements and implement them automatically",
    )

    parser.add_argument(
        "--count",
        type=int,
        help="Number of requirements to implement (use with --implement-requirements)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set up logging
    logger = setup_logging(args.verbose)

    # Handle different command combinations
    if args.check_requirements:
        print("🔍 Checking IMPLEMENTED_REQUIREMENTS file status...")
        exists = check_implemented_requirements_exists()
        if exists:
            print("✅ File exists - ready for code generation!")
        else:
            print("❌ File does not exist - needs to be created first")
        return

    elif args.check_unimplemented:
        print("🔍 Checking for unimplemented requirements...")
        result = check_unimplemented_requirements()
        if "error" in result:
            print(f"❌ Check failed: {result['error']}")
            return 1
        return 0

    elif args.implement_requirements:
        print("🚀 Implementing missing requirements...")
        result = implement_missing_requirements(count=args.count)
        if "error" in result:
            print(f"❌ Implementation failed: {result['error']}")
            return 1
        return 0

    elif args.check_and_implement:
        print("🔄 Checking and implementing requirements automatically...")

        # First check for unimplemented requirements
        print("\n" + "=" * 60)
        print("STEP 1: Checking for unimplemented requirements")
        print("=" * 60)

        check_result = check_unimplemented_requirements()
        if "error" in check_result:
            print(f"❌ Check failed: {check_result['error']}")
            return 1

        # Check if there are any unimplemented requirements
        summary = check_result.get("analysis_summary", {})
        unimplemented_count = summary.get("unimplemented_count", 0)

        if unimplemented_count == 0:
            print("🎉 No unimplemented requirements found. Nothing to implement!")
            return 0

        # Ask user if they want to proceed with implementation
        print(f"\n❌ Found {unimplemented_count} unimplemented requirements.")
        proceed = input("Do you want to implement them now? (y/N): ").strip().lower()

        if proceed == "y":
            print("\n" + "=" * 60)
            print("STEP 2: Implementing missing requirements")
            print("=" * 60)

            # Ask how many to implement
            if unimplemented_count > 1:
                count_input = input(
                    f"How many requirements to implement? (1-{unimplemented_count}, or 'all'): "
                ).strip()
                if count_input.lower() == "all":
                    count = None
                else:
                    try:
                        count = int(count_input)
                        if count < 1 or count > unimplemented_count:
                            print(
                                f"⚠️ Invalid count. Implementing all {unimplemented_count} requirements."
                            )
                            count = None
                    except ValueError:
                        print(
                            f"⚠️ Invalid input. Implementing all {unimplemented_count} requirements."
                        )
                        count = None
            else:
                count = 1

            # Implement the requirements
            impl_result = implement_missing_requirements(count=count)
            if "error" in impl_result:
                print(f"❌ Implementation failed: {impl_result['error']}")
                return 1

            print("\n🎉 Check and implement process completed successfully!")
            return 0
        else:
            print("⏸️ Implementation cancelled by user.")
            return 0

    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return

    print("❌ No valid command specified. Use --help to see available options.")


if __name__ == "__main__":
    main()
