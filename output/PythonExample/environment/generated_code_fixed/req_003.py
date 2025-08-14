import sys
from typing import Union

def multiply_numbers(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Multiplies two numbers and returns the result.

    Args:
        a (Union[int, float]): The first number.
        b (Union[int, float]): The second number.

    Returns:
        Union[int, float]: The result of multiplying the two numbers.

    Raises:
        ValueError: If either input is not a number.
    """
    try:
        # Validate that the inputs are numeric
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise ValueError(f"Invalid input types: {type(a).__name__}, {type(b).__name__}. Must be int or float.")

        # Perform multiplication
        result = a * b
        return result

    except Exception as e:
        # Catch and log unexpected exceptions
        print(f"An error occurred: {e}", file=sys.stderr)
        raise

# Example usage (can be removed or commented out for production code)
if __name__ == "__main__":
    try:
        num1 = float(input("Enter the first number: "))
        num2 = float(input("Enter the second number: "))
        print(f"The product of {num1} and {num2} is: {multiply_numbers(num1, num2)}")
    except ValueError as ve:
        print(f"Input error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")