import os
import sys
import logging

import numbers
from typing import List, Union


class CalculatorError(Exception):
    """
    Custom exception class for Calculator errors.
    """
    pass


class Calculator:
    """
    A comprehensive calculator class with proper error handling.
    """

    @staticmethod
    def sum_list(values: List[Union[int, float]]) -> float:
        """
        Sums up a list of numeric elements. Raises an error if any element is non-numeric.

        Args:
            values (List[Union[int, float]]): List of numeric elements to sum.

        Returns:
            float: The sum of the numeric elements.

        Raises:
            CalculatorError: If the list contains any non-numeric elements.
        """
        if not all(isinstance(value, numbers.Number) for value in values):
            raise CalculatorError("All elements in the list must be numeric.")
        return sum(values)


def main():
    """
    Main function to demonstrate the usage of the Calculator class.
    """
    calculator = Calculator()

    try:
        numeric_list = [1, 2.5, 3]
        print("Sum of numeric_list:", calculator.sum_list(numeric_list))

        invalid_list = [1, "a", 3]
        print("Sum of invalid_list:", calculator.sum_list(invalid_list))
    except CalculatorError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()