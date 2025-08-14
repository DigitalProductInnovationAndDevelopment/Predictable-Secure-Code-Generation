import sys
from typing import Union


class CalculatorError(Exception):
    """Custom exception class for calculator errors."""
    pass


class Calculator:
    """A simple calculator with error handling for division by zero."""

    @staticmethod
    def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Adds two numbers.

        :param a: The first number.
        :param b: The second number.
        :return: The sum of the two numbers.
        """
        return a + b

    @staticmethod
    def subtract(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Subtracts the second number from the first.

        :param a: The first number.
        :param b: The second number.
        :return: The result of subtraction.
        """
        return a - b

    @staticmethod
    def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Multiplies two numbers.

        :param a: The first number.
        :param b: The second number.
        :return: The product of the two numbers.
        """
        return a * b

    @staticmethod
    def divide(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Divides the first number by the second.

        :param a: The numerator.
        :param b: The denominator.
        :return: The result of division.
        :raises CalculatorError: If an attempt is made to divide by zero.
        """
        if b == 0:
            raise CalculatorError("Division by zero is not allowed.")
        return a / b


def main():
    """
    Main function to demonstrate the Calculator functionality.
    """
    calculator = Calculator()

    try:
        # Example use cases
        print("Addition: ", calculator.add(10, 5))
        print("Subtraction: ", calculator.subtract(10, 5))
        print("Multiplication: ", calculator.multiply(10, 5))
        print("Division: ", calculator.divide(10, 5))
        
        # Example of a division by zero error
        print("Division by zero attempt: ", calculator.divide(10, 0))
    except CalculatorError as e:
        print(f"Error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()