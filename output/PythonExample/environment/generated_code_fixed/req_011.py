import os
import sys
import logging

import numbers
from typing import List

class CalculatorError(Exception):
    """Custom exception for calculator errors."""
    pass

class Calculator:
    """A simple calculator application with error handling."""

    @staticmethod
    def sum_numbers(numbers_list: List) -> float:
        """
        Sums a list of numbers, raising an error if non-numeric elements are found.

        Args:
            numbers_list (List): A list of elements to sum.

        Returns:
            float: The sum of all numeric elements in the list.

        Raises:
            CalculatorError: If the list contains non-numeric elements.
        """
        if not all(isinstance(item, numbers.Number) for item in numbers_list):
            raise CalculatorError("All elements in the list must be numeric.")
        
        return sum(numbers_list)

# Example usage
if __name__ == "__main__":
    calculator = Calculator()

    try:
        numbers_to_sum = [1, 2, 3, 'a', 5]  # Example input containing a non-numeric value
        result = calculator.sum_numbers(numbers_to_sum)
        print(f"The sum is: {result}")
    except CalculatorError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")