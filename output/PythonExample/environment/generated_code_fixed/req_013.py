import os
import sys
import logging

import math


def calculate_square_root(number: float) -> float:
    """
    Calculate the square root of a given number.

    Args:
        number (float): The number for which the square root is to be calculated.

    Returns:
        float: The square root of the number if successful.

    Raises:
        ValueError: If the number is negative, as square root of a negative number is not defined in real numbers.
    """
    if number < 0:
        raise ValueError("Cannot calculate the square root of a negative number.")
    return math.sqrt(number)


def main():
    """
    Main function to interact with the user and calculate the square root.
    """
    print("Welcome to the Square Root Calculator!")
    try:
        user_input = input("Enter a number to calculate its square root: ")
        number = float(user_input)
        result = calculate_square_root(number)
        print(f"The square root of {number} is {result:.5f}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Thank you for using the Square Root Calculator!")


if __name__ == "__main__":
    main()