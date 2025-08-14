import sys
from typing import Union

def subtract_numbers(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Subtract two numbers and return the result.

    Args:
        a (Union[int, float]): The first number (minuend).
        b (Union[int, float]): The second number (subtrahend).

    Returns:
        Union[int, float]: The difference between the two numbers.

    Raises:
        ValueError: If either of the inputs is not a valid number.
    """
    try:
        # Ensure inputs are valid numbers
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise ValueError("Both inputs must be integers or floats.")
        return a - b
    except Exception as error:
        # Log the error and re-raise it for further handling
        print(f"Error: {error}", file=sys.stderr)
        raise

# Example usage
if __name__ == "__main__":
    try:
        num1 = float(input("Enter the first number: "))
        num2 = float(input("Enter the second number: "))
        result = subtract_numbers(num1, num2)
        print(f"The result of subtracting {num2} from {num1} is: {result}")
    except ValueError as ve:
        print(f"Invalid input: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")