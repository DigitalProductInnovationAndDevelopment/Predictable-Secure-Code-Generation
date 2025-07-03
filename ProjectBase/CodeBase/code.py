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

# Example usage
if __name__ == "__main__":
    # Test the functions
    print(f"Addition: 5 + 3 = {addition(5, 3)}")
    print(f"Subtraction: 5 - 3 = {subtraction(5, 3)}")

    print(f"Addition: 10.5 + 2.3 = {addition(10.5, 2.3)}")
    print(f"Subtraction: 10.5 - 2.3 = {subtraction(10.5, 2.3)}")
