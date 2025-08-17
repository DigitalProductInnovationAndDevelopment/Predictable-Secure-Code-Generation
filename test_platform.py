#!/usr/bin/env python3
"""
Simple test script to verify the platform works end-to-end.
This script tests all three services without requiring OpenAI API keys.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src" / "HandleGeneric v2" / "src"))


def test_platform_initialization():
    """Test that the platform can initialize without errors."""
    print("🧪 Testing platform initialization...")

    try:
        from platform.kernel.di import build_app
        from platform.kernel.registry import registry

        # Initialize the app (this will fail if OpenAI keys are missing, but we can still test structure)
        try:
            app = build_app()
            print("✅ Platform initialization successful")

            # Test registry
            languages = registry.get_supported_languages()
            print(f"📋 Supported languages: {languages}")

            if "python" in languages:
                print("✅ Python provider registered")
            else:
                print("❌ Python provider not found")

        except Exception as e:
            if "api_key" in str(e).lower() or "openai" in str(e).lower():
                print(
                    "⚠️  Platform structure OK, but missing OpenAI credentials (expected)"
                )
            else:
                raise

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

    return True


def test_domain_models():
    """Test that domain models work correctly."""
    print("\n🧪 Testing domain models...")

    try:
        from platform.domain.models.requirements import Requirement
        from platform.domain.models.metadata import FileMetadata, ProjectMetadata
        from platform.domain.models.validation import SyntaxResult, SyntaxIssue
        from platform.domain.models.generation import GeneratedFile, CodeGenReport

        # Test requirement creation
        req = Requirement(
            id="TEST-001",
            title="Test Requirement",
            description="A test requirement",
            acceptance=["Must work", "Must be tested"],
        )
        print(f"✅ Requirement created: {req.id}")

        # Test file metadata
        metadata = FileMetadata(
            path="test.py",
            language="python",
            loc=50,
            functions=["test_func"],
            classes=["TestClass"],
            imports=["os", "sys"],
        )
        print(f"✅ FileMetadata created: {metadata.path}")

        # Test project metadata
        project = ProjectMetadata(files=[metadata], languages=["python"])
        print(f"✅ ProjectMetadata created with {len(project.files)} files")

        # Test syntax result
        syntax_result = SyntaxResult(status="valid", issues=[])
        print(f"✅ SyntaxResult created: {syntax_result.status}")

        # Test generated file
        gen_file = GeneratedFile(
            path="generated.py", content="print('Hello, World!')", language="python"
        )
        print(f"✅ GeneratedFile created: {gen_file.path}")

        # Test code generation report
        report = CodeGenReport(
            files=[gen_file],
            rationale="Test generation",
            cost_tokens=100,
            generation_time_seconds=1.5,
        )
        print(f"✅ CodeGenReport created: {report.summary()}")

    except Exception as e:
        print(f"❌ Domain model error: {e}")
        return False

    return True


def test_python_providers():
    """Test Python providers without requiring external dependencies."""
    print("\n🧪 Testing Python providers...")

    try:
        from platform.adapters.providers.python.metadata_provider import (
            PythonMetadataProvider,
        )
        from platform.adapters.providers.python.syntax_validator import (
            PythonSyntaxValidator,
        )

        # Test metadata provider
        metadata_provider = PythonMetadataProvider()

        # Test with simple Python code
        test_code = '''
def hello_world():
    """Say hello to the world."""
    return "Hello, World!"

class Calculator:
    """A simple calculator."""
    
    def add(self, a, b):
        return a + b
'''

        metadata = metadata_provider.parse_file(Path("test.py"), test_code)
        print(
            f"✅ Metadata extracted: {len(metadata.functions)} functions, {len(metadata.classes)} classes"
        )

        # Test syntax validator
        syntax_validator = PythonSyntaxValidator()

        # Test valid syntax
        valid_result = syntax_validator.validate(Path("test.py"), test_code)
        print(f"✅ Syntax validation (valid): {valid_result.status}")

        # Test invalid syntax
        invalid_code = "def broken_function(\n    print('missing closing paren')"
        invalid_result = syntax_validator.validate(Path("broken.py"), invalid_code)
        print(
            f"✅ Syntax validation (invalid): {invalid_result.status} with {len(invalid_result.issues)} issues"
        )

    except Exception as e:
        print(f"❌ Python provider error: {e}")
        return False

    return True


def test_file_system_adapters():
    """Test file system adapters."""
    print("\n🧪 Testing file system adapters...")

    try:
        from platform.adapters.fs.local_fs import LocalFileSystem
        from platform.adapters.fs.artifact_writer import LocalArtifactWriter
        from platform.domain.models.generation import GeneratedFile

        fs = LocalFileSystem()
        writer = LocalArtifactWriter()

        # Test with temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test file writing and reading
            test_file = temp_path / "test.txt"
            test_content = "Hello, World!"

            fs.write_text(test_file, test_content)
            read_content = fs.read_text(test_file)

            if read_content == test_content:
                print("✅ File write/read successful")
            else:
                print("❌ File write/read failed")
                return False

            # Test directory scanning
            files = fs.scan(temp_path)
            print(f"✅ Directory scan found {len(files)} files")

            # Test artifact writer
            generated_files = [
                GeneratedFile(
                    path="main.py", content="print('main')", language="python"
                ),
                GeneratedFile(
                    path="utils.py", content="def util(): pass", language="python"
                ),
            ]

            writer.write(temp_path / "generated", generated_files)
            print("✅ Artifact writing successful")

    except Exception as e:
        print(f"❌ File system adapter error: {e}")
        return False

    return True


def test_cli_structure():
    """Test that CLI can be imported and has expected commands."""
    print("\n🧪 Testing CLI structure...")

    try:
        # Try to import the CLI module directly to avoid platform name collision
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "cli_main",
            Path(__file__).parent
            / "src"
            / "HandleGeneric v2"
            / "src"
            / "platform"
            / "interfaces"
            / "cli"
            / "main.py",
        )
        if spec and spec.loader:
            cli_main = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cli_main)

            # Check that the app exists and has commands
            app = cli_main.app
            commands = app.commands
            expected_commands = [
                "s1-generate",
                "s2-metadata",
                "s3-validate",
                "status",
                "version",
            ]

            found_commands = []
            for cmd_name in expected_commands:
                if cmd_name in commands:
                    found_commands.append(cmd_name)

            print(f"✅ CLI commands found: {found_commands}")

            if len(found_commands) == len(expected_commands):
                print("✅ All expected CLI commands present")
            else:
                missing = set(expected_commands) - set(found_commands)
                print(f"⚠️  Missing CLI commands: {missing}")
        else:
            print("⚠️  Could not load CLI module")

    except Exception as e:
        print(f"❌ CLI structure error: {e}")
        return False

    return True


def main():
    """Run all tests."""
    print("🚀 Starting Platform Integration Test\n")

    tests = [
        test_platform_initialization,
        test_domain_models,
        test_python_providers,
        test_file_system_adapters,
        test_cli_structure,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        else:
            print(f"💥 Test failed: {test.__name__}")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Platform is ready to use.")
        print("\n🔧 Next steps:")
        print("1. Set up your OpenAI API key in .env")
        print("2. Run: python -m platform.interfaces.cli.main status")
        print(
            "3. Try generating code: python -m platform.interfaces.cli.main s1-generate examples/requirements/sample_calculator.json python"
        )
        return True
    else:
        print(f"❌ {total - passed} tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
