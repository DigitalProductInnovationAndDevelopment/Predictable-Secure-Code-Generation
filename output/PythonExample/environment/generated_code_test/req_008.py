import os
import sys
import logging

import operator
from typing import Union

class Calculator:
    """
    A comprehensive calculator application that performs basic arithmetic operations
    with input validation and proper error handling.
    """

    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Adds two numbers.

        :param a: The first number (int or float).
        :param b: The second number (int or float).
        :return: The sum of the two numbers.
        :raises TypeError: If inputs are not int or float.
        """
        self._validate_input(a, b)
        return operator.add(a, b)

    def subtract(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Subtracts the second number from the first.

        :param a: The first number (int or float).
        :param b: The second number (int or float).
        :return: The difference between the two numbers.
        :raises TypeError: If inputs are not int or float.
        """
        self._validate_input(a, b)
        return operator.sub(a, b)

    def multiply(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Multiplies two numbers.

        :param a: The first number (int or float).
        :param b: The second number (int or float).
        :return: The product of the two numbers.
        :raises TypeError: If inputs are not int or float.
        """
        self._validate_input(a, b)
        return operator.mul(a, b)

    def divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Divides the first number by the second.

        :param a: The first number (int or float).
        :param b: The second number (int or float).
        :return: The quotient of the division.
        :raises TypeError: If inputs are not int or float.
        :raises ZeroDivisionError: If the second number is zero.
        """
        self._validate_input(a, b)
        if b == 0:
            raise ZeroDivisionError("Division by zero is not allowed.")
        return operator.truediv(a, b)

    def _validate_input(self, a: Union[int, float], b: Union[int, float]) -> None:
        """
        Validates that both inputs are either int or float.

        :param a: The first input.
        :param b: The second input.
        :raises TypeError: If either input is not an int or float.
        """
        if not isinstance(a, (int, float)):
            raise TypeError(f"Invalid input type: {a} (expected int or float).")
        if not isinstance(b, (int, float)):
            raise TypeError(f"Invalid input type: {b} (expected int or float).")

if __name__ == "__main__":
    calc = Calculator()

    try:
        print("Addition:", calc.add(10, 5))
        print("Subtraction:", calc.subtract(10, 5))
        print("Multiplication:", calc.multiply(10, 5))
        print("Division:", calc.divide(10, 5))
    except (TypeError, ZeroDivisionError) as e:
        print(f"Error: {e}")