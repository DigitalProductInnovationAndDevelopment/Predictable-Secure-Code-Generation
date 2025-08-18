#!/usr/bin/env python3
"""
Main script to demonstrate the Calculator functionality.
"""

from calculator import Calculator


def main():
    """Main function to demonstrate calculator operations."""
    print("🧮 Calculator Demo")
    print("=" * 50)

    # Create calculator instance
    calc = Calculator()

    # Basic arithmetic operations
    print("\n📊 Basic Arithmetic Operations:")
    print("-" * 30)

    # Addition
    result = calc.add(5, 3)
    print(f"Addition: 5 + 3 = {result}")

    result = calc.add(10.5, 2.3)
    print(f"Addition: 10.5 + 2.3 = {result}")

    # Subtraction
    result = calc.subtract(10, 4)
    print(f"Subtraction: 10 - 4 = {result}")

    result = calc.subtract(5.5, 2.3)
    print(f"Subtraction: 5.5 - 2.3 = {result}")

    # Multiplication
    result = calc.multiply(6, 7)
    print(f"Multiplication: 6 × 7 = {result}")

    result = calc.multiply(2.5, 3.0)
    print(f"Multiplication: 2.5 × 3.0 = {result}")

    # Division
    result = calc.divide(20, 5)
    print(f"Division: 20 ÷ 5 = {result}")

    result = calc.divide(15, 4)
    print(f"Division: 15 ÷ 4 = {result}")

    # Special operations
    print("\n🔢 Special Operations:")
    print("-" * 30)

    # Add and multiply by two
    result = calc.add_and_multiply_by_two(3, 2)
    print(f"Add and multiply by 2: (3 + 2) × 2 = {result}")

    result = calc.add_and_multiply_by_two(0.5, 0.5)
    print(f"Add and multiply by 2: (0.5 + 0.5) × 2 = {result}")

    # List operations
    print("\n📋 List Operations:")
    print("-" * 30)

    numbers = [1, 2, 3, 4, 5]
    result = calc.sum_list(numbers)
    print(f"Sum of {numbers} = {result}")

    float_numbers = [1.5, 2.5, 3.0, 4.0]
    result = calc.sum_list(float_numbers)
    print(f"Sum of {float_numbers} = {result}")

    mixed_numbers = [1, 2.5, 3, 4.5]
    result = calc.sum_list(mixed_numbers)
    print(f"Sum of {mixed_numbers} = {result}")

    # Error handling examples
    print("\n⚠️  Error Handling Examples:")
    print("-" * 30)

    try:
        calc.divide(10, 0)
    except ValueError as e:
        print(f"Division by zero error: {e}")

    try:
        calc.multiply("5", 3)
    except TypeError as e:
        print(f"Type error: {e}")

    try:
        calc.sum_list([])
    except ValueError as e:
        print(f"Empty list error: {e}")

    try:
        calc.sum_list([1, 2, "3"])
    except TypeError as e:
        print(f"Non-numeric list error: {e}")

    print("\n✅ Demo completed successfully!")


if __name__ == "__main__":
    main()
