import sys
from typing import Union

def subtract_numbers(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Subtract two numbers and return the result.

    Parameters:
        a (int | float): The first number (minuend).
        b (int | float): The second number (subtrahend).

    Returns:
        int | float: The result of subtracting b from a.

    Raises:
        ValueError: If inputs are not numbers.
    """
    try:
        # Validate inputs
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise ValueError("Both inputs must be integers or floats.")

        # Perform subtraction
        result = a - b
        return result

    except Exception as e:
        # Log the exception details to standard error
        print(f"Error occurred: {e}", file=sys.stderr)
        raise

# Example usage
if __name__ == "__main__":
    try:
        num1 = float(input("Enter the first number: "))
        num2 = float(input("Enter the second number: "))
        print(f"The result of subtraction is: {subtract_numbers(num1, num2)}")
    except ValueError as ve:
        print(f"Input error: {ve}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)