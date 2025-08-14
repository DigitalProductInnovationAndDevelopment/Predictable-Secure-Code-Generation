import sys
from typing import Union

def divide_numbers(dividend: Union[int, float], divisor: Union[int, float]) -> Union[float, None]:
    """
    Divide two numbers and return the result.
    
    Args:
        dividend (Union[int, float]): The number to be divided (numerator).
        divisor (Union[int, float]): The number to divide by (denominator).
    
    Returns:
        Union[float, None]: The result of the division if successful, or None if an error occurs.
        
    Raises:
        ValueError: If the divisor is zero, since division by zero is undefined.
    """
    try:
        if divisor == 0:
            raise ValueError("Division by zero is not allowed.")
        result = dividend / divisor
        return result
    except ValueError as ve:
        print(f"Error: {ve}", file=sys.stderr)
        return None
    except TypeError as te:
        print(f"Error: Invalid input types. Both arguments must be numbers. {te}", file=sys.stderr)
        return None

def main():
    """
    Main function to demonstrate the division functionality.
    """
    try:
        dividend = float(input("Enter the dividend (numerator): "))
        divisor = float(input("Enter the divisor (denominator): "))
        result = divide_numbers(dividend, divisor)
        if result is not None:
            print(f"The result of dividing {dividend} by {divisor} is: {result}")
    except ValueError:
        print("Error: Please enter valid numeric inputs.", file=sys.stderr)

if __name__ == "__main__":
    main()