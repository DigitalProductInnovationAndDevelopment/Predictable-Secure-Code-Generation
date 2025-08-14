import sys
from typing import Union

def add_and_double(num1: Union[int, float], num2: Union[int, float]) -> Union[int, float]:
    """
    Adds two numbers and multiplies the result by two.

    Args:
        num1 (Union[int, float]): The first number.
        num2 (Union[int, float]): The second number.

    Returns:
        Union[int, float]: The result of (num1 + num2) * 2.

    Raises:
        ValueError: If inputs are not numbers.
    """
    try:
        # Ensure the inputs are valid numbers
        result = (num1 + num2) * 2
        return result
    except TypeError as e:
        raise ValueError("Both inputs must be integers or floats.") from e

def main():
    """
    Main function to execute the calculator logic.
    Prompts the user for two numbers, performs the calculation,
    and displays the result.
    """
    try:
        print("Welcome to the Calculator!")
        
        # Prompt for first number
        num1 = input("Enter the first number: ")
        num1 = float(num1) if '.' in num1 else int(num1)
        
        # Prompt for second number
        num2 = input("Enter the second number: ")
        num2 = float(num2) if '.' in num2 else int(num2)
        
        # Perform the calculation
        result = add_and_double(num1, num2)
        
        # Display the result
        print(f"The result of adding {num1} and {num2}, then doubling it, is: {result}")
    
    except ValueError as ve:
        print(f"Input Error: {ve}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")
    finally:
        print("Thank you for using the Calculator. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()