import sys


def subtract_numbers(a: float, b: float) -> float:
    """
    Subtract two numbers and return the result.

    Args:
        a (float): The first number (minuend).
        b (float): The second number (subtrahend).

    Returns:
        float: The result of subtracting b from a.

    Raises:
        ValueError: If the inputs are not numbers.
    """
    try:
        return a - b
    except TypeError as e:
        raise ValueError("Both inputs must be numbers.") from e


def main():
    """
    Main function to provide a user-friendly interface for subtracting two numbers.

    Prompts the user to input two numbers, performs the subtraction,
    and displays the result. Handles invalid inputs gracefully.
    """
    print("Welcome to the Comprehensive Calculator - Subtraction Module")
    try:
        # Prompt the user for inputs
        num1 = float(input("Enter the first number (minuend): "))
        num2 = float(input("Enter the second number (subtrahend): "))

        # Perform subtraction
        result = subtract_numbers(num1, num2)

        # Display the result
        print(f"The result of {num1} - {num2} is {result}")
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()