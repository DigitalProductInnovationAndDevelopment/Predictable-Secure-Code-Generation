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
        # Ensure inputs are numeric
        result = a * b
        return result
    except TypeError as e:
        raise ValueError("Both inputs must be numeric.") from e

def main():
    """
    Main function to handle user input and output for multiplication.
    """
    try:
        # Prompt the user for input
        print("Multiplication Calculator")
        first_input = input("Enter the first number: ")
        second_input = input("Enter the second number: ")

        # Convert inputs to floats
        num1 = float(first_input)
        num2 = float(second_input)

        # Perform multiplication
        result = multiply_numbers(num1, num2)

        # Display the result
        print(f"The result of multiplying {num1} and {num2} is: {result}")
    except ValueError as e:
        print(f"Input Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Thank you for using the calculator.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by the user.")
        sys.exit(0)