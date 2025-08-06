import os
import sys
import logging

import operator
from typing import List, Union, Optional


class Calculator:
    """
    A comprehensive calculator application that supports basic arithmetic operations
    and handles errors gracefully.

    Supported operations:
    - Addition
    - Subtraction
    - Multiplication
    - Division
    """

    def __init__(self):
        # Dictionary mapping operation names to their corresponding functions
        self.operations = {
            "add": operator.add,
            "subtract": operator.sub,
            "multiply": operator.mul,
            "divide": self._safe_divide,
        }

    def calculate(self, operation: str, operands: List[Union[int, float]]) -> Optional[Union[int, float]]:
        """
        Perform the specified operation on a list of operands.

        Args:
            operation (str): The name of the operation to perform (e.g., "add", "subtract").
            operands (List[Union[int, float]]): A list of numbers to operate on.

        Returns:
            Optional[Union[int, float]]: The result of the calculation, or None if an error occurs.

        Raises:
            ValueError: If the operation is not supported or the operands list is invalid.
        """
        try:
            # Validate operation
            if operation not in self.operations:
                raise ValueError(f"Unsupported operation: {operation}")

            # Validate operands
            if not operands or len(operands) < 2:
                raise ValueError("At least two operands are required for calculation.")

            # Perform the operation iteratively
            result = operands[0]
            for operand in operands[1:]:
                result = self.operations[operation](result, operand)

            return result

        except ZeroDivisionError:
            print("Error: Division by zero is not allowed.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def _safe_divide(self, x: Union[int, float], y: Union[int, float]) -> Union[int, float]:
        """
        Safely perform division, raising ZeroDivisionError if the denominator is zero.

        Args:
            x (Union[int, float]): The numerator.
            y (Union[int, float]): The denominator.

        Returns:
            Union[int, float]: The result of the division.

        Raises:
            ZeroDivisionError: If the denominator is zero.
        """
        if y == 0:
            raise ZeroDivisionError("Division by zero is not allowed.")
        return x / y


def main():
    """
    Entry point for the calculator application. Accepts user input, performs the requested
    operation, and displays the result.
    """
    calculator = Calculator()

    print("Welcome to the Calculator Application!")
    print("Supported operations: add, subtract, multiply, divide")

    while True:
        try:
            # Get user input
            operation = input("Enter the operation to perform (or 'exit' to quit): ").strip().lower()
            if operation == "exit":
                print("Goodbye!")
                break

            # Get operands
            operands_input = input("Enter the operands (comma-separated): ").strip()
            operands = [float(x) for x in operands_input.split(",")]

            # Perform calculation
            result = calculator.calculate(operation, operands)
            if result is not None:
                print(f"The result is: {result}")

        except ValueError as ve:
            print(f"Input error: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()