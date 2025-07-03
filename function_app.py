import azure.functions as func
import logging
import json
from datetime import datetime
from CodeFromRequirements.requirements_checker import RequirementsChecker
from CodeFromRequirements.code_analyzer import CodeAnalyzer
from CodeFromRequirements.ai_code_editor import AICodeEditor
from CodeFromRequirements.code_validator import CodeValidator
from CodeFromRequirements.metadata_manager import MetadataManager
from config import Config

app = func.FunctionApp()


@app.timer_trigger(schedule="0 0 9 * * *", arg_name="timer", run_on_startup=False)
def daily_code_update_trigger(timer: func.TimerRequest) -> None:
    """
    Daily trigger function that checks for requirement updates and processes them.
    Runs every day at 9:00 AM UTC (cron: 0 0 9 * * *)
    """
    logging.info(f"Daily code update trigger started at {datetime.now()}")

    try:
        # Initialize components
        req_checker = RequirementsChecker()
        code_analyzer = CodeAnalyzer()
        ai_editor = AICodeEditor()
        validator = CodeValidator()
        metadata_manager = MetadataManager()

        # Step 1: Check for requirement updates
        logging.info("Step 1: Checking for requirement updates...")
        has_new_requirements, new_requirements = req_checker.check_for_updates()

        if not has_new_requirements:
            logging.info("No new requirements found. System is up to date.")
            metadata_manager.log_status("up_to_date", "No new requirements found")
            return

        logging.info(f"Found {len(new_requirements)} new requirement(s)")

        # Step 2: Read code structure + metadata + new requirements
        logging.info("Step 2: Reading code structure and metadata...")
        code_structure = code_analyzer.analyze_codebase()
        current_metadata = metadata_manager.load_metadata()

        # Step 3: Identify required changes
        logging.info("Step 3: Identifying required changes...")
        required_changes = code_analyzer.identify_changes(
            code_structure, current_metadata, new_requirements
        )

        # Step 4: Process each requirement
        for requirement in new_requirements:
            logging.info(
                f"Processing requirement: {requirement.get('name', 'Unknown')}"
            )

            success = process_requirement(
                requirement, required_changes, ai_editor, validator, metadata_manager
            )

            if success:
                logging.info(
                    f"Successfully processed requirement: {requirement.get('name')}"
                )
            else:
                logging.error(
                    f"Failed to process requirement: {requirement.get('name')}"
                )

        # Update metadata with processing results
        metadata_manager.update_processed_requirements(new_requirements)
        logging.info("Daily code update process completed")

    except Exception as e:
        logging.error(f"Error in daily code update process: {str(e)}")
        metadata_manager.log_status("error", str(e))


def process_requirement(
    requirement, required_changes, ai_editor, validator, metadata_manager
):
    """Process a single requirement with retry logic"""
    max_retries = 3

    for attempt in range(max_retries):
        try:
            logging.info(
                f"Attempt {attempt + 1}/{max_retries} for requirement: {requirement.get('name')}"
            )

            # Step 4: Edit scripts with AI
            logging.info("Step 4: Editing scripts with AI...")
            changes_made = ai_editor.apply_changes(requirement, required_changes)

            # Step 5: Run code validation
            logging.info("Step 5: Running code validation...")
            validation_result = validator.validate_changes(changes_made)

            if validation_result.is_valid:
                logging.info("Code validation passed")
                metadata_manager.log_status(
                    "success",
                    f"Requirement {requirement.get('name')} processed successfully",
                )
                return True
            else:
                logging.warning(f"Code validation failed: {validation_result.errors}")
                if attempt == max_retries - 1:
                    logging.error(f"Failed after {max_retries} attempts")
                    metadata_manager.log_status(
                        "failed", f"Validation failed after {max_retries} attempts"
                    )
                    return False

        except Exception as e:
            logging.error(f"Error in attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                metadata_manager.log_status(
                    "failed", f"Exception after {max_retries} attempts: {str(e)}"
                )
                return False

    return False


@app.route(route="status", methods=["GET"])
def get_status(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP endpoint to check the status of the automated code update system"""
    try:
        metadata_manager = MetadataManager()
        status = metadata_manager.get_latest_status()

        return func.HttpResponse(
            json.dumps(status, indent=2),
            status_code=200,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"},
        )


@app.route(route="trigger-manual", methods=["POST"])
def manual_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """Manual trigger endpoint for testing purposes"""
    try:
        logging.info("Manual trigger initiated")
        daily_code_update_trigger(None)

        return func.HttpResponse(
            json.dumps({"status": "Manual trigger completed successfully"}),
            status_code=200,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"},
        )
