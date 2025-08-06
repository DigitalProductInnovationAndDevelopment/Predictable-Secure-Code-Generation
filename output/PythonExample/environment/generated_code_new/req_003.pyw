import sys
from typing import Union

def multiply_numbers(num1: Union[int, float], num2: Union[int, float]) -> Union[int, float]:
    """
    Multiplies two numbers and returns the result.

    Args:
        num1 (Union[int, float]): The first number.
        num2 (Union[int, float]): The second number.

    Returns:
        Union[int, float]: The product of num1 and num2.

    Raises:
        ValueError: If inputs are not valid numbers.
    """
    try:
        # Validate that inputs are numbers
        if not isinstance(num1, (int, float)) or not isinstance(num2, (int, float)):
            raise ValueError("Both inputs must be integers or floats.")

        # Perform multiplication
        result = num1 * num2
        return result

    except ValueError as e:
        # Log and re-raise the exception for caller to handle
        print(f"Error: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    try:
        # Example usage
        print("Welcome to the calculator!")
        first_number = input("Enter the first number: ")
        second_number = input("Enter the second number: ")

        # Convert inputs to float for calculation
        num1 = float(first_number)
        num2 = float(second_number)

        # Call the multiply function
        product = multiply_numbers(num1, num2)
        print(f"The product of {num1} and {num2} is {product}")

    except ValueError as ve:
        print(f"Input error: {ve}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}", file=sys.stderr)