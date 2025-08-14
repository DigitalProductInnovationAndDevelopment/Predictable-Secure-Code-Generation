import sys
from typing import List


class CalculatorError(Exception):
    """Custom exception class for Calculator errors."""
    pass


class Calculator:
    """
    A class representing a simple calculator with various operations.
    """

    @staticmethod
    def sum_numbers(numbers: List[float]) -> float:
        """
        Computes the sum of a list of numbers.

        Args:
            numbers (List[float]): A list of numbers to sum.

        Returns:
            float: The sum of the numbers in the list.

        Raises:
            CalculatorError: If the input list is empty.
        """
        if not numbers:
            raise CalculatorError("Cannot calculate the sum of an empty list.")
        return sum(numbers)


def main():
    """
    Entry point for the calculator application.
    Demonstrates the usage of the Calculator class.
    """
    try:
        # Example usage of the Calculator
        calc = Calculator()
        numbers_to_sum = []  # Empty list to trigger the error
        result = calc.sum_numbers(numbers_to_sum)
        print(f"The sum is: {result}")
    except CalculatorError as e:
        print(f"Error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()