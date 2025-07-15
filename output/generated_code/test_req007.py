Below is the updated `tests/test_calculator.py` file rewritten using `pytest` to meet the requirements for comprehensive test cases. The test cases cover normal functionality, edge cases, and error conditions.

# File: tests/test_calculator.py

import pytest
from calculator.calculator import Calculator


class TestCalculator:
    """
    Test suite for the Calculator class.
    """

    @pytest.fixture
    def calc(self):
        """
        Fixture to create a Calculator instance for testing.
        """
        return Calculator()

    # Test cases for the add method
    def test_add(self, calc):
        assert calc.add(2, 3) == 5
        assert calc.add(-2, 3) == 1
        assert calc.add(0, 0) == 0
        assert calc.add(1.5, 2.5) == 4.0

    # Test cases for the subtract method
    def test_subtract(self, calc):
        assert calc.subtract(5, 3) == 2
        assert calc.subtract(3, 5) == -2
        assert calc.subtract(0, 0) == 0
        assert calc.subtract(2.5, 1.5) == 1.0

    # Test cases for the multiply method
    def test_multiply(self, calc):
        assert calc.multiply(2, 3) == 6
        assert calc.multiply(-2, 3) == -6
        assert calc.multiply(0, 5) == 0
        assert calc.multiply(1.5, 2) == 3.0

    # Test cases for the divide method
    def test_divide(self, calc):
        assert calc.divide(6, 3) == 2
        assert calc.divide(5, 2) == 2.5
        with pytest.raises(ValueError, match="Division by zero is not allowed."):
            calc.divide(6, 0)

    # Test cases for the add_and_multiply_by_two method
    def test_add_and_multiply_by_two(self, calc):
        assert calc.add_and_multiply_by_two(2, 3) == 10
        assert calc.add_and_multiply_by_two(-2, 3) == 2
        assert calc.add_and_multiply_by_two(0, 0) == 0
        assert calc.add_and_multiply_by_two(1.5, 2.5) == 8.0

    # Test cases for the sum_list method
    def test_sum_list(self, calc):
        assert calc.sum_list([1, 2, 3, 4]) == 10
        assert calc.sum_list([-1, -2, -3, -4]) == -10
        assert calc.sum_list([]) == 0
        assert calc.sum_list([1.5, 2.5, 3.5]) == 7.5

    # Edge case tests for sum_list
    def test_sum_list_edge_cases(self, calc):
        assert calc.sum_list([0]) == 0
        assert calc.sum_list([1]) == 1
        assert calc.sum_list([1, -1]) == 0

    # Edge case tests for divide
    def test_divide_edge_cases(self, calc):
        assert calc.divide(0, 1) == 0
        assert calc.divide(1, 1) == 1
        assert calc.divide(-1, 1) == -1

    # Test logging functionality indirectly
    def test_logging_functionality(self, calc, caplog):
        with caplog.at_level("INFO"):
            calc.add(2, 3)
            calc.subtract(5, 3)
            calc.multiply(2, 3)
            calc.divide(6, 3)
            calc.add_and_multiply_by_two(2, 3)
            calc.sum_list([1, 2, 3, 4])

        # Check that logs are generated for each operation
        assert "Performed addition: 2 + 3 = 5" in caplog.text
        assert "Performed subtraction: 5 - 3 = 2" in caplog.text
        assert "Performed multiplication: 2 * 3 = 6" in caplog.text
        assert "Performed division: 6 / 3 = 2.0" in caplog.text
        assert "Performed add and multiply by two: (2 + 3) * 2 = 10" in caplog.text
        assert "Performed sum of list: [1, 2, 3, 4] = 10" in caplog.text

### Explanation of the Test Cases
1. **Normal Functionality**:
   - Each method (`add`, `subtract`, `multiply`, `divide`, `add_and_multiply_by_two`, `sum_list`) is tested with typical inputs to ensure correct results.

2. **Edge Cases**:
   - For `add`, `subtract`, and `multiply`, edge cases like zero, negative numbers, and floating-point numbers are tested.
   - For `divide`, edge cases like division by zero (raises `ValueError`), division of zero, and negative numbers are tested.
   - For `sum_list`, edge cases like an empty list, a single-element list, and a list with mixed positive and negative numbers are tested.

3. **Error Conditions**:
   - The `divide` method is tested to ensure it raises a `ValueError` when attempting to divide by zero.

4. **Logging Functionality**:
   - The `caplog` pytest fixture is used to capture log messages and verify that the correct log entries are generated for each operation.

### How to Run the Tests
1. Install `pytest` if not already installed:
   pip install pytest

2. Run the tests using the following command:
   pytest tests/test_calculator.py

3. View the test results in the terminal.