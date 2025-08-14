import sys
from typing import Union

def divide_numbers(dividend: Union[int, float], divisor: Union[int, float]) -> Union[float, None]:
    """
    Divides two numbers and returns the result.

    Args:
        dividend (Union[int, float]): The number to be divided.
        divisor (Union[int, float]): The number by which to divide.

    Returns:
        Union[float, None]: The result of the division if successful, 
        or None if an error occurs (e.g., division by zero).
    """
    try:
        result = dividend / divisor
        return result
    except ZeroDivisionError:
        print("Error: Division by zero is not allowed.", file=sys.stderr)
        return None
    except TypeError:
        print("Error: Both inputs must be numbers (int or float).", file=sys.stderr)
        return None

def main() -> None:
    """
    Main function to demonstrate the divide_numbers function.
    Prompts the user for two numbers and performs division.
    """
    try:
        # Get user input
        dividend = float(input("Enter the dividend (number to be divided): "))
        divisor = float(input("Enter the divisor (number to divide by): "))
        
        # Perform division
        result = divide_numbers(dividend, divisor)
        
        # Display the result
        if result is not None:
            print(f"The result of dividing {dividend} by {divisor} is: {result}")
    except ValueError:
        print("Error: Invalid input. Please enter numeric values.", file=sys.stderr)

if __name__ == "__main__":
    main()