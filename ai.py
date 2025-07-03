import sys
import logging
import argparse
from typing import Optional, Dict, Any
from openai import AzureOpenAI
from config import Config


class AzureOpenAIClient:
    """Azure OpenAI client for handling prompts and questions"""

    def __init__(self, config: Config = None):
        """Initialize the Azure OpenAI client with configuration"""
        self.config = config or Config()
        self._setup_logging()
        self._validate_config()
        self.client = self._initialize_client()

    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL), format=self.config.LOG_FORMAT
        )
        self.logger = logging.getLogger(__name__)

    def _validate_config(self):
        """Validate configuration settings"""
        errors = self.config.validate_config()
        if errors:
            for error in errors:
                self.logger.error(f"Configuration error: {error}")
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")

    def _initialize_client(self) -> AzureOpenAI:
        """Initialize and return Azure OpenAI client"""
        try:
            client = AzureOpenAI(
                api_key=self.config.AZURE_OPENAI_API_KEY,
                azure_endpoint=self.config.AZURE_OPENAI_ENDPOINT,
                api_version=self.config.AZURE_OPENAI_API_VERSION,
            )
            self.logger.info("Azure OpenAI client initialized successfully")
            return client
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
            raise

    def ask_question(
        self,
        question: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Ask a question and get a response from Azure OpenAI

        Args:
            question: The user's question or prompt
            system_prompt: Optional system prompt (uses default if not provided)
            max_tokens: Maximum tokens for response (uses config default if not provided)
            temperature: Temperature for response generation (uses config default if not provided)
            **kwargs: Additional parameters for the API call

        Returns:
            Dictionary containing response and metadata
        """
        try:
            # Use provided values or fall back to config defaults
            system_prompt = system_prompt or self.config.DEFAULT_SYSTEM_PROMPT
            max_tokens = max_tokens or self.config.AI_MAX_TOKENS
            temperature = (
                temperature if temperature is not None else self.config.AI_TEMPERATURE
            )

            self.logger.info(f"Processing question: {question[:100]}...")

            # Prepare messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ]

            # Make API call
            response = self.client.chat.completions.create(
                model=self.config.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=kwargs.get("top_p", self.config.AI_TOP_P),
                frequency_penalty=kwargs.get(
                    "frequency_penalty", self.config.AI_FREQUENCY_PENALTY
                ),
                presence_penalty=kwargs.get(
                    "presence_penalty", self.config.AI_PRESENCE_PENALTY
                ),
                **{
                    k: v
                    for k, v in kwargs.items()
                    if k not in ["top_p", "frequency_penalty", "presence_penalty"]
                },
            )

            if response and response.choices:
                result = {
                    "status": "success",
                    "answer": response.choices[0].message.content,
                    "usage": {
                        "prompt_tokens": (
                            response.usage.prompt_tokens if response.usage else 0
                        ),
                        "completion_tokens": (
                            response.usage.completion_tokens if response.usage else 0
                        ),
                        "total_tokens": (
                            response.usage.total_tokens if response.usage else 0
                        ),
                    },
                    "model": self.config.AZURE_OPENAI_DEPLOYMENT_NAME,
                    "parameters": {
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "top_p": kwargs.get("top_p", self.config.AI_TOP_P),
                    },
                }
                self.logger.info(
                    f"Question processed successfully. Tokens used: {result['usage']['total_tokens']}"
                )
                return result
            else:
                raise ValueError("No response received from Azure OpenAI")

        except Exception as e:
            error_msg = f"Error processing question: {str(e)}"
            self.logger.error(error_msg)
            return {"status": "error", "error": error_msg, "answer": None}

    def correct_code(self, code: str, **kwargs) -> Dict[str, Any]:
        """
        Correct Python code using Azure OpenAI

        Args:
            code: The code to correct
            **kwargs: Additional parameters for the API call

        Returns:
            Dictionary containing corrected code and metadata
        """
        prompt = f"Please correct this Python code:\n\n{code}"
        return self.ask_question(
            question=prompt, system_prompt=self.config.CODE_CORRECTION_PROMPT, **kwargs
        )

    def test_connection(self) -> bool:
        """Test the Azure OpenAI connection"""
        try:
            self.logger.info("Testing Azure OpenAI connection...")
            result = self.ask_question(
                "Say hello and confirm you're working!", max_tokens=50
            )
            if result["status"] == "success":
                self.logger.info("Connection test successful")
                print(f"Connection successful! Response: {result['answer']}")
                return True
            else:
                self.logger.error(
                    f"Connection test failed: {result.get('error', 'Unknown error')}"
                )
                print(f"Connection test failed: {result.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            self.logger.error(f"Connection test failed with exception: {str(e)}")
            print(f"Connection test failed: {str(e)}")
            return False


def main():
    """Main function for command line interface"""
    parser = argparse.ArgumentParser(
        description="Azure OpenAI Client for Questions and Code Correction"
    )
    parser.add_argument("--question", "-q", type=str, help="Question to ask")
    parser.add_argument("--code", "-c", type=str, help="Code to correct")
    parser.add_argument("--system-prompt", "-s", type=str, help="Custom system prompt")
    parser.add_argument(
        "--max-tokens", "-m", type=int, help="Maximum tokens for response"
    )
    parser.add_argument(
        "--temperature", "-t", type=float, help="Temperature for response generation"
    )
    parser.add_argument("--test", action="store_true", help="Test the connection")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Start interactive mode"
    )

    args = parser.parse_args()

    try:
        # Initialize client
        ai_client = AzureOpenAIClient()

        # Test connection if requested
        if args.test:
            ai_client.test_connection()
            return

        # Interactive mode
        if args.interactive:
            print("Azure OpenAI Interactive Mode")
            print("Commands:")
            print("  /code <your_code>  - Correct code")
            print("  /system <prompt>   - Set system prompt")
            print("  /quit or /exit     - Exit")
            print("  Anything else      - Ask a question")
            print("-" * 50)

            system_prompt = None
            while True:
                try:
                    user_input = input("\n> ").strip()
                    if not user_input:
                        continue

                    if user_input.lower() in ["/quit", "/exit"]:
                        print("Goodbye!")
                        break
                    elif user_input.startswith("/code "):
                        code = user_input[6:]
                        result = ai_client.correct_code(code)
                        if result["status"] == "success":
                            print(f"\nCorrected Code:\n{result['answer']}")
                            print(f"\nTokens used: {result['usage']['total_tokens']}")
                        else:
                            print(f"Error: {result['error']}")
                    elif user_input.startswith("/system "):
                        system_prompt = user_input[8:]
                        print(f"System prompt set: {system_prompt[:50]}...")
                    else:
                        # Regular question
                        result = ai_client.ask_question(
                            user_input,
                            system_prompt=system_prompt,
                            max_tokens=args.max_tokens,
                            temperature=args.temperature,
                        )
                        if result["status"] == "success":
                            print(f"\nAnswer: {result['answer']}")
                            print(f"\nTokens used: {result['usage']['total_tokens']}")
                        else:
                            print(f"Error: {result['error']}")

                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break
                except Exception as e:
                    print(f"Error: {str(e)}")
            return

        # Single question mode
        if args.question:
            result = ai_client.ask_question(
                args.question,
                system_prompt=args.system_prompt,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
            )
            if result["status"] == "success":
                print(result["answer"])
                if "-v" in sys.argv or "--verbose" in sys.argv:
                    print(f"\nTokens used: {result['usage']['total_tokens']}")
            else:
                print(f"Error: {result['error']}", file=sys.stderr)
                sys.exit(1)
            return

        # Code correction mode
        if args.code:
            result = ai_client.correct_code(
                args.code, max_tokens=args.max_tokens, temperature=args.temperature
            )
            if result["status"] == "success":
                print(result["answer"])
                if "-v" in sys.argv or "--verbose" in sys.argv:
                    print(f"\nTokens used: {result['usage']['total_tokens']}")
            else:
                print(f"Error: {result['error']}", file=sys.stderr)
                sys.exit(1)
            return

        # If no arguments provided, show help
        parser.print_help()

    except Exception as e:
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
