import sys
from typing import Union

def add_numbers(a: Union[int, float], b: Union[int, float]) -> float:
    """
    Add two numbers and return the result.

    Args:
        a (Union[int, float]): The first number to add.
        b (Union[int, float]): The second number to add.

    Returns:
        float: The result of adding the two numbers.

    Raises:
        TypeError: If the inputs are not integers or floats.
        ValueError: If the inputs cannot be interpreted as numbers.
    """
    try:
        # Ensure both inputs are numbers
        if not isinstance(a, (int, float)):
            raise TypeError(f"Invalid type for 'a': {type(a)}. Expected int or float.")
        if not isinstance(b, (int, float)):
            raise TypeError(f"Invalid type for 'b': {type(b)}. Expected int or float.")

        # Perform the addition
        result = a + b
        return result

    except TypeError as e:
        print(f"Type Error: {e}", file=sys.stderr)
        raise
    except ValueError as e:
        print(f"Value Error: {e}", file=sys.stderr)
        raise

# Example usage:
if __name__ == "__main__":
    try:
        num1 = float(input("Enter the first number: "))
        num2 = float(input("Enter the second number: "))
        print(f"The result of addition is: {add_numbers(num1, num2)}")
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)