import os
import sys
import logging

import operator
from typing import Union

class CalculatorError(Exception):
    """Custom exception for calculator errors."""
    pass

class Calculator:
    """
    A simple calculator class that performs basic arithmetic operations
    with proper error handling.
    """

    @staticmethod
    def divide(a: Union[int, float], b: Union[int, float]) -> float:
        """
        Performs division of two numbers.

        Args:
            a (Union[int, float]): The numerator.
            b (Union[int, float]): The denominator.

        Returns:
            float: The result of the division.

        Raises:
            CalculatorError: If the denominator is zero.
        """
        if b == 0:
            raise CalculatorError("Division by zero is not allowed.")
        return operator.truediv(a, b)

    @staticmethod
    def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Performs addition of two numbers.

        Args:
            a (Union[int, float]): The first number.
            b (Union[int, float]): The second number.

        Returns:
            Union[int, float]: The sum of the two numbers.
        """
        return operator.add(a, b)

    @staticmethod
    def subtract(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Performs subtraction of two numbers.

        Args:
            a (Union[int, float]): The first number.
            b (Union[int, float]): The second number.

        Returns:
            Union[int, float]: The result of subtracting b from a.
        """
        return operator.sub(a, b)

    @staticmethod
    def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Performs multiplication of two numbers.

        Args:
            a (Union[int, float]): The first number.
            b (Union[int, float]): The second number.

        Returns:
            Union[int, float]: The product of the two numbers.
        """
        return operator.mul(a, b)

def main():
    """
    The main function to demonstrate the usage of the Calculator class.
    """
    calculator = Calculator()

    try:
        # Example usage
        result = calculator.divide(10, 2)
        print("Division Result:", result)

        # Example of division by zero
        result = calculator.divide(10, 0)
        print("This will not print.")
    except CalculatorError as e:
        print("Error:", e)

if __name__ == "__main__":
    main()