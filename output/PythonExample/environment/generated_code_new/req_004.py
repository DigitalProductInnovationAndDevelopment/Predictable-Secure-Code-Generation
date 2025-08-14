import sys
from typing import Union


def divide_numbers(dividend: Union[int, float], divisor: Union[int, float]) -> Union[float, str]:
    """
    Divides two numbers and returns the result.

    Args:
        dividend (Union[int, float]): The number to be divided (numerator).
        divisor (Union[int, float]): The number by which the dividend is divided (denominator).

    Returns:
        Union[float, str]: The result of the division if successful, or an error message if division fails.

    Raises:
        ValueError: If inputs are not numeric.
    """
    try:
        # Validate input types
        if not isinstance(dividend, (int, float)) or not isinstance(divisor, (int, float)):
            raise ValueError("Both dividend and divisor must be numbers (int or float).")

        # Perform division
        result = dividend / divisor
        return result

    except ZeroDivisionError:
        return "Error: Division by zero is not allowed."

    except ValueError as ve:
        return f"Error: {ve}"

    except Exception as e:
        # Handle any other unforeseen exceptions
        return f"An unexpected error occurred: {e}"


def main():
    """
    Main function to interact with the user for dividing two numbers.
    """
    try:
        print("Welcome to the Calculator Application - Division Module")
        dividend = float(input("Enter the dividend (numerator): "))
        divisor = float(input("Enter the divisor (denominator): "))

        # Perform the division
        result = divide_numbers(dividend, divisor)
        print(f"Result: {result}")

    except ValueError:
        print("Error: Invalid input. Please enter numeric values.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Thank you for using the calculator. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()