import pytest
from req_012 import add, subtract, multiply, divide, calculator


class TestAdd:
    @pytest.mark.parametrize(
        "a, b, expected",
        [
            (1, 2, 3),
            (-1, -2, -3),
            (1.5, 2.5, 4.0),
            (0, 0, 0),
            (1e10, 1e10, 2e10),
        ],
    )
    def test_add(self, a, b, expected):
        assert add(a, b) == expected


class TestSubtract:
    @pytest.mark.parametrize(
        "a, b, expected",
        [
            (5, 3, 2),
            (-5, -3, -2),
            (1.5, 0.5, 1.0),
            (0, 0, 0),
            (1e10, 1e9, 9e9),
        ],
    )
    def test_subtract(self, a, b, expected):
        assert subtract(a, b) == expected


class TestMultiply:
    @pytest.mark.parametrize(
        "a, b, expected",
        [
            (2, 3, 6),
            (-2, -3, 6),
            (1.5, 2, 3.0),
            (0, 5, 0),
            (1e5, 1e5, 1e10),
        ],
    )
    def test_multiply(self, a, b, expected):
        assert multiply(a, b) == expected


class TestDivide:
    @pytest.mark.parametrize(
        "a, b, expected",
        [
            (6, 3, 2),
            (-6, -3, 2),
            (1.5, 0.5, 3.0),
            (0, 5, 0),
            (1e10, 1e5, 1e5),
        ],
    )
    def test_divide(self, a, b, expected):
        assert divide(a, b) == expected

    def test_divide_by_zero(self):
        with pytest.raises(ValueError, match="Division by zero is not allowed."):
            divide(5, 0)


class TestCalculator:
    @pytest.mark.parametrize(
        "operation, a, b, expected",
        [
            (add, 1, 2, 3),
            (subtract, 5, 3, 2),
            (multiply, 2, 3, 6),
            (divide, 6, 3, 2),
        ],
    )
    def test_calculator(self, operation, a, b, expected):
        assert calculator(operation, a, b) == expected

    def test_calculator_divide_by_zero(self):
        with pytest.raises(ValueError, match="Division by zero is not allowed."):
            calculator(divide, 5, 0)

    def test_calculator_invalid_operation(self):
        with pytest.raises(TypeError):
            calculator(None, 5, 3)