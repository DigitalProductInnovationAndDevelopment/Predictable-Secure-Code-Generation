import pytest
from req_010 import Calculator, CalculatorError


class TestCalculator:
    """
    Test suite for the Calculator class.
    """

    @pytest.mark.parametrize(
        "numbers, expected_sum",
        [
            ([1, 2, 3, 4], 10),  # Normal case with positive integers
            ([1.5, 2.5, 3.5], 7.5),  # Normal case with floats
            ([0, 0, 0], 0),  # Edge case with all zeros
            ([-1, -2, -3], -6),  # Edge case with negative numbers
            ([1, -1, 2, -2], 0),  # Mixed positive and negative numbers
            ([1000000, 2000000, 3000000], 6000000),  # Large numbers
            ([0.1, 0.2, 0.3], 0.6),  # Floating-point precision
        ],
    )
    def test_sum_numbers_valid(self, numbers, expected_sum):
        """
        Test the sum_numbers method with valid inputs.
        """
        result = Calculator.sum_numbers(numbers)
        assert result == pytest.approx(expected_sum), f"Expected {expected_sum}, got {result}"

    def test_sum_numbers_empty_list(self):
        """
        Test the sum_numbers method with an empty list, expecting a CalculatorError.
        """
        with pytest.raises(CalculatorError, match="Cannot calculate the sum of an empty list."):
            Calculator.sum_numbers([])

    def test_sum_numbers_single_element(self):
        """
        Test the sum_numbers method with a single-element list.
        """
        result = Calculator.sum_numbers([42])
        assert result == 42, "Expected the sum to be the single element in the list."

    def test_sum_numbers_large_list(self):
        """
        Test the sum_numbers method with a large list of numbers.
        """
        large_list = [1] * 1000000  # A list of one million ones
        result = Calculator.sum_numbers(large_list)
        assert result == 1000000, "Expected the sum to be the size of the list."

    def test_sum_numbers_invalid_input(self):
        """
        Test the sum_numbers method with invalid input types.
        """
        with pytest.raises(TypeError):
            Calculator.sum_numbers("not a list")  # Passing a string instead of a list

        with pytest.raises(TypeError):
            Calculator.sum_numbers(123)  # Passing a number instead of a list

        with pytest.raises(TypeError):
            Calculator.sum_numbers(None)  # Passing None instead of a list

    def test_sum_numbers_nested_list(self):
        """
        Test the sum_numbers method with a nested list, expecting a TypeError.
        """
        with pytest.raises(TypeError):
            Calculator.sum_numbers([1, [2, 3], 4])  # Nested list is not supported


# Run the tests using pytest
if __name__ == "__main__":
    pytest.main()