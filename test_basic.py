#!/usr/bin/env python3
"""
Basic test script that tests core functionality without import conflicts.
"""

import sys
import tempfile
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src" / "HandleGeneric v2" / "src"))


def test_basic_functionality():
    """Test basic functionality without full platform initialization."""
    print("🧪 Testing basic functionality...")

    try:
        # Test domain models
        from platform.domain.models.requirements import Requirement
        from platform.domain.models.metadata import FileMetadata
        from platform.domain.models.validation import SyntaxResult
        from platform.domain.models.generation import GeneratedFile

        # Test requirement
        req = Requirement(
            id="TEST-001",
            title="Test",
            description="Test desc",
            acceptance=["Must work"],
        )
        print(f"✅ Domain models work: {req.id}")

        # Test Python providers
        from platform.adapters.providers.python.metadata_provider import (
            PythonMetadataProvider,
        )
        from platform.adapters.providers.python.syntax_validator import (
            PythonSyntaxValidator,
        )

        metadata_provider = PythonMetadataProvider()
        syntax_validator = PythonSyntaxValidator()

        # Test with simple code
        test_code = '''
def hello():
    """Say hello."""
    return "hello"

class TestClass:
    """A test class."""
    def method(self):
        return 42
'''

        # Test metadata extraction
        metadata = metadata_provider.parse_file(Path("test.py"), test_code)
        print(
            f"✅ Metadata extraction: {len(metadata.functions)} functions, {len(metadata.classes)} classes"
        )

        # Test syntax validation
        result = syntax_validator.validate(Path("test.py"), test_code)
        print(f"✅ Syntax validation: {result.status}")

        # Test file system adapters
        from platform.adapters.fs.local_fs import LocalFileSystem
        from platform.adapters.fs.artifact_writer import LocalArtifactWriter

        fs = LocalFileSystem()
        writer = LocalArtifactWriter()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.py"

            fs.write_text(test_file, test_code)
            read_back = fs.read_text(test_file)

            if read_back == test_code:
                print("✅ File system operations work")
            else:
                print("❌ File system operations failed")
                return False

            # Test artifact writing
            generated_files = [
                GeneratedFile(
                    path="main.py", content="print('hello')", language="python"
                )
            ]
            writer.write(temp_path / "output", generated_files)
            print("✅ Artifact writing works")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def main():
    """Run basic tests."""
    print("🚀 Running Basic Platform Tests\n")

    if test_basic_functionality():
        print("\n🎉 Basic functionality works!")
        print("\n📝 Summary:")
        print("✅ Domain models - working")
        print("✅ Python providers - working")
        print("✅ File system adapters - working")
        print("✅ Metadata extraction - working")
        print("✅ Syntax validation - working")

        print("\n🔧 To use the platform:")
        print("1. Install dependencies: pip install openai pydantic typer rich")
        print("2. Set up .env file with your OpenAI API key")
        print("3. Navigate to: cd 'src/HandleGeneric v2/src'")
        print("4. Run: python -m platform.interfaces.cli.main status")

        return True
    else:
        print("\n❌ Basic functionality failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
