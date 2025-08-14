import pytest
from req_009 import Calculator, CalculatorError


class TestCalculator:
    @pytest.mark.parametrize(
        "a, b, expected",
        [
            (1, 1, 2),  # Basic addition
            (-1, -1, -2),  # Negative numbers
            (1.5, 2.5, 4.0),  # Floats
            (0, 0, 0),  # Zero addition
            (1e10, 1e10, 2e10),  # Large numbers
        ],
    )
    def test_add(self, a, b, expected):
        assert Calculator.add(a, b) == expected

    @pytest.mark.parametrize(
        "a, b, expected",
        [
            (5, 3, 2),  # Basic subtraction
            (-5, -3, -2),  # Negative numbers
            (5.5, 2.5, 3.0),  # Floats
            (0, 0, 0),  # Zero subtraction
            (1e10, 1e9, 9e9),  # Large numbers
        ],
    )
    def test_subtract(self, a, b, expected):
        assert Calculator.subtract(a, b) == expected

    @pytest.mark.parametrize(
        "a, b, expected",
        [
            (2, 3, 6),  # Basic multiplication
            (-2, -3, 6),  # Negative numbers
            (2.5, 4, 10.0),  # Floats
            (0, 5, 0),  # Multiplication with zero
            (1e5, 1e5, 1e10),  # Large numbers
        ],
    )
    def test_multiply(self, a, b, expected):
        assert Calculator.multiply(a, b) == expected

    @pytest.mark.parametrize(
        "a, b, expected",
        [
            (6, 3, 2),  # Basic division
            (-6, -3, 2),  # Negative numbers
            (7.5, 2.5, 3.0),  # Floats
            (1e10, 1e5, 1e5),  # Large numbers
        ],
    )
    def test_divide(self, a, b, expected):
        assert Calculator.divide(a, b) == expected

    def test_divide_by_zero(self):
        with pytest.raises(CalculatorError, match="Division by zero is not allowed."):
            Calculator.divide(10, 0)

    @pytest.mark.parametrize(
        "a, b",
        [
            ("10", 5),  # Invalid type for a
            (10, "5"),  # Invalid type for b
            (None, 5),  # None as input
            (10, None),  # None as input
        ],
    )
    def test_invalid_inputs(self, a, b):
        with pytest.raises(TypeError):
            Calculator.add(a, b)
        with pytest.raises(TypeError):
            Calculator.subtract(a, b)
        with pytest.raises(TypeError):
            Calculator.multiply(a, b)
        with pytest.raises(TypeError):
            Calculator.divide(a, b)

    def test_custom_exception(self):
        # Ensure CalculatorError is a subclass of Exception
        assert issubclass(CalculatorError, Exception)

    def test_zero_edge_cases(self):
        # Test operations involving zero
        assert Calculator.add(0, 0) == 0
        assert Calculator.subtract(0, 0) == 0
        assert Calculator.multiply(0, 0) == 0
        assert Calculator.multiply(0, 5) == 0
        assert Calculator.add(0, 5) == 5
        assert Calculator.subtract(5, 0) == 5


# Run the tests using pytest
if __name__ == "__main__":
    pytest.main()