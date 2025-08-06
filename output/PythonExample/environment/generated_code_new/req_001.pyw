import sys

def add_two_numbers(num1: float, num2: float) -> float:
    """
    Adds two numbers and returns the result.

    Args:
        num1 (float): The first number.
        num2 (float): The second number.

    Returns:
        float: The sum of the two numbers.

    Raises:
        ValueError: If the inputs are not valid numbers.
    """
    try:
        return num1 + num2
    except TypeError as e:
        raise ValueError("Invalid input: Both inputs must be numbers.") from e


def get_number_input(prompt: str) -> float:
    """
    Prompts the user to input a number and validates the input.

    Args:
        prompt (str): The input prompt to display to the user.

    Returns:
        float: The validated number input.

    Raises:
        ValueError: If the user inputs an invalid number.
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def main() -> None:
    """
    Main function to execute the calculator application.

    Prompts the user to input two numbers, adds them, and displays the result.
    Handles exceptions gracefully and ensures a smooth user experience.
    """
    print("Welcome to the Calculator Application!")
    print("This program will add two numbers for you.\n")

    try:
        num1 = get_number_input("Enter the first number: ")
        num2 = get_number_input("Enter the second number: ")
        result = add_two_numbers(num1, num2)
        print(f"\nThe result of adding {num1} and {num2} is: {result}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()