import os
import sys
import logging

import operator
from typing import Union

class Calculator:
    """
    A comprehensive calculator class that supports basic operations
    with proper error handling, including division by zero.
    """
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Adds two numbers.
        
        Args:
            a (int | float): The first number.
            b (int | float): The second number.
            
        Returns:
            int | float: The result of addition.
        """
        return operator.add(a, b)
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Subtracts the second number from the first.
        
        Args:
            a (int | float): The first number.
            b (int | float): The second number.
            
        Returns:
            int | float: The result of subtraction.
        """
        return operator.sub(a, b)
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Multiplies two numbers.
        
        Args:
            a (int | float): The first number.
            b (int | float): The second number.
            
        Returns:
            int | float: The result of multiplication.
        """
        return operator.mul(a, b)
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Divides the first number by the second.
        
        Args:
            a (int | float): The numerator.
            b (int | float): The denominator.
            
        Returns:
            int | float: The result of division.
            
        Raises:
            ZeroDivisionError: If an attempt is made to divide by zero.
        """
        try:
            if b == 0:
                raise ZeroDivisionError("Division by zero is not allowed.")
            return operator.truediv(a, b)
        except ZeroDivisionError as e:
            print(f"Error: {e}")
            raise

if __name__ == "__main__":
    calculator = Calculator()
    
    try:
        # Example usage
        print("Addition: ", calculator.add(10, 5))
        print("Subtraction: ", calculator.subtract(10, 5))
        print("Multiplication: ", calculator.multiply(10, 5))
        print("Division: ", calculator.divide(10, 5))
        print("Division by zero test: ", calculator.divide(10, 0))  # This will trigger an error
    except ZeroDivisionError:
        print("Caught an exception while performing division.")