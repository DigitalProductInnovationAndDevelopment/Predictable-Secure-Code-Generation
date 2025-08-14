import pytest
from req_011 import Calculator, CalculatorError

class TestCalculator:
    """Test suite for the Calculator class."""

    @pytest.mark.parametrize(
        "numbers_list, expected_sum",
        [
            ([1, 2, 3, 4], 10),  # Normal case with integers
            ([1.5, 2.5, 3.0], 7.0),  # Normal case with floats
            ([0, 0, 0], 0),  # Edge case with all zeros
            ([100], 100),  # Single element in the list
            ([], 0),  # Edge case with an empty list
            ([-1, -2, -3], -6),  # Negative numbers
            ([1, -1, 2, -2], 0),  # Mixed positive and negative numbers
        ],
    )
    def test_sum_numbers_valid(self, numbers_list, expected_sum):
        """Test sum_numbers with valid numeric inputs."""
        result = Calculator.sum_numbers(numbers_list)
        assert result == expected_sum, f"Expected {expected_sum}, got {result}"

    @pytest.mark.parametrize(
        "numbers_list",
        [
            [1, 2, "a", 4],  # Contains a string
            [1, 2, None, 4],  # Contains None
            [1, 2, [3], 4],  # Contains a list
            [1, 2, {"key": "value"}, 4],  # Contains a dictionary
            [1, 2, (3, 4), 5],  # Contains a tuple
            [1, 2, True, 4],  # Contains a boolean
        ],
    )
    def test_sum_numbers_invalid(self, numbers_list):
        """Test sum_numbers with invalid inputs containing non-numeric elements."""
        with pytest.raises(CalculatorError, match="All elements in the list must be numeric."):
            Calculator.sum_numbers(numbers_list)

    def test_sum_numbers_empty_list(self):
        """Test sum_numbers with an empty list."""
        result = Calculator.sum_numbers([])
        assert result == 0, "Expected sum of an empty list to be 0"

    def test_sum_numbers_large_numbers(self):
        """Test sum_numbers with very large numbers."""
        large_numbers = [1e18, 1e18, -1e18]
        result = Calculator.sum_numbers(large_numbers)
        assert result == 1e18, f"Expected {1e18}, got {result}"

    def test_sum_numbers_mixed_types(self):
        """Test sum_numbers with mixed numeric types (int and float)."""
        mixed_numbers = [1, 2.5, 3, 4.5]
        result = Calculator.sum_numbers(mixed_numbers)
        assert result == 11.0, f"Expected 11.0, got {result}"

    def test_sum_numbers_no_arguments(self):
        """Test sum_numbers with no arguments (should raise a TypeError)."""
        with pytest.raises(TypeError):
            Calculator.sum_numbers()

    def test_sum_numbers_non_iterable(self):
        """Test sum_numbers with a non-iterable input (should raise a TypeError)."""
        with pytest.raises(TypeError):
            Calculator.sum_numbers(123)  # Passing a single integer instead of a list

    def test_sum_numbers_nested_list(self):
        """Test sum_numbers with a nested list (should raise a CalculatorError)."""
        nested_list = [1, 2, [3, 4], 5]
        with pytest.raises(CalculatorError, match="All elements in the list must be numeric."):
            Calculator.sum_numbers(nested_list)

    def test_sum_numbers_boolean_values(self):
        """Test sum_numbers with boolean values (should raise a CalculatorError)."""
        boolean_list = [1, 2, True, 4]
        with pytest.raises(CalculatorError, match="All elements in the list must be numeric."):
            Calculator.sum_numbers(boolean_list)

    def test_sum_numbers_large_list(self):
        """Test sum_numbers with a very large list of numbers."""
        large_list = [1] * 10**6  # A list with one million ones
        result = Calculator.sum_numbers(large_list)
        assert result == 10**6, f"Expected {10**6}, got {result}"