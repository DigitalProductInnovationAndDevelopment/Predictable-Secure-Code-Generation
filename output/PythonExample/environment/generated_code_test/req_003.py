import sys

def multiply_numbers(a: float, b: float) -> float:
    """
    Multiply two numbers and return the result.

    Args:
        a (float): The first number to multiply.
        b (float): The second number to multiply.

    Returns:
        float: The product of the two numbers.

    Raises:
        ValueError: If inputs are not valid numbers.
    """
    try:
        # Ensure both inputs are numbers
        a = float(a)
        b = float(b)
        return a * b
    except ValueError:
        raise ValueError("Both inputs must be valid numbers.")

def main():
    """
    Main function to execute the calculator.
    Demonstrates the multiply_numbers function with user input.
    """
    try:
        print("Welcome to the Calculator: Multiply Two Numbers")
        # Get user input
        num1 = input("Enter the first number: ").strip()
        num2 = input("Enter the second number: ").strip()

        # Perform multiplication
        result = multiply_numbers(num1, num2)
        print(f"The result of multiplying {num1} and {num2} is: {result}")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        # Catch any other unforeseen errors
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Exiting the calculator. Goodbye!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting...")
        sys.exit(0)