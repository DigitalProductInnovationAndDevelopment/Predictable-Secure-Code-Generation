import os
import sys
import logging

import operator
from typing import Callable, Union

class Calculator:
    """
    A comprehensive calculator class that supports basic arithmetic operations
    with proper error handling.
    """

    def __init__(self):
        """
        Initializes the calculator with a dictionary of supported operators.
        """
        self.operations = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': self.safe_divide,
            '%': operator.mod,
            '**': operator.pow
        }

    def safe_divide(self, a: float, b: float) -> float:
        """
        Safely performs division and handles division by zero.
        
        Args:
            a (float): The numerator.
            b (float): The denominator.
        
        Returns:
            float: The result of the division.
            
        Raises:
            ValueError: If division by zero is attempted.
        """
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        return a / b

    def calculate(self, operand1: Union[int, float], operand2: Union[int, float], operator: str) -> float:
        """
        Performs the calculation based on the given operator and operands.
        
        Args:
            operand1 (Union[int, float]): The first operand.
            operand2 (Union[int, float]): The second operand.
            operator (str): The operator to perform the calculation.
        
        Returns:
            float: The result of the calculation.
        
        Raises:
            ValueError: If the operator is not supported.
        """
        if operator not in self.operations:
            raise ValueError(f"Unsupported operator: {operator}")
        
        operation: Callable[[float, float], float] = self.operations[operator]
        return operation(operand1, operand2)

    def parse_and_calculate(self, input_string: str) -> float:
        """
        Parses an input string and performs the corresponding calculation.
        
        Args:
            input_string (str): The input string in the format "operand1 operator operand2".
        
        Returns:
            float: The result of the calculation.
        
        Raises:
            ValueError: If the input format is invalid or calculation errors occur.
        """
        try:
            parts = input_string.split()
            if len(parts) != 3:
                raise ValueError("Input must be in the format: 'operand1 operator operand2'.")
            
            operand1 = float(parts[0])
            operator = parts[1]
            operand2 = float(parts[2])
            
            return self.calculate(operand1, operand2, operator)
        except ValueError as e:
            raise ValueError(f"Error processing input: {e}")

def main():
    """
    Main function to run the calculator application.
    """
    calculator = Calculator()
    print("Welcome to the Calculator!")
    print("Enter your calculation in the format: 'operand1 operator operand2'")
    print("Type 'exit' to quit.")

    while True:
        user_input = input("\nEnter calculation: ").strip()
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        try:
            result = calculator.parse_and_calculate(user_input)
            print(f"Result: {result}")
        except ValueError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()