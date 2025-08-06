import os
import sys
import logging

import operator
from typing import Union, Any

class Calculator:
    """
    A comprehensive calculator class that performs basic arithmetic operations
    with input type validation and proper error handling.
    """

    def validate_input(self, value: Any) -> Union[int, float]:
        """
        Validates that the input is either an integer or a float.
        
        Args:
            value (Any): The input value to validate.

        Returns:
            Union[int, float]: The validated numerical value.

        Raises:
            TypeError: If the input value is not an integer or a float.
        """
        if not isinstance(value, (int, float)):
            raise TypeError(f"Invalid input type: {value}. Expected int or float.")
        return value

    def add(self, a: Any, b: Any) -> Union[int, float]:
        """
        Adds two numbers.

        Args:
            a (Any): The first number.
            b (Any): The second number.

        Returns:
            Union[int, float]: The sum of the two numbers.

        Raises:
            TypeError: If inputs are not numeric.
        """
        a = self.validate_input(a)
        b = self.validate_input(b)
        return operator.add(a, b)

    def subtract(self, a: Any, b: Any) -> Union[int, float]:
        """
        Subtracts the second number from the first.

        Args:
            a (Any): The first number.
            b (Any): The second number.

        Returns:
            Union[int, float]: The result of the subtraction.

        Raises:
            TypeError: If inputs are not numeric.
        """
        a = self.validate_input(a)
        b = self.validate_input(b)
        return operator.sub(a, b)

    def multiply(self, a: Any, b: Any) -> Union[int, float]:
        """
        Multiplies two numbers.

        Args:
            a (Any): The first number.
            b (Any): The second number.

        Returns:
            Union[int, float]: The product of the two numbers.

        Raises:
            TypeError: If inputs are not numeric.
        """
        a = self.validate_input(a)
        b = self.validate_input(b)
        return operator.mul(a, b)

    def divide(self, a: Any, b: Any) -> Union[int, float]:
        """
        Divides the first number by the second.

        Args:
            a (Any): The dividend.
            b (Any): The divisor.

        Returns:
            Union[int, float]: The result of the division.

        Raises:
            TypeError: If inputs are not numeric.
            ZeroDivisionError: If the divisor is zero.
        """
        a = self.validate_input(a)
        b = self.validate_input(b)
        if b == 0:
            raise ZeroDivisionError("Division by zero is not allowed.")
        return operator.truediv(a, b)

    def power(self, a: Any, b: Any) -> Union[int, float]:
        """
        Raises the first number to the power of the second.

        Args:
            a (Any): The base.
            b (Any): The exponent.

        Returns:
            Union[int, float]: The result of the exponentiation.

        Raises:
            TypeError: If inputs are not numeric.
        """
        a = self.validate_input(a)
        b = self.validate_input(b)
        return operator.pow(a, b)

    def modulus(self, a: Any, b: Any) -> Union[int, float]:
        """
        Calculates the modulus of the first number by the second.

        Args:
            a (Any): The dividend.
            b (Any): The divisor.

        Returns:
            Union[int, float]: The remainder after division.

        Raises:
            TypeError: If inputs are not numeric.
            ZeroDivisionError: If the divisor is zero.
        """
        a = self.validate_input(a)
        b = self.validate_input(b)
        if b == 0:
            raise ZeroDivisionError("Modulus by zero is not allowed.")
        return operator.mod(a, b)

# Example usage
if __name__ == "__main__":
    calculator = Calculator()

    try:
        print(calculator.add(10, 5))         # 15
        print(calculator.subtract(10, 5))    # 5
        print(calculator.multiply(10, 5))    # 50
        print(calculator.divide(10, 5))      # 2.0
        print(calculator.power(2, 3))        # 8
        print(calculator.modulus(10, 3))     # 1
    except (TypeError, ZeroDivisionError) as e:
        print(f"Error: {e}")