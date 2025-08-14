import os
import sys
import logging

import operator
from typing import List, Union, Callable

class Calculator:
    """
    A comprehensive calculator application that supports basic arithmetic operations.

    Methods:
        add(a, b): Adds two numbers.
        subtract(a, b): Subtracts the second number from the first.
        multiply(a, b): Multiplies two numbers.
        divide(a, b): Divides the first number by the second.
        calculate(operand, a, b): Performs the specified operation on two numbers.
        process_operations(operations): Processes a list of operations and returns results.
    """

    def __init__(self) -> None:
        """
        Initializes the calculator and defines the supported operations.
        """
        self.operators: dict[str, Callable[[float, float], float]] = {
            "add": operator.add,
            "subtract": operator.sub,
            "multiply": operator.mul,
            "divide": self._safe_divide
        }

    @staticmethod
    def _safe_divide(a: float, b: float) -> float:
        """
        Safely divides two numbers, handling division by zero.

        Args:
            a (float): The dividend.
            b (float): The divisor.

        Returns:
            float: The result of the division.

        Raises:
            ValueError: If division by zero is attempted.
        """
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        return a / b

    def add(self, a: float, b: float) -> float:
        """
        Adds two numbers.

        Args:
            a (float): The first number.
            b (float): The second number.

        Returns:
            float: The sum of the two numbers.
        """
        return self.operators["add"](a, b)

    def subtract(self, a: float, b: float) -> float:
        """
        Subtracts the second number from the first.

        Args:
            a (float): The first number.
            b (float): The second number.

        Returns:
            float: The result of the subtraction.
        """
        return self.operators["subtract"](a, b)

    def multiply(self, a: float, b: float) -> float:
        """
        Multiplies two numbers.

        Args:
            a (float): The first number.
            b (float): The second number.

        Returns:
            float: The product of the two numbers.
        """
        return self.operators["multiply"](a, b)

    def divide(self, a: float, b: float) -> float:
        """
        Divides the first number by the second.

        Args:
            a (float): The first number.
            b (float): The second number.

        Returns:
            float: The result of the division.
        """
        return self.operators["divide"](a, b)

    def calculate(self, operand: str, a: float, b: float) -> Union[float, str]:
        """
        Performs the specified operation on two numbers.

        Args:
            operand (str): The operation to perform. Must be one of "add", "subtract", "multiply", or "divide".
            a (float): The first number.
            b (float): The second number.

        Returns:
            Union[float, str]: The result of the operation, or an error message if the operation is invalid.
        """
        try:
            if operand not in self.operators:
                raise ValueError(f"Invalid operation '{operand}'. Supported operations are: {', '.join(self.operators.keys())}")
            return self.operators[operand](a, b)
        except Exception as e:
            return str(e)

    def process_operations(self, operations: List[dict]) -> List[Union[float, str]]:
        """
        Processes a list of operations and returns their results.

        Args:
            operations (List[dict]): A list of operations, where each operation is a dictionary
                                     with keys "operand", "a", and "b".

        Returns:
            List[Union[float, str]]: A list of results for each operation.
        """
        results = []
        for operation in operations:
            try:
                operand = operation.get("operand")
                a = operation.get("a")
                b = operation.get("b")
                if operand is None or a is None or b is None:
                    raise ValueError("Operation dictionary must contain 'operand', 'a', and 'b' keys.")
                result = self.calculate(operand, float(a), float(b))
                results.append(result)
            except Exception as e:
                results.append(str(e))
        return results

if __name__ == "__main__":
    calc = Calculator()
    operations = [
        {"operand": "add", "a": 5, "b": 3},
        {"operand": "subtract", "a": 10, "b": 4},
        {"operand": "multiply", "a": 7, "b": 2},
        {"operand": "divide", "a": 8, "b": 0},  # Division by zero
        {"operand": "modulus", "a": 9, "b": 3}  # Invalid operation
    ]
    results = calc.process_operations(operations)
    for i, result in enumerate(results, 1):
        print(f"Operation {i}: {result}")