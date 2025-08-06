import os
import sys
import logging

import operator
from typing import Callable, Union

class Calculator:
    """
    A comprehensive calculator application that performs basic mathematical operations.
    """

    def __init__(self) -> None:
        """
        Initializes the calculator with a dictionary of supported operations.
        """
        self.operations = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': self.safe_divide,
            '**': operator.pow,
        }

    def safe_divide(self, a: float, b: float) -> float:
        """
        Safely performs division and handles division by zero.

        Args:
            a (float): The dividend.
            b (float): The divisor.

        Returns:
            float: The result of the division.

        Raises:
            ValueError: If attempting to divide by zero.
        """
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        return a / b

    def calculate(self, operand1: Union[float, int], operator_symbol: str, operand2: Union[float, int]) -> float:
        """
        Performs a calculation based on the provided operands and operator.

        Args:
            operand1 (Union[float, int]): The first operand.
            operator_symbol (str): The operator as a string (e.g., '+', '-', '*', '/', '**').
            operand2 (Union[float, int]): The second operand.

        Returns:
            float: The result of the calculation.

        Raises:
            ValueError: If an invalid operator is provided.
        """
        operation: Callable[[float, float], float] = self.operations.get(operator_symbol)
        if operation is None:
            raise ValueError(f"Invalid operator '{operator_symbol}'. Supported operators are: {', '.join(self.operations.keys())}.")
        return operation(operand1, operand2)

def main() -> None:
    """
    Main function to interact with the Calculator application.
    """
    calculator = Calculator()
    print("Welcome to the Calculator application!")
    print("Supported operations: +, -, *, /, ** (power)")

    while True:
        try:
            # Input parsing
            operand1 = float(input("Enter the first number: "))
            operator_symbol = input("Enter the operator: ")
            operand2 = float(input("Enter the second number: "))

            # Perform calculation
            result = calculator.calculate(operand1, operator_symbol, operand2)
            print(f"The result is: {result}")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        # Check if the user wants to continue
        continue_calculation = input("Would you like to perform another calculation? (yes/no): ").strip().lower()
        if continue_calculation not in ('yes', 'y'):
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()