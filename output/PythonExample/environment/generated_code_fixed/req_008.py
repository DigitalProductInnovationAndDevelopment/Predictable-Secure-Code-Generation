import os
import sys
import logging

import operator
from typing import Union

class Calculator:
    """
    A comprehensive calculator application that performs basic mathematical operations
    with proper input type validation and error handling.
    """

    def __init__(self):
        """
        Initializes a Calculator instance.
        """
        self.operations = {
            "add": operator.add,
            "subtract": operator.sub,
            "multiply": operator.mul,
            "divide": self._safe_divide
        }

    def _validate_inputs(self, a: Union[int, float], b: Union[int, float]) -> None:
        """
        Validates that the inputs are either integers or floats.

        :param a: First input value
        :param b: Second input value
        :raises TypeError: If either input is not an int or float
        """
        if not isinstance(a, (int, float)):
            raise TypeError(f"Invalid type for 'a': {type(a).__name__}. Must be int or float.")
        if not isinstance(b, (int, float)):
            raise TypeError(f"Invalid type for 'b': {type(b).__name__}. Must be int or float.")

    def _safe_divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Safely performs division, ensuring no division by zero occurs.

        :param a: Dividend
        :param b: Divisor
        :return: Result of division
        :raises ZeroDivisionError: If divisor is zero
        """
        if b == 0:
            raise ZeroDivisionError("Division by zero is not allowed.")
        return operator.truediv(a, b)

    def calculate(self, operation: str, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Performs a calculation based on the given operation and input values.

        :param operation: The operation to perform ('add', 'subtract', 'multiply', 'divide')
        :param a: First input value
        :param b: Second input value
        :return: The result of the operation
        :raises ValueError: If the operation is not supported
        :raises TypeError: If inputs are not valid types
        :raises ZeroDivisionError: If division by zero is attempted
        """
        self._validate_inputs(a, b)

        if operation not in self.operations:
            raise ValueError(f"Unsupported operation: {operation}. Supported operations are: {list(self.operations.keys())}")

        return self.operations[operation](a, b)

def main():
    """
    Main function to demonstrate the usage of the Calculator class.
    """
    calculator = Calculator()

    try:
        # Example usage
        result = calculator.calculate("add", 10, 5)
        print(f"Addition Result: {result}")

        result = calculator.calculate("subtract", 10, 5)
        print(f"Subtraction Result: {result}")

        result = calculator.calculate("multiply", 10, 5)
        print(f"Multiplication Result: {result}")

        result = calculator.calculate("divide", 10, 5)
        print(f"Division Result: {result}")

        # Uncomment the following lines to test error handling:
        # result = calculator.calculate("divide", 10, 0)  # ZeroDivisionError
        # result = calculator.calculate("mod", 10, 5)     # ValueError
        # result = calculator.calculate("add", "10", 5)  # TypeError

    except (TypeError, ValueError, ZeroDivisionError) as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()