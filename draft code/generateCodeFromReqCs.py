import sys
import os
import csv
import re

# Add root directory and src directory to path to import modules
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(src_dir)

from src.CheckCodeRequirements.adapters.readRequirementsFromCSV import read_requirements_csv
from CodeManagement.readCode import list_code_files
from config import Config
from src.AIBrain.ai import AzureOpenAIClient

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


def extract_cs_from_ai_response(ai_response):
    match = re.search(r"```cs\s*(.*?)```", ai_response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ai_response.strip()


def inject_cs_code(file_path, new_code):
    try:
        current_content = read_file_content(file_path)

        # Inject before last closing brace if exists
        match = re.search(r"\n}\s*$", current_content)
        injection_pos = match.start() if match else len(current_content)

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
    target_cs_file = os.path.join(codeBase, "code.cs")

    print(f"📁 Reading requirements from: {requirements}")
    print(f"📁 Reading implemented from: {implementedRequirements}")
    print(f"📁 Code base location: {codeBase}")
    print(f"🎯 Target file: {target_cs_file}")



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
        You are a C# code generator. Generate a C# method that implements the following requirement:

        Requirement ID: {req_id}
        Description: {desc}

        Requirements:
        1. Generate ONLY the method definition with proper XML documentation comments
        2. Include parameter validation if needed
        3. Add proper error handling (e.g., exceptions)
        4. Follow C# best practices
        5. Use descriptive method names based on the requirement

        Example format:
        /// <summary>
        /// Description of what the method does.
        /// </summary>
        /// <param name="param1">Description</param>
        /// <param name="param2">Description</param>
        /// <returns>Description of return value</returns>
        public static ReturnType MethodName(Type1 param1, Type2 param2)
        {{
            // Implementation
        }}

        Generate the function:
        """

        print("🤖 Generating code with AI...")

        # Call AI to generate code
        try:
            result = ai_client.ask_question(
                question=prompt,
                system_prompt="You are a C# code generator. Generate clean, efficient, and well-documented C# code.",
                max_tokens=1000,
                temperature=0.1,
            )

            if result["status"] == "success":
                ai_response = result["answer"]
                print(
                    f"✅ AI generated code (tokens used: {result['usage']['total_tokens']})"
                )

                # Extract function code
                function_code = extract_cs_from_ai_response(ai_response)
                print("📄 Generated function:")
                print("-" * 40)
                print(function_code)
                print("-" * 40)

                # Inject code into target file
                print("💉 Injecting code into target file...")
                if inject_cs_code(target_cs_file, function_code):
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
    print(f"📄 Check {target_cs_file} for the generated functions")
    print(f"📄 Check {implementedRequirements} for updated requirements")


if __name__ == "__main__":
    generateCodeFromRequirements()


# Example usage:
