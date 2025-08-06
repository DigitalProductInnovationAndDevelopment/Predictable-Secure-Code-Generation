# Here is the updated and comprehensive test suite for the `Calculator.factorial` method. The test cases cover normal functionality, edge cases, and error conditions.

# File: tests/test_calculator.py

import pytest
from calculator.calculator import Calculator


class TestCalculator:
    """
    Unit tests for the Calculator class.
    """

    # Normal functionality tests
    def test_factorial_positive_integer(self):
        """
        Test factorial of a positive integer.
        """
        assert Calculator.factorial(5) == 120
        assert Calculator.factorial(6) == 720
        assert Calculator.factorial(10) == 3628800

    # Edge case tests
    def test_factorial_zero(self):
        """
        Test factorial of zero.
        """
        assert Calculator.factorial(0) == 1

    def test_factorial_one(self):
        """
        Test factorial of one.
        """
        assert Calculator.factorial(1) == 1

    # Error condition tests
    def test_factorial_negative_integer(self):
        """
        Test factorial of a negative integer raises ValueError.
        """
        with pytest.raises(
            ValueError, match="Factorial is not defined for negative numbers."
        ):
            Calculator.factorial(-1)
        with pytest.raises(
            ValueError, match="Factorial is not defined for negative numbers."
        ):
            Calculator.factorial(-10)

    def test_factorial_non_integer(self):
        """
        Test factorial of a non-integer raises TypeError.
        """
        with pytest.raises(TypeError, match="Input must be an integer."):
            Calculator.factorial(5.5)
        with pytest.raises(TypeError, match="Input must be an integer."):
            Calculator.factorial("string")
        with pytest.raises(TypeError, match="Input must be an integer."):
            Calculator.factorial(None)
        with pytest.raises(TypeError, match="Input must be an integer."):
            Calculator.factorial([5])
        with pytest.raises(TypeError, match="Input must be an integer."):
            Calculator.factorial({5: "value"})

    # Additional edge case tests
    def test_factorial_large_number(self):
        """
        Test factorial of a large number to ensure it handles large results.
        """
        assert Calculator.factorial(20) == 2432902008176640000
        assert Calculator.factorial(15) == 1307674368000

    def test_factorial_boundary_case(self):
        """
        Test factorial at the boundary of valid input (e.g., 2).
        """
        assert Calculator.factorial(2) == 2
        assert Calculator.factorial(3) == 6


### Explanation of the Test Cases

# 1. **Normal Functionality Tests**:
#    - `test_factorial_positive_integer`: Tests the factorial of typical positive integers like 5, 6, and 10.

# 2. **Edge Case Tests**:
#    - `test_factorial_zero`: Tests the factorial of 0, which should return 1.
#    - `test_factorial_one`: Tests the factorial of 1, which should also return 1.
#    - `test_factorial_large_number`: Tests the factorial of large numbers like 20 and 15 to ensure the function handles large results correctly.
#    - `test_factorial_boundary_case`: Tests the factorial of small positive integers like 2 and 3 to ensure correctness at the boundary of valid input.

# 3. **Error Condition Tests**:
#    - `test_factorial_negative_integer`: Ensures that a `ValueError` is raised when a negative integer is passed.
#    - `test_factorial_non_integer`: Ensures that a `TypeError` is raised when the input is not an integer (e.g., float, string, list, dictionary, or `None`).

# ### How to Run the Tests
# To run the tests, use the following command in the terminal:
# pytest tests/test_calculator.py

# This will execute all the test cases and provide a detailed report of the results.
