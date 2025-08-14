import sys
from typing import Callable


def add(a: float, b: float) -> float:
    """
    Perform addition of two numbers.

    Args:
        a (float): The first number.
        b (float): The second number.

    Returns:
        float: The sum of the two numbers.
    """
    return a + b


def subtract(a: float, b: float) -> float:
    """
    Perform subtraction of two numbers.

    Args:
        a (float): The first number.
        b (float): The second number.

    Returns:
        float: The result of subtracting b from a.
    """
    return a - b


def multiply(a: float, b: float) -> float:
    """
    Perform multiplication of two numbers.

    Args:
        a (float): The first number.
        b (float): The second number.

    Returns:
        float: The product of the two numbers.
    """
    return a * b


def divide(a: float, b: float) -> float:
    """
    Perform division of two numbers.

    Args:
        a (float): The numerator.
        b (float): The denominator.

    Returns:
        float: The result of dividing a by b.

    Raises:
        ValueError: If b is zero.
    """
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b


def calculator(operation: Callable[[float, float], float], a: float, b: float) -> float:
    """
    Perform a calculation using the given operation.

    Args:
        operation (Callable[[float, float], float]): The arithmetic operation to perform.
        a (float): The first operand.
        b (float): The second operand.

    Returns:
        float: The result of the calculation.
    """
    return operation(a, b)


def main() -> None:
    """
    Main function to provide a command-line interface for the calculator.

    Args:
        None

    Returns:
        None
    """
    print("Welcome to the Calculator CLI!")
    print("Available operations:")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")
    print("5. Exit")

    while True:
        try:
            choice = input("\nEnter the number of the operation you want to perform (1-5): ").strip()
            if choice == "5":
                print("Exiting the calculator. Goodbye!")
                sys.exit(0)

            if choice not in {"1", "2", "3", "4"}:
                print("Invalid choice. Please select a valid operation.")
                continue

            try:
                a = float(input("Enter the first number: ").strip())
                b = float(input("Enter the second number: ").strip())
            except ValueError:
                print("Invalid input. Please enter numeric values.")
                continue

            operation_map = {
                "1": add,
                "2": subtract,
                "3": multiply,
                "4": divide
            }

            operation = operation_map[choice]
            result = calculator(operation, a, b)
            print(f"The result is: {result}")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()