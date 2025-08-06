#!/usr/bin/env python3
"""
Test script for AI functionality in HandleGeneric/ai module.
This script tests the Azure OpenAI client and its capabilities.
"""

import sys
import os
import logging
from typing import Dict, Any

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_ai_functionality():
    """Test the AI functionality"""
    print("🤖 Testing AI Functionality")
    print("=" * 50)

    try:
        # Import the AI client
        from src.HandleGeneric.ai.client import AzureOpenAIClient

        print("✅ Successfully imported AzureOpenAIClient")

        # Test configuration
        from config import Config

        config = Config()
        print("✅ Successfully loaded configuration")

        # Validate configuration
        errors = config.validate_config()
        if errors:
            print("❌ Configuration errors found:")
            for error in errors:
                print(f"   - {error}")
            print("\n💡 Please set the required environment variables:")
            print("   - AZURE_OPENAI_API_KEY")
            print("   - AZURE_OPENAI_ENDPOINT")
            print("   - AZURE_OPENAI_DEPLOYMENT_NAME (optional, defaults to 'gpt-4o')")
            return False
        else:
            print("✅ Configuration validation passed")

        # Initialize the AI client
        print("\n🔧 Initializing AI client...")
        ai_client = AzureOpenAIClient(config)
        print("✅ AI client initialized successfully")

        # Test connection
        print("\n🔗 Testing connection to Azure OpenAI...")
        connection_success = ai_client.test_connection()

        if connection_success:
            print("✅ Connection test successful!")

            # Test asking a simple question
            print("\n❓ Testing question functionality...")
            result = ai_client.ask_question(
                "What is 2 + 2? Please respond with just the number.", max_tokens=20
            )

            if result["status"] == "success":
                print(f"✅ Question test successful!")
                print(f"   Answer: {result['answer']}")
                print(f"   Tokens used: {result['usage']['total_tokens']}")
            else:
                print(
                    f"❌ Question test failed: {result.get('error', 'Unknown error')}"
                )
                return False

            # Test code correction functionality
            print("\n🔧 Testing code correction functionality...")
            test_code = """
def add_numbers(a, b):
    return a + b

result = add_numbers(5, 3)
print(result)
"""
            correction_result = ai_client.correct_code(test_code)

            if correction_result["status"] == "success":
                print("✅ Code correction test successful!")
                print(f"   Corrected code:\n{correction_result['answer']}")
                print(f"   Tokens used: {correction_result['usage']['total_tokens']}")
            else:
                print(
                    f"❌ Code correction test failed: {correction_result.get('error', 'Unknown error')}"
                )
                return False

            print("\n🎉 All AI functionality tests passed!")
            return True

        else:
            print("❌ Connection test failed!")
            print("💡 Please check your Azure OpenAI configuration:")
            print("   - Verify your API key is correct")
            print("   - Verify your endpoint URL is correct")
            print("   - Verify your deployment name exists")
            return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install openai python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_command_line_interface():
    """Test the command line interface"""
    print("\n🖥️  Testing Command Line Interface")
    print("=" * 50)

    try:
        # Test the test connection functionality
        print("Testing --test flag...")
        import subprocess

        result = subprocess.run(
            [sys.executable, "src/HandleGeneric/ai/client.py", "--test"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("✅ Command line test flag works")
        else:
            print(f"❌ Command line test failed: {result.stderr}")
            return False

        return True

    except subprocess.TimeoutExpired:
        print("❌ Command line test timed out")
        return False
    except Exception as e:
        print(f"❌ Command line test error: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Starting AI Functionality Tests")
    print("=" * 60)

    # Test 1: Basic functionality
    test1_passed = test_ai_functionality()

    # Test 2: Command line interface
    test2_passed = test_command_line_interface()

    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    print(f"AI Functionality Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Command Line Interface: {'✅ PASSED' if test2_passed else '❌ FAILED'}")

    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! AI functionality is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the configuration and try again.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
