#!/usr/bin/env python3
"""
Simple test script for AI functionality.
Run this from the ai directory to test the AI client.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)


def test_ai():
    """Test the AI functionality"""
    print("🤖 Testing AI Client")
    print("=" * 40)

    try:
        from ai import AzureOpenAIClient

        print("✅ Successfully imported AzureOpenAIClient")

        # Initialize client
        ai_client = AzureOpenAIClient()
        print("✅ AI client initialized")

        # Test connection
        print("\n🔗 Testing connection...")
        if ai_client.test_connection():
            print("✅ Connection successful!")

            # Test a simple question
            print("\n❓ Testing question...")
            result = ai_client.ask_question(
                "What is 3 + 3? Answer with just the number.", max_tokens=20
            )

            if result["status"] == "success":
                print(f"✅ Question test successful!")
                print(f"   Answer: {result['answer']}")
                print(f"   Tokens: {result['usage']['total_tokens']}")
            else:
                print(f"❌ Question failed: {result.get('error')}")

            print("\n🎉 AI is working correctly!")
            return True
        else:
            print("❌ Connection failed!")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_ai()
    sys.exit(0 if success else 1)
