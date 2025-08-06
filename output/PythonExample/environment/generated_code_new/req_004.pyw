import sys
from typing import Union

def divide_numbers(dividend: Union[int, float], divisor: Union[int, float]) -> float:
    """
    Divides two numbers and returns the result.

    Args:
        dividend (Union[int, float]): The number to be divided.
        divisor (Union[int, float]): The number by which to divide.

    Returns:
        float: The result of the division.

    Raises:
        ValueError: If the divisor is zero.
        TypeError: If non-numeric types are provided.
    """
    try:
        # Ensure inputs are numeric
        if not isinstance(dividend, (int, float)) or not isinstance(divisor, (int, float)):
            raise TypeError("Both dividend and divisor must be numeric (int or float).")
        
        # Check for division by zero
        if divisor == 0:
            raise ValueError("Division by zero is not allowed.")
        
        # Perform division
        result = dividend / divisor
        return result
    except (ValueError, TypeError) as e:
        # Handle exceptions and print an error message
        print(f"Error: {e}", file=sys.stderr)
        raise  # Re-raise the exception for further handling if needed

# Example usage (uncomment to test):
# try:
#     result = divide_numbers(10, 2)
#     print(f"Result: {result}")
# except Exception as e:
#     print(f"An error occurred: {e}")