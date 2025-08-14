import os
import sys
import logging

import operator
from typing import List, Tuple, Union


class Calculator:
    """
    A comprehensive calculator application with basic arithmetic operations 
    and proper error handling.

    Supported operations:
    - Addition
    - Subtraction
    - Multiplication
    - Division
    """

    def __init__(self) -> None:
        """
        Initializes the Calculator with a mapping of supported operations.
        """
        self.operations = {
            "add": operator.add,
            "subtract": operator.sub,
            "multiply": operator.mul,
            "divide": self._safe_divide
        }

    def calculate(
        self, operation: str, numbers: List[Union[int, float]]
    ) -> Union[float, str]:
        """
        Perform the specified operation on the given list of numbers.

        Args:
            operation (str): The operation to perform ("add", "subtract", "multiply", "divide").
            numbers (List[Union[int, float]]): A list of numbers to perform the operation on.

        Returns:
            Union[float, str]: The result of the calculation, or an error message if input is invalid.

        Raises:
            ValueError: If the operation is not supported.
        """
        if operation not in self.operations:
            raise ValueError(f"Unsupported operation: {operation}")

        if not numbers or len(numbers) < 2:
            return "Error: At least two numbers are required for the operation."

        try:
            result = numbers[0]
            for number in numbers[1:]:
                result = self.operations[operation](result, number)
            return result
        except ZeroDivisionError:
            return "Error: Division by zero is not allowed."
        except Exception as e:
            return f"Error: An unexpected error occurred: {e}"

    @staticmethod
    def _safe_divide(a: Union[int, float], b: Union[int, float]) -> float:
        """
        Safely performs division, raising an exception for division by zero.

        Args:
            a (Union[int, float]): The numerator.
            b (Union[int, float]): The denominator.

        Returns:
            float: The result of the division.

        Raises:
            ZeroDivisionError: If the denominator is zero.
        """
        if b == 0:
            raise ZeroDivisionError
        return a / b


def main() -> None:
    """
    Main function to demonstrate the usage of the Calculator class.
    Allows the user to perform arithmetic operations interactively.
    """
    calculator = Calculator()
    print("Welcome to the Calculator Application!")
    print("Available operations: add, subtract, multiply, divide")
    print("Enter 'quit' to exit the application.")

    while True:
        try:
            operation = input("Enter operation: ").strip().lower()
            if operation == "quit":
                print("Goodbye!")
                break

            numbers_input = input("Enter numbers separated by spaces: ").strip()
            numbers = [float(num) for num in numbers_input.split()]

            result = calculator.calculate(operation, numbers)
            print(f"Result: {result}")

        except ValueError as ve:
            print(f"Error: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()