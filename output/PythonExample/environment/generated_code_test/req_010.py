import os
import sys
import logging

import typing


class CalculatorError(Exception):
    """
    Custom exception class for Calculator errors.
    """
    def __init__(self, message: str):
        super().__init__(message)


class Calculator:
    """
    A comprehensive calculator class with proper error handling.
    """

    @staticmethod
    def sum_numbers(numbers: typing.List[float]) -> float:
        """
        Sums a list of numbers.

        Args:
            numbers (List[float]): A list of numbers to sum.

        Returns:
            float: The sum of the numbers.

        Raises:
            CalculatorError: If the input list is empty.
        """
        if not numbers:
            raise CalculatorError("Cannot calculate the sum of an empty list.")
        return sum(numbers)


# Example usage
if __name__ == "__main__":
    try:
        calculator = Calculator()
        result = calculator.sum_numbers([])  # This will raise an error
        print(f"The sum is: {result}")
    except CalculatorError as e:
        print(f"Error: {e}")