import sys

def add_and_double(a: float, b: float) -> float:
    """
    Adds two numbers and multiplies the result by two.

    Args:
        a (float): The first number.
        b (float): The second number.

    Returns:
        float: The result of (a + b) * 2.
    """
    return (a + b) * 2

def get_number_input(prompt: str) -> float:
    """
    Prompts the user for a number and validates the input.

    Args:
        prompt (str): The input prompt to display to the user.

    Returns:
        float: The valid number entered by the user.

    Raises:
        ValueError: If the input cannot be converted to a float.
    """
    while True:
        try:
            user_input = input(prompt)
            return float(user_input)
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def main() -> None:
    """
    Main function for the calculator application.
    Prompts the user for two numbers, calculates (a + b) * 2, and prints the result.
    """
    print("Welcome to the Comprehensive Calculator!")
    print("This application calculates (a + b) * 2.\n")

    try:
        # Get user inputs
        num1 = get_number_input("Enter the first number: ")
        num2 = get_number_input("Enter the second number: ")

        # Calculate the result
        result = add_and_double(num1, num2)

        # Display the result
        print(f"\nThe result of ({num1} + {num2}) * 2 is: {result}")

    except Exception as e:
        # Catch any unexpected errors
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()