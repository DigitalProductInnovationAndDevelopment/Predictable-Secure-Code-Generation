import sys
from typing import Union

def subtract_numbers(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Subtracts the second number from the first number.

    Args:
        a (Union[int, float]): The first number (minuend).
        b (Union[int, float]): The second number (subtrahend).

    Returns:
        Union[int, float]: The result of the subtraction.

    Raises:
        ValueError: If the inputs are not numbers.
    """
    try:
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise ValueError("Both inputs must be integers or floats.")
        return a - b
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        raise

# Example usage (this part would generally not be in the module if used as a library):
if __name__ == "__main__":
    try:
        num1 = float(input("Enter the first number: "))
        num2 = float(input("Enter the second number: "))
        result = subtract_numbers(num1, num2)
        print(f"The result of subtracting {num2} from {num1} is {result}.")
    except ValueError as ve:
        print(f"Input error: {ve}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")