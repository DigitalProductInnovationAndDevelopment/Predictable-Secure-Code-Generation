import os
import sys
import logging

import operator


class Calculator:
    """
    A comprehensive calculator application that supports basic arithmetic operations.
    Includes proper error handling and adheres to PEP 8 style guidelines.
    """

    def __init__(self) -> None:
        """
        Initializes the Calculator class with supported operations.
        """
        # Mapping of operation symbols to corresponding functions
        self.operations = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": self._safe_divide,
            "**": operator.pow,
        }

    def calculate(self, expression: str) -> float:
        """
        Evaluates a given arithmetic expression and returns the result.

        Args:
            expression (str): A string representing the arithmetic expression.

        Returns:
            float: The result of the calculation.

        Raises:
            ValueError: If the input is invalid or contains unsupported operations.
            ZeroDivisionError: If division by zero is attempted.
        """
        try:
            # Parse the input expression
            left_operand, operator_symbol, right_operand = self._parse_expression(expression)

            # Convert operands to float
            left_operand = float(left_operand)
            right_operand = float(right_operand)

            # Retrieve the operation function
            operation_func = self.operations.get(operator_symbol)
            if operation_func is None:
                raise ValueError(f"Unsupported operation: {operator_symbol}")

            # Perform the calculation
            result = operation_func(left_operand, right_operand)
            return result

        except ValueError as e:
            raise ValueError(f"Invalid input: {expression}. Error: {e}")

    def _safe_divide(self, a: float, b: float) -> float:
        """
        Safely performs division, raising an error for division by zero.

        Args:
            a (float): The numerator.
            b (float): The denominator.

        Returns:
            float: The result of the division.

        Raises:
            ZeroDivisionError: If the denominator is zero.
        """
        if b == 0:
            raise ZeroDivisionError("Division by zero is not allowed.")
        return a / b

    @staticmethod
    def _parse_expression(expression: str) -> tuple[str, str, str]:
        """
        Parses a basic arithmetic expression into operands and operator.

        Args:
            expression (str): A string representing the arithmetic expression.

        Returns:
            tuple[str, str, str]: A tuple containing the left operand, operator, and right operand.

        Raises:
            ValueError: If the expression format is invalid.
        """
        for operator_symbol in ["+", "-", "*", "/", "**"]:
            if operator_symbol in expression:
                parts = expression.split(operator_symbol)
                if len(parts) == 2:
                    left_operand, right_operand = parts
                    return left_operand.strip(), operator_symbol, right_operand.strip()
        raise ValueError("Invalid expression format. Ensure it includes a valid operator.")

    def list_operations(self) -> list[str]:
        """
        Returns a list of supported operations.

        Returns:
            list[str]: A list of supported operation symbols.
        """
        return list(self.operations.keys())


def main() -> None:
    """
    The main function to interact with the Calculator.
    """
    calculator = Calculator()
    print("Welcome to the Calculator!")
    print("Supported operations:", ", ".join(calculator.list_operations()))

    while True:
        try:
            # Prompt the user for input
            expression = input("Enter an expression (e.g., 2 + 2) or 'q' to quit: ").strip()

            # Exit condition
            if expression.lower() == "q":
                print("Goodbye!")
                break

            # Perform calculation
            result = calculator.calculate(expression)
            print(f"Result: {result}")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()