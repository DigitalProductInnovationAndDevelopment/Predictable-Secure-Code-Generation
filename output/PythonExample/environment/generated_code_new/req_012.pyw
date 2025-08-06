import sys
from typing import Callable

def add(a: float, b: float) -> float:
    """Returns the sum of two numbers."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Returns the difference of two numbers."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Returns the product of two numbers."""
    return a * b

def divide(a: float, b: float) -> float:
    """
    Returns the division of two numbers.
    Raises a ZeroDivisionError if the divisor is zero.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b

def modulus(a: float, b: float) -> float:
    """
    Returns the modulus of two numbers.
    Raises a ZeroDivisionError if the divisor is zero.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot perform modulus with zero.")
    return a % b

def exponent(a: float, b: float) -> float:
    """Returns the result of raising a to the power of b."""
    return a ** b

def calculator_operation(a: float, b: float, operation: Callable[[float, float], float]) -> float:
    """
    Performs the given calculator operation on two numbers.

    Args:
        a: First number.
        b: Second number.
        operation: A callable representing the operation to perform.

    Returns:
        The result of the operation.
    """
    return operation(a, b)

def main() -> None:
    """
    Entry point for the command-line calculator. 
    Prompts the user to select a calculator operation and inputs two numbers.
    """
    operations = {
        "1": ("Addition", add),
        "2": ("Subtraction", subtract),
        "3": ("Multiplication", multiply),
        "4": ("Division", divide),
        "5": ("Modulus", modulus),
        "6": ("Exponentiation", exponent),
    }

    print("Welcome to the Command-Line Calculator!")
    print("Select an operation:")
    
    for key, (name, _) in operations.items():
        print(f"{key}. {name}")

    choice = input("Enter the number of the operation you want to perform: ").strip()

    if choice not in operations:
        print("Invalid choice. Please select a valid operation.")
        sys.exit(1)

    try:
        a = float(input("Enter the first number: ").strip())
        b = float(input("Enter the second number: ").strip())
        
        operation_name, operation_func = operations[choice]
        print(f"Performing {operation_name}...")
        
        result = calculator_operation(a, b, operation_func)
        print(f"The result is: {result}")

    except ValueError:
        print("Invalid input. Please enter valid numbers.")
    except ZeroDivisionError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print("Thank you for using the calculator!")

if __name__ == "__main__":
    main()