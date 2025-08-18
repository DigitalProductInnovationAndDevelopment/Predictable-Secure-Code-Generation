#!/usr/bin/env python3
"""
Example Usage of RequirementImplementationManager

This script demonstrates how to use the RequirementImplementationManager
class programmatically to implement requirements.
"""

import os
import sys
import json
from typing import Dict, Any

# Path setup for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..", "..", "..")
handle_generic_v2_path = os.path.join(project_root, "HandleGenericV2")
sys.path.insert(0, handle_generic_v2_path)

from config import Config
from s2_codeGeneration.core.implementMissingRequirements import (
    RequirementImplementationManager,
)


def implement_multiple_requirements(count: int = 3) -> Dict[str, Any]:
    """
    Implement multiple requirements in sequence.

    Args:
        count: Number of requirements to implement

    Returns:
        Dictionary with implementation results
    """
    try:
        print(f"🚀 Implementing {count} requirements...")
        print("=" * 50)

        # Initialize the manager
        config = Config()
        manager = RequirementImplementationManager(config)

        results = []

        for i in range(count):
            print(f"\n📋 Implementation {i+1}/{count}")
            print("-" * 30)

            # Get current status
            status = manager.get_implementation_status()
            print(f"Current Status: {status['current_status']}")
            print(f"Total Implementations: {status['total_implementations']}")

            # Implement next requirement
            result = manager.implement_next_requirement()

            if result["status"] == "success":
                print(f"✅ {result['message']}")
                results.append(
                    {
                        "iteration": i + 1,
                        "status": "success",
                        "requirement_id": result.get("requirement_id"),
                        "message": result.get("message"),
                    }
                )
            elif result["status"] == "no_requirements":
                print(f"🎉 {result['message']}")
                results.append(
                    {
                        "iteration": i + 1,
                        "status": "no_requirements",
                        "message": result.get("message"),
                    }
                )
                break
            else:
                print(f"❌ {result['message']}")
                results.append(
                    {
                        "iteration": i + 1,
                        "status": "error",
                        "error": result.get("error"),
                        "message": result.get("message"),
                    }
                )

        # Final status
        final_status = manager.get_implementation_status()
        print(f"\n📊 Final Implementation Status:")
        print(f"   Total Implementations: {final_status['total_implementations']}")
        print(f"   Successful: {final_status['successful_implementations']}")
        print(f"   Failed: {final_status['failed_implementations']}")
        print(f"   Current Status: {final_status['current_status']}")

        return {
            "total_iterations": len(results),
            "results": results,
            "final_status": final_status,
        }

    except Exception as e:
        print(f"❌ Error in implement_multiple_requirements: {e}")
        return {"error": str(e)}


def get_implementation_summary() -> Dict[str, Any]:
    """Get a summary of all implementations."""
    try:
        config = Config()
        manager = RequirementImplementationManager(config)

        status = manager.get_implementation_status()

        # Load detailed log
        with open(manager.implementation_log_file, "r", encoding="utf-8") as f:
            log_data = json.load(f)

        implementations = log_data.get("implementations", [])

        # Analyze implementations
        analysis = {
            "total_implementations": len(implementations),
            "successful": len(
                [impl for impl in implementations if impl.get("status") == "completed"]
            ),
            "failed": len(
                [impl for impl in implementations if impl.get("status") == "failed"]
            ),
            "in_progress": len(
                [
                    impl
                    for impl in implementations
                    if impl.get("status") == "in_progress"
                ]
            ),
            "requirements_implemented": [
                impl.get("requirement_id")
                for impl in implementations
                if impl.get("status") == "completed"
            ],
            "average_steps_per_implementation": 0,
            "total_errors": 0,
        }

        if implementations:
            total_steps = sum(
                len(impl.get("steps_completed", [])) for impl in implementations
            )
            analysis["average_steps_per_implementation"] = round(
                total_steps / len(implementations), 2
            )

            total_errors = sum(len(impl.get("errors", [])) for impl in implementations)
            analysis["total_errors"] = total_errors

        return {
            "status": status,
            "analysis": analysis,
            "log_file": manager.implementation_log_file,
        }

    except Exception as e:
        print(f"❌ Error getting implementation summary: {e}")
        return {"error": str(e)}


def reset_implementations():
    """Reset the implementation log."""
    try:
        config = Config()
        manager = RequirementImplementationManager(config)

        print("🔄 Resetting implementation log...")
        manager.reset_implementation_log()
        print("✅ Implementation log reset successfully")

    except Exception as e:
        print(f"❌ Error resetting implementations: {e}")


def main():
    """Main function demonstrating various usage patterns."""
    print("🔧 RequirementImplementationManager - Example Usage")
    print("=" * 60)

    while True:
        print("\n📋 Choose an option:")
        print("1. Implement next requirement")
        print("2. Implement multiple requirements")
        print("3. Show implementation summary")
        print("4. Reset implementations")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            # Implement single requirement
            config = Config()
            manager = RequirementImplementationManager(config)
            result = manager.implement_next_requirement()

            if result["status"] == "success":
                print(f"✅ {result['message']}")
            elif result["status"] == "no_requirements":
                print(f"🎉 {result['message']}")
            else:
                print(f"❌ {result['message']}")

        elif choice == "2":
            # Implement multiple requirements
            try:
                count = int(input("Enter number of requirements to implement: "))
                if count > 0:
                    result = implement_multiple_requirements(count)
                    print(
                        f"\n📊 Implementation completed: {result['total_iterations']} iterations"
                    )
                else:
                    print("❌ Please enter a positive number")
            except ValueError:
                print("❌ Please enter a valid number")

        elif choice == "3":
            # Show summary
            summary = get_implementation_summary()
            if "error" not in summary:
                print(f"\n📊 Implementation Summary:")
                print(f"   Total: {summary['analysis']['total_implementations']}")
                print(f"   Successful: {summary['analysis']['successful']}")
                print(f"   Failed: {summary['analysis']['failed']}")
                print(
                    f"   Average Steps: {summary['analysis']['average_steps_per_implementation']}"
                )
                print(f"   Total Errors: {summary['analysis']['total_errors']}")
                print(
                    f"   Requirements: {', '.join(summary['analysis']['requirements_implemented'])}"
                )
            else:
                print(f"❌ Error: {summary['error']}")

        elif choice == "4":
            # Reset
            confirm = (
                input("Are you sure you want to reset all implementations? (y/N): ")
                .strip()
                .lower()
            )
            if confirm == "y":
                reset_implementations()
            else:
                print("Reset cancelled")

        elif choice == "5":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main()
