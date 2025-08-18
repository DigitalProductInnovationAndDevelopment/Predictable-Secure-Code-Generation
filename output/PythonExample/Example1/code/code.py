def addition(a, b):
    """
    Return the sum of two numbers.

    Args:
        a (int/float): First number
        b (int/float): Second number

    Returns:
        int/float: Sum of a and b
    """
    return a + b


def subtraction(a, b):
    """
    Return the difference of two numbers.

    Args:
        a (int/float): First number
        b (int/float): Second number

    Returns:
        int/float: Difference of a and b (a - b)
    """
    return a - b



def multiply_two_numbers(num1, num2):
    """
    Multiplies two numbers and returns the result.
    
    Args:
        num1 (float or int): The first number to be multiplied.
        num2 (float or int): The second number to be multiplied.
    
    Returns:
        float or int: The product of the two numbers.
    
    Raises:
        TypeError: If either of the inputs is not a number (int or float).
    """
    # Validate input types
    if not isinstance(num1, (int, float)):
        raise TypeError(f"Invalid type for num1: expected int or float, got {type(num1).__name__}")
    if not isinstance(num2, (int, float)):
        raise TypeError(f"Invalid type for num2: expected int or float, got {type(num2).__name__}")
    
    # Perform multiplication
    return num1 * num2


def divide_two_numbers(numerator, denominator):
    """
    Divides two numbers and returns the result.
    
    Args:
        numerator (float): The number to be divided (the dividend).
        denominator (float): The number by which to divide (the divisor).
    
    Returns:
        float: The result of the division.
    
    Raises:
        ValueError: If the denominator is zero.
        TypeError: If either numerator or denominator is not a number.
    """
    # Validate input types
    if not isinstance(numerator, (int, float)):
        raise TypeError("The numerator must be an integer or a float.")
    if not isinstance(denominator, (int, float)):
        raise TypeError("The denominator must be an integer or a float.")
    
    # Handle division by zero
    if denominator == 0:
        raise ValueError("Division by zero is not allowed.")
    
    # Perform the division
    return numerator / denominator


def add_and_multiply_by_two(num1, num2):
    """
    Adds two numbers and multiplies the result by two.
    
    Args:
        num1 (float or int): The first number to be added.
        num2 (float or int): The second number to be added.
    
    Returns:
        float: The result of adding the two numbers and multiplying by two.
    
    Raises:
        TypeError: If either num1 or num2 is not a number (int or float).
    """
    # Validate input types
    if not isinstance(num1, (int, float)):
        raise TypeError(f"Expected num1 to be int or float, got {type(num1).__name__}")
    if not isinstance(num2, (int, float)):
        raise TypeError(f"Expected num2 to be int or float, got {type(num2).__name__}")
    
    # Perform the calculation
    result = (num1 + num2) * 2
    return result


def sum_list_elements(numbers):
    """
    Calculate the sum of all elements in a given list.
    
    Args:
        numbers (list): A list of numeric values to be summed.
    
    Returns:
        float: The sum of all elements in the list.
    
    Raises:
        TypeError: If the input is not a list or if the list contains non-numeric elements.
        ValueError: If the list is empty.
    """
    # Validate input type
    if not isinstance(numbers, list):
        raise TypeError("Input must be a list.")
    
    # Validate list content
    if not all(isinstance(num, (int, float)) for num in numbers):
        raise TypeError("All elements in the list must be numeric (int or float).")
    
    # Validate non-empty list
    if not numbers:
        raise ValueError("The list cannot be empty.")
    
    # Calculate and return the sum
    return sum(numbers)


def is_palindrome(input_string):
    """
    Determines whether a given string is a palindrome or not.
    
    A palindrome is a string that reads the same backward as forward, 
    ignoring case and non-alphanumeric characters.
    
    Args:
        input_string (str): The string to check for palindrome property.
    
    Returns:
        bool: True if the input string is a palindrome, False otherwise.
    
    Raises:
        TypeError: If the input is not a string.
    """
    # Validate input
    if not isinstance(input_string, str):
        raise TypeError("Input must be a string.")
    
    # Normalize the string: remove non-alphanumeric characters and convert to lowercase
    normalized_string = ''.join(char.lower() for char in input_string if char.isalnum())
    
    # Check if the normalized string is equal to its reverse
    return normalized_string == normalized_string[::-1]


def validate_operation_inputs(operation_name, param1, param2):
    """
    Validates the input types for mathematical operations and raises errors for invalid inputs.
    
    Args:
        operation_name (str): The name of the operation (e.g., 'addition', 'subtraction').
        param1 (int or float): The first input value for the operation.
        param2 (int or float): The second input value for the operation.
    
    Raises:
        TypeError: If `operation_name` is not a string.
        ValueError: If `operation_name` is not a recognized operation.
        TypeError: If `param1` or `param2` is not an integer or float.
    """
    # Validate operation_name
    if not isinstance(operation_name, str):
        raise TypeError(f"Expected 'operation_name' to be a string, but got {type(operation_name).__name__}.")
    
    valid_operations = {'addition', 'subtraction'}
    if operation_name not in valid_operations:
        raise ValueError(f"Invalid operation '{operation_name}'. Supported operations are: {', '.join(valid_operations)}.")
    
    # Validate param1 and param2
    if not isinstance(param1, (int, float)):
        raise TypeError(f"Expected 'param1' to be an int or float, but got {type(param1).__name__}.")
    if not isinstance(param2, (int, float)):
        raise TypeError(f"Expected 'param2' to be an int or float, but got {type(param2).__name__}.")


def safe_division(numerator, denominator):
    """
    Safely performs division of two numbers, raising an error if the denominator is zero.
    
    Args:
        numerator (float): The number to be divided (dividend).
        denominator (float): The number by which to divide (divisor).
    
    Returns:
        float: The result of the division if valid.
    
    Raises:
        ValueError: If the denominator is zero.
        TypeError: If either numerator or denominator is not a number.
    """
    # Validate input types
    if not isinstance(numerator, (int, float)):
        raise TypeError("The numerator must be an integer or a float.")
    if not isinstance(denominator, (int, float)):
        raise TypeError("The denominator must be an integer or a float.")
    
    # Check for division by zero
    if denominator == 0:
        raise ValueError("Division by zero is not allowed.")
    
    # Perform the division
    return numerator / denominator


def sum_non_empty_list(numbers):
    """
    Sums the elements of a list, raising an error if the list is empty.
    
    Args:
        numbers (list): A list of numeric values to be summed.
    
    Returns:
        float: The sum of the numeric values in the list.
    
    Raises:
        ValueError: If the input list is empty.
        TypeError: If the input is not a list or contains non-numeric elements.
    """
    # Validate input is a list
    if not isinstance(numbers, list):
        raise TypeError("Input must be a list.")
    
    # Validate the list is not empty
    if not numbers:
        raise ValueError("Cannot sum an empty list.")
    
    # Validate all elements in the list are numeric
    if not all(isinstance(num, (int, float)) for num in numbers):
        raise TypeError("All elements in the list must be numeric.")
    
    # Return the sum of the list
    return sum(numbers)


def sum_numeric_elements(elements):
    """
    Sums a list of numeric elements. Raises a ValueError if any non-numeric 
    element is present in the list.
    
    Args:
        elements (list): A list of elements to be summed. All elements must 
                         be numeric (int or float).
    
    Returns:
        float: The sum of all numeric elements in the list.
    
    Raises:
        ValueError: If the list contains any non-numeric elements.
        TypeError: If the input is not a list.
    """
    # Validate that the input is a list
    if not isinstance(elements, list):
        raise TypeError("Input must be a list.")
    
    # Validate that all elements in the list are numeric
    if not all(isinstance(item, (int, float)) for item in elements):
        raise ValueError("All elements in the list must be numeric (int or float).")
    
    # Calculate and return the sum of numeric elements
    return sum(elements)


def demonstrate_calculator_operations():
    """
    Provides a command-line interface to demonstrate all calculator operations 
    (addition and subtraction) available in the codebase.

    This function allows the user to interactively select an operation, input 
    the required numbers, and view the result. It includes parameter validation 
    and error handling to ensure a smooth user experience.
    
    Returns:
        None
    """
    import sys

    def get_number_input(prompt):
        """
        Helper function to get a valid number input from the user.

        Args:
            prompt (str): The prompt message to display to the user.

        Returns:
            float: The validated number input.
        """
        while True:
            try:
                return float(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def display_menu():
        """
        Displays the available calculator operations to the user.

        Returns:
            None
        """
        print("\nCalculator Operations:")
        print("1. Addition")
        print("2. Subtraction")
        print("3. Exit")

    while True:
        display_menu()
        try:
            choice = input("Select an operation (1/2/3): ").strip()
            if choice == "1":
                # Perform addition
                num1 = get_number_input("Enter the first number: ")
                num2 = get_number_input("Enter the second number: ")
                result = addition(num1, num2)
                print(f"The result of addition is: {result}")
            elif choice == "2":
                # Perform subtraction
                num1 = get_number_input("Enter the first number: ")
                num2 = get_number_input("Enter the second number: ")
                result = subtraction(num1, num2)
                print(f"The result of subtraction is: {result}")
            elif choice == "3":
                print("Exiting the calculator. Goodbye!")
                break
            else:
                print("Invalid choice. Please select a valid option (1/2/3).")
        except Exception as e:
            print(f"An error occurred: {e}. Please try again.")


def add_and_double(num1, num2):
    """
    Adds two numbers and multiplies the result by two.
    
    Args:
        num1 (float): The first number to be added.
        num2 (float): The second number to be added.
    
    Returns:
        float: The result of adding the two numbers and multiplying the sum by two.
    
    Raises:
        TypeError: If either of the inputs is not a number (int or float).
    """
    # Validate input types
    if not isinstance(num1, (int, float)):
        raise TypeError(f"Invalid type for num1: expected int or float, got {type(num1).__name__}")
    if not isinstance(num2, (int, float)):
        raise TypeError(f"Invalid type for num2: expected int or float, got {type(num2).__name__}")
    
    # Perform the calculation
    result = (num1 + num2) * 2
    return result


def process_list(input_list):
    """
    Processes a given list by validating its contents and performing operations as needed.
    
    Args:
        input_list (list): The list to be processed. Must be a list of elements.
    
    Returns:
        list: A processed version of the input list, or an empty list if the input is invalid.
    
    Raises:
        TypeError: If the input is not a list.
        ValueError: If the list contains invalid elements (e.g., None or unsupported types).
    """
    # Validate that the input is a list
    if not isinstance(input_list, list):
        raise TypeError("The input must be a list.")
    
    # Validate that the list does not contain invalid elements
    if any(element is None for element in input_list):
        raise ValueError("The list contains invalid elements (e.g., None).")
    
    # Example processing: Return the list sorted (modify as needed for specific requirements)
    try:
        processed_list = sorted(input_list)
    except TypeError as e:
        raise ValueError(f"List contains elements that cannot be compared: {e}")
    
    return processed_list


def process_string(input_string):
    """
    Processes a given string by validating its type and performing operations as needed.
    
    Args:
        input_string (str): The string to be processed.
    
    Returns:
        str: The processed string.
    
    Raises:
        ValueError: If the input is not a string.
    """
    if not isinstance(input_string, str):
        raise ValueError("The input must be a string.")
    
    # Implementation of string processing logic here
    # For now, we'll return the input string as-is
    return input_string

# Example usage
if __name__ == "__main__":
    # Test the functions
    print(f"Addition: 5 + 3 = {addition(5, 3)}")
    print(f"Subtraction: 5 - 3 = {subtraction(5, 3)}")

    print(f"Addition: 10.5 + 2.3 = {addition(10.5, 2.3)}")
    print(f"Subtraction: 10.5 - 2.3 = {subtraction(10.5, 2.3)}")
