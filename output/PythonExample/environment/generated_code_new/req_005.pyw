import sys
from typing import Union

def add_and_double(num1: Union[int, float], num2: Union[int, float]) -> Union[int, float]:
    """
    Add two numbers and multiply the result by two.

    Args:
        num1 (Union[int, float]): The first number.
        num2 (Union[int, float]): The second number.

    Returns:
        Union[int, float]: The result of adding the two numbers and multiplying by two.

    Raises:
        ValueError: If the inputs are not numbers.
    """
    try:
        result = (num1 + num2) * 2
        return result
    except TypeError as e:
        raise ValueError("Both inputs must be numbers.") from e

def main() -> None:
    """
    Main function to execute the calculator application.

    Prompts the user for input, calculates the result, and handles any errors.
    """
    try:
        # Get user input
        num1_input = input("Enter the first number: ")
        num2_input = input("Enter the second number: ")

        # Convert input to float
        num1 = float(num1_input)
        num2 = float(num2_input)

        # Perform calculation
        result = add_and_double(num1, num2)

        # Display result
        print(f"The result of adding {num1} and {num2}, then multiplying by two, is: {result}")

    except ValueError as ve:
        print(f"Input error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()