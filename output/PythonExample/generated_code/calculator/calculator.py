"""
Calculator module providing basic mathematical operations.
"""

import sys
import math
from typing import List, Union


class Calculator:
    """
    A calculator class that provides basic mathematical operations.
    """

    @staticmethod
    def add(a: float, b: float) -> float:
        """
        Add two numbers.

        Args:
            a (float): First number
            b (float): Second number

        Returns:
            float: Sum of a and b
        """
        return a + b

    @staticmethod
    def subtract(a: float, b: float) -> float:
        """
        Subtract two numbers.

        Args:
            a (float): First number
            b (float): Second number

        Returns:
            float: Difference of a and b (a - b)
        """
        return a - b

    @staticmethod
    def multiply(a: float, b: float) -> float:
        """
        Multiply two numbers.

        Args:
            a (float): First number
            b (float): Second number

        Returns:
            float: Product of a and b

        Raises:
            TypeError: If inputs are not numbers
        """
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Inputs must be numbers")
        return round(a * b, 10)  # Round to avoid floating point precision issues

    @staticmethod
    def divide(a: float, b: float) -> float:
        """
        Divide two numbers.

        Args:
            a (float): First number
            b (float): Second number

        Returns:
            float: Division of a by b

        Raises:
            ValueError: If b is zero
        """
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        return a / b

    @staticmethod
    def add_and_multiply_by_two(a: float, b: float) -> float:
        """
        Add two numbers and multiply the result by 2.

        Args:
            a (float): First number
            b (float): Second number

        Returns:
            float: (a + b) * 2
        """
        return (a + b) * 2

    @staticmethod
    def sum_list(numbers: List[float]) -> float:
        """
        Calculate the sum of a list of numbers.

        Args:
            numbers (List[float]): List of numbers to sum

        Returns:
            float: Sum of all numbers in the list

        Raises:
            TypeError: If input is not a list or contains non-numeric elements
            ValueError: If list is empty
        """
        if not isinstance(numbers, list):
            raise TypeError("Input must be a list")

        if len(numbers) == 0:
            raise ValueError("The list cannot be empty")

        # Check if all elements are numeric
        for element in numbers:
            if not isinstance(element, (int, float)):
                raise TypeError("All elements in the list must be numeric")

        return sum(numbers)

    @staticmethod
    def factorial(n: int) -> int:
        """
        Calculate the factorial of a number.

        Args:
            n (int): Non-negative integer

        Returns:
            int: Factorial of n

        Raises:
            ValueError: If n is negative or not an integer
            TypeError: If n is not a number
        """
        if not isinstance(n, (int, float)):
            raise TypeError("Input must be a number")

        if not isinstance(n, int) or n != int(n):
            raise ValueError("Input must be an integer")

        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers")

        if n == 0 or n == 1:
            return 1

        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    @staticmethod
    def power(base: float, exponent: float) -> float:
        """
        Calculate base raised to the power of exponent.

        Args:
            base (float): Base number
            exponent (float): Exponent

        Returns:
            float: base^exponent
        """
        return base**exponent

    @staticmethod
    def calculate_percentage(part: float, whole: float) -> float:
        """
        Calculate what percentage 'part' is of 'whole'.

        Args:
            part (float): The part value
            whole (float): The whole value

        Returns:
            float: Percentage value

        Raises:
            ValueError: If whole is zero
            TypeError: If inputs are not numbers
        """
        if not isinstance(part, (int, float)) or not isinstance(whole, (int, float)):
            raise TypeError("Both inputs must be numbers")

        if whole == 0:
            raise ValueError("Cannot calculate percentage with zero as whole")

        if math.isinf(part) or math.isinf(whole):
            raise ValueError("Cannot calculate percentage with infinite values")

        if math.isnan(part) or math.isnan(whole):
            raise ValueError("Cannot calculate percentage with NaN values")

        return (part / whole) * 100

    def square_root(self, n: float) -> float:
        """
        Calculate the square root of a number.

        Args:
            n (float): Non-negative number

        Returns:
            float: Square root of n

        Raises:
            ValueError: If n is negative
            TypeError: If n is not a number
        """
        if isinstance(n, str):
            raise TypeError("Input must be a number, not string")

        if not isinstance(n, (int, float, bool)):
            raise TypeError("Input must be a number")

        if n < 0:
            raise ValueError("Cannot calculate square root of negative number")

        return math.sqrt(n)


def display_menu() -> None:
    """
    Displays the CLI menu with numbered options for user interaction.
    """
    print("\n=== Calculator CLI Menu ===")
    print("1. Add two numbers")
    print("2. Subtract two numbers")
    print("3. Multiply two numbers")
    print("4. Divide two numbers")
    print("5. Add two numbers and multiply the result by 2")
    print("6. Sum a list of numbers")
    print("7. Exit")


def get_user_choice() -> int:
    """
    Prompts the user to select an option from the menu.

    Returns:
        int: The user's menu choice.
    """
    try:
        choice = int(input("Enter your choice (1-7): "))
        if choice < 1 or choice > 7:
            raise ValueError("Choice must be between 1 and 7.")
        return choice
    except ValueError as e:
        print(f"Invalid input: {e}")
        return -1


def handle_user_choice(choice: int, calculator: Calculator) -> None:
    """
    Handles the user's menu choice and performs the corresponding operation.

    Args:
        choice (int): The user's menu choice.
        calculator (Calculator): An instance of the Calculator class.
    """
    if choice == 1:
        try:
            a = float(input("Enter the first number: "))
            b = float(input("Enter the second number: "))
            result = calculator.add(a, b)
            print(f"Result: {result}")
        except ValueError:
            print("Invalid input. Please enter numeric values.")
    elif choice == 2:
        try:
            a = float(input("Enter the first number: "))
            b = float(input("Enter the second number: "))
            result = calculator.subtract(a, b)
            print(f"Result: {result}")
        except ValueError:
            print("Invalid input. Please enter numeric values.")
    elif choice == 3:
        try:
            a = float(input("Enter the first number: "))
            b = float(input("Enter the second number: "))
            result = calculator.multiply(a, b)
            print(f"Result: {result}")
        except ValueError:
            print("Invalid input. Please enter numeric values.")
    elif choice == 4:
        try:
            a = float(input("Enter the first number: "))
            b = float(input("Enter the second number: "))
            if b == 0:
                print("Error: Division by zero is not allowed.")
            else:
                result = calculator.divide(a, b)
                print(f"Result: {result}")
        except ValueError:
            print("Invalid input. Please enter numeric values.")
        except ValueError as e:
            print(f"Error: {e}")
    elif choice == 5:
        try:
            a = float(input("Enter the first number: "))
            b = float(input("Enter the second number: "))
            result = calculator.add_and_multiply_by_two(a, b)
            print(f"Result: {result}")
        except ValueError:
            print("Invalid input. Please enter numeric values.")
    elif choice == 6:
        try:
            numbers = input("Enter a list of numbers separated by spaces: ")
            num_list = [float(num) for num in numbers.split()]
            result = calculator.sum_list(num_list)
            print(f"Result: {result}")
        except ValueError:
            print("Invalid input. Please enter numeric values.")
    elif choice == 7:
        print("Exiting the program. Goodbye!")
        sys.exit(0)
    else:
        print("Invalid choice. Please try again.")


def main() -> None:
    """
    Main function to run the CLI menu interface.
    """
    calculator = Calculator()
    while True:
        display_menu()
        choice = get_user_choice()
        if choice != -1:
            handle_user_choice(choice, calculator)


if __name__ == "__main__":
    main()
