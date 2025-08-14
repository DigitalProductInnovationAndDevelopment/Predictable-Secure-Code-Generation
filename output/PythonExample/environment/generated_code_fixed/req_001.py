import sys
from typing import Union

def add_numbers(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Adds two numbers and returns the result.

    Args:
        a (Union[int, float]): The first number to add.
        b (Union[int, float]): The second number to add.

    Returns:
        Union[int, float]: The sum of the two numbers.

    Raises:
        ValueError: If the inputs are not numbers.
    """
    try:
        # Ensure inputs are numbers
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise ValueError(f"Invalid input types: a={a} ({type(a)}), b={b} ({type(b)})")
        return a + b
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise

def main() -> None:
    """
    Main function to demonstrate the usage of add_numbers function.
    Handles user input and provides a simple calculator interface.
    """
    try:
        print("Welcome to the calculator!")
        num1 = input("Enter the first number: ")
        num2 = input("Enter the second number: ")

        # Convert inputs to numbers
        try:
            num1 = float(num1) if '.' in num1 else int(num1)
            num2 = float(num2) if '.' in num2 else int(num2)
        except ValueError:
            raise ValueError("Both inputs must be numeric values.")

        # Perform addition
        result = add_numbers(num1, num2)
        print(f"The result of adding {num1} and {num2} is: {result}")

    except ValueError as ve:
        print(f"Input Error: {ve}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()