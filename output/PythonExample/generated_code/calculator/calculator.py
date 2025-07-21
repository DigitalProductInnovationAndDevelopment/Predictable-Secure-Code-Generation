# File: code.py

import sys
from calculator.calculator import Calculator


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

### Explanation:
1. **Menu Display**: The `display_menu` function provides a clear and user-friendly menu.
2. **Input Validation**: The `get_user_choice` function ensures the user enters a valid choice.
3. **Error Handling**: Each operation includes error handling for invalid inputs and division by zero.
4. **Modular Design**: Functions are modular and reusable, adhering to the existing structure.
5. **Integration**: The `Calculator` class from `calculator/calculator.py` is used for all operations.