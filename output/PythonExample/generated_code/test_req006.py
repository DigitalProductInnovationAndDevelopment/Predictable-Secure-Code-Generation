Here is the updated and comprehensive test suite for the `Calculator` class, ensuring all requirements are met:

# File: tests/test_calculator.py

import pytest
from calculator.calculator import Calculator


class TestCalculator:
    """Test suite for the Calculator class."""

    # --- Tests for add() ---
    def test_add_integers(self):
        assert Calculator.add(2, 3) == 5

    def test_add_floats(self):
        assert Calculator.add(2.5, 3.5) == 6.0

    def test_add_negative_numbers(self):
        assert Calculator.add(-2, -3) == -5

    def test_add_zero(self):
        assert Calculator.add(0, 5) == 5

    def test_add_type_error(self):
        with pytest.raises(ValueError, match="Both inputs must be numeric"):
            Calculator.add(2, "three")

    # --- Tests for subtract() ---
    def test_subtract_integers(self):
        assert Calculator.subtract(5, 3) == 2

    def test_subtract_floats(self):
        assert Calculator.subtract(5.5, 3.5) == 2.0

    def test_subtract_negative_numbers(self):
        assert Calculator.subtract(-5, -3) == -2

    def test_subtract_zero(self):
        assert Calculator.subtract(5, 0) == 5

    def test_subtract_type_error(self):
        with pytest.raises(ValueError, match="Both inputs must be numeric"):
            Calculator.subtract(5, "three")

    # --- Tests for multiply() ---
    def test_multiply_integers(self):
        assert Calculator.multiply(2, 3) == 6

    def test_multiply_floats(self):
        assert Calculator.multiply(2.5, 3.5) == 8.75

    def test_multiply_negative_numbers(self):
        assert Calculator.multiply(-2, -3) == 6

    def test_multiply_by_zero(self):
        assert Calculator.multiply(5, 0) == 0

    def test_multiply_type_error(self):
        with pytest.raises(ValueError, match="Both inputs must be numeric"):
            Calculator.multiply(2, "three")

    # --- Tests for divide() ---
    def test_divide_integers(self):
        assert Calculator.divide(6, 3) == 2.0

    def test_divide_floats(self):
        assert Calculator.divide(7.5, 2.5) == 3.0

    def test_divide_negative_numbers(self):
        assert Calculator.divide(-6, -3) == 2.0

    def test_divide_by_zero(self):
        with pytest.raises(ValueError, match="Division by zero is not allowed"):
            Calculator.divide(6, 0)

    def test_divide_type_error(self):
        with pytest.raises(ValueError, match="Both inputs must be numeric"):
            Calculator.divide(6, "three")

    # --- Tests for add_and_multiply_by_two() ---
    def test_add_and_multiply_by_two(self):
        assert Calculator.add_and_multiply_by_two(2, 3) == 10

    def test_add_and_multiply_by_two_negative_numbers(self):
        assert Calculator.add_and_multiply_by_two(-2, -3) == -10

    def test_add_and_multiply_by_two_zero(self):
        assert Calculator.add_and_multiply_by_two(0, 0) == 0

    def test_add_and_multiply_by_two_type_error(self):
        with pytest.raises(ValueError, match="Both inputs must be numeric"):
            Calculator.add_and_multiply_by_two(2, "three")

    # --- Tests for sum_list() ---
    def test_sum_list_integers(self):
        assert Calculator.sum_list([1, 2, 3]) == 6

    def test_sum_list_floats(self):
        assert Calculator.sum_list([1.5, 2.5, 3.5]) == 7.5

    def test_sum_list_mixed(self):
        assert Calculator.sum_list([1, 2.5, 3]) == 6.5

    def test_sum_list_empty(self):
        assert Calculator.sum_list([]) == 0

    def test_sum_list_negative_numbers(self):
        assert Calculator.sum_list([-1, -2, -3]) == -6

    def test_sum_list_not_list(self):
        with pytest.raises(ValueError, match="Input must be a list"):
            Calculator.sum_list("not a list")

    def test_sum_list_non_numeric(self):
        with pytest.raises(ValueError, match="All elements in the list must be numeric"):
            Calculator.sum_list([1, "two", 3])

    def test_sum_list_nested_list(self):
        with pytest.raises(ValueError, match="All elements in the list must be numeric"):
            Calculator.sum_list([1, [2, 3], 4])

    def test_sum_list_large_numbers(self):
        assert Calculator.sum_list([1e10, 2e10, 3e10]) == 6e10

### Explanation of the Test Cases:
1. **Normal Functionality**:
   - Tests for valid inputs (integers, floats, mixed types) for all methods.
   - Includes edge cases like zero and negative numbers.

2. **Edge Cases**:
   - Tests for empty lists in `sum_list`.
   - Tests for large numbers in `sum_list`.
   - Tests for zero in arithmetic operations.

3. **Error Conditions**:
   - Tests for invalid types (e.g., strings, nested lists).
   - Tests for division by zero.
   - Tests for non-list inputs in `sum_list`.

4. **Setup**:
   - Proper imports are included.
   - Each test is isolated and uses `pytest.raises` to validate exceptions.

This test suite ensures comprehensive coverage of the `Calculator` class functionality and input validation.