import sys
from typing import Union

def add_numbers(num1: Union[int, float], num2: Union[int, float]) -> float:
    """
    Adds two numbers and returns the result.

    Args:
        num1 (Union[int, float]): The first number to add.
        num2 (Union[int, float]): The second number to add.

    Returns:
        float: The sum of the two numbers.

    Raises:
        ValueError: If the inputs are not numbers.
    """
    try:
        # Ensure both inputs are numbers
        if not isinstance(num1, (int, float)) or not isinstance(num2, (int, float)):
            raise ValueError("Both inputs must be numeric (int or float).")
        return num1 + num2
    except Exception as e:
        # Log the exception and re-raise
        print(f"An error occurred: {e}", file=sys.stderr)
        raise

def main():
    """
    Main function to demonstrate the addition of two numbers with error handling.
    """
    try:
        # Example inputs
        num1 = input("Enter the first number: ")
        num2 = input("Enter the second number: ")

        # Convert inputs to float
        num1 = float(num1)
        num2 = float(num2)

        # Perform addition
        result = add_numbers(num1, num2)
        print(f"The sum of {num1} and {num2} is: {result}")

    except ValueError as ve:
        print(f"Input error: {ve}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()