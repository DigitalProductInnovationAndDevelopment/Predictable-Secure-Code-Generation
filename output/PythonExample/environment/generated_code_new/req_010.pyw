import os
import sys
import logging

import typing


class CalculatorError(Exception):
    """
    Custom exception class for calculator-related errors.
    """
    pass


class Calculator:
    """
    A comprehensive calculator class with various operations and proper error handling.
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
            raise CalculatorError("Cannot sum an empty list.")
        return sum(numbers)


# Example usage
if __name__ == "__main__":
    calculator = Calculator()
    try:
        result = calculator.sum_numbers([1, 2, 3])
        print(f"Sum: {result}")
        result_empty = calculator.sum_numbers([])
    except CalculatorError as e:
        print(f"Error: {e}")