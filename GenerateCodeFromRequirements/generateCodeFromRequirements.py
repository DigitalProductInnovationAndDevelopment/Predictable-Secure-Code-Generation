import sys
import os
import csv
import re

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CheckCodeRequirements.adapters.readRequirementsFromCSV import read_requirements_csv
from CodeManagement.readCode import list_code_files
from config import Config
from ai import AzureOpenAIClient

# Create config instance
config = Config()


def read_file_content(file_path):
    """Read the content of a file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""


def write_file_content(file_path, content):
    """Write content to a file"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")
        return False


def update_implemented_requirements(file_path, req_id, description):
    """Add a new requirement to the implemented requirements CSV"""
    try:
        # Read existing requirements
        existing_reqs = {}
        if os.path.exists(file_path):
            existing_reqs = read_requirements_csv(file_path)

        # Add new requirement
        existing_reqs[req_id] = description

        # Write back to CSV
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "description"])
            for req_id, desc in existing_reqs.items():
                writer.writerow([req_id, desc])

        print(f"✅ Updated {file_path} with {req_id}")
        return True
    except Exception as e:
        print(f"❌ Error updating implemented requirements: {e}")
        return False


def extract_function_from_ai_response(ai_response):
    """Extract Python function code from AI response"""
    # Look for code blocks first
    code_block_pattern = r"```python\s*(.*?)\s*```"
    match = re.search(code_block_pattern, ai_response, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Look for function definitions
    function_pattern = r"(def\s+\w+\(.*?\):.*?)(?=\n\n|def\s+|\Z)"
    match = re.search(function_pattern, ai_response, re.DOTALL)
    if match:
        return match.group(1).strip()

    # If no specific pattern found, return the response (may need manual cleanup)
    return ai_response.strip()


def inject_code_into_file(file_path, new_code):
    """Inject new code into the target file before the main execution block"""
    try:
        current_content = read_file_content(file_path)

        # Find the position to inject (before "# Example usage" or "__main__")
        injection_patterns = [
            r"\n# Example usage",
            r'\nif __name__ == "__main__":',
            r"\n\n$",  # End of file
        ]

        injection_pos = len(current_content)
        for pattern in injection_patterns:
            match = re.search(pattern, current_content)
            if match:
                injection_pos = match.start()
                break

        # Inject the new code
        new_content = (
            current_content[:injection_pos]
            + "\n\n"
            + new_code
            + "\n"
            + current_content[injection_pos:]
        )

        if write_file_content(file_path, new_content):
            print(f"✅ Successfully injected code into {file_path}")
            return True
        else:
            print(f"❌ Failed to write to {file_path}")
            return False

    except Exception as e:
        print(f"❌ Error injecting code: {e}")
        return False


def generateCodeFromRequirements():
    print("🚀 Starting Code Generation from Requirements")
    print("=" * 60)

    # Initialize AI client
    try:
        ai_client = AzureOpenAIClient(config)
        print("✅ AI Client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize AI client: {e}")
        return

    # Get file paths
    implementedRequirements = config.IMPLEMENTED_REQUIREMENTS_FILE
    requirements = config.REQUIREMENTS_FILE
    codeBase = config.CODEBASE_ROOT

    print(f"📁 Reading requirements from: {requirements}")
    print(f"📁 Reading implemented from: {implementedRequirements}")
    print(f"📁 Code base location: {codeBase}")

    # List code files
    codeFiles = list_code_files(codeBase)
    target_code_file = os.path.join(codeBase, "code.py")
    print(f"🎯 Target code file: {target_code_file}")

    # Read current and new requirements
    try:
        current = read_requirements_csv(implementedRequirements)
        new = read_requirements_csv(requirements)
        print(f"📊 Current implemented requirements: {len(current)}")
        print(f"📊 Total requirements: {len(new)}")
    except Exception as e:
        print(f"❌ Error reading requirements: {e}")
        return

    # Identify new and modified requirements
    added = {}
    modified = {}
    for req_id, desc in new.items():
        if req_id not in current:
            added[req_id] = desc
        elif current[req_id] != desc:
            modified[req_id] = desc

    # Combine all tasks
    tasks = {**added, **modified}

    print(
        f"\n📋 Found {len(added)} new requirements and {len(modified)} modified requirements"
    )

    if added:
        print("\n🆕 New requirements to implement:")
        for req_id, desc in added.items():
            print(f"  • {req_id}: {desc}")

    if modified:
        print("\n🔄 Requirements to modify:")
        for req_id, desc in modified.items():
            print(f"  • {req_id}: {desc}")

    if not tasks:
        print("\n✅ All requirements are already implemented!")
        return

    # Process each task
    print(f"\n🔨 Starting implementation of {len(tasks)} requirement(s)")
    print("=" * 60)

    for i, (req_id, desc) in enumerate(tasks.items(), 1):
        print(f"\n📝 Step {i}/{len(tasks)}: Processing {req_id}")
        print(f"📋 Description: {desc}")

        # Prepare AI prompt
        prompt = f"""
You are a Python code generator. Generate a Python function that implements the following requirement:

Requirement ID: {req_id}
Description: {desc}

Requirements:
1. Generate ONLY the function definition with proper docstring
2. Include parameter validation if needed
3. Add proper error handling
4. Follow Python best practices
5. Make the function name descriptive based on the requirement

Current existing functions in the codebase include: addition, subtraction

Example format:
```python
def function_name(param1, param2):
    \"\"\"
    Description of what the function does.
    
    Args:
        param1 (type): Description
        param2 (type): Description
    
    Returns:
        type: Description of return value
    \"\"\"
    # Implementation here
    return result
```

Generate the function:
"""

        print("🤖 Generating code with AI...")

        # Call AI to generate code
        try:
            result = ai_client.ask_question(
                question=prompt,
                system_prompt="You are a Python code generator. Generate clean, efficient, and well-documented code.",
                max_tokens=1000,
                temperature=0.1,
            )

            if result["status"] == "success":
                ai_response = result["answer"]
                print(
                    f"✅ AI generated code (tokens used: {result['usage']['total_tokens']})"
                )

                # Extract function code
                function_code = extract_function_from_ai_response(ai_response)
                print("📄 Generated function:")
                print("-" * 40)
                print(function_code)
                print("-" * 40)

                # Inject code into target file
                print("💉 Injecting code into target file...")
                if inject_code_into_file(target_code_file, function_code):
                    print("✅ Code injection successful")

                    # Update implemented requirements
                    print("📝 Updating implemented requirements...")
                    if update_implemented_requirements(
                        implementedRequirements, req_id, desc
                    ):
                        print(f"✅ Requirement {req_id} completed successfully!")
                    else:
                        print(
                            f"⚠️  Code injected but failed to update requirements file"
                        )
                else:
                    print(f"❌ Failed to inject code for {req_id}")

            else:
                print(
                    f"❌ AI failed to generate code: {result.get('error', 'Unknown error')}"
                )

        except Exception as e:
            print(f"❌ Error processing {req_id}: {e}")

        print("-" * 60)

    print(f"\n🎉 Code generation process completed!")
    print(f"📄 Check {target_code_file} for the generated functions")
    print(f"📄 Check {implementedRequirements} for updated requirements")


if __name__ == "__main__":
    generateCodeFromRequirements()


# Example usage:
