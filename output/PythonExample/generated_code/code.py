from typing import Union
from typing import List, Union
import datetime
import logging
import sys
# File: code.py

# Global variable to simulate calculator memory storage
_calculator_memory: float = 0.0


def store_in_memory(value: float) -> None:
    """
    Stores a given value in the calculator's memory.

    Args:
        value (float): The value to store in memory.

    Raises:
        ValueError: If the provided value is not a valid float.
    """
    global _calculator_memory

    if not isinstance(value, (int, float)):
        raise ValueError("Only numeric values can be stored in memory.")

    _calculator_memory = float(value)


def recall_memory() -> float:
    """
    Recalls the value stored in the calculator's memory.

    Returns:
        float: The value currently stored in memory.
    """
    return _calculator_memory


def clear_memory() -> None:
    """
    Clears the value stored in the calculator's memory.
    """
    global _calculator_memory
    _calculator_memory = 0.0


# Example usage of the memory functions
if __name__ == "__main__":
    # Storing a value in memory
    store_in_memory(42.5)
    print(f"Stored value: {recall_memory()}")  # Output: Stored value: 42.5

    # Clearing memory
    clear_memory()
    print(f"Memory after clearing: {recall_memory()}")  # Output: Memory after clearing: 0.0