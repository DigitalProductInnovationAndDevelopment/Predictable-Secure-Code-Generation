# Below is a comprehensive set of `pytest` test cases for the `power` function implemented in both `calculator/calculator.py` and `code.py`. The test cases cover normal functionality, edge cases, and error conditions.

### Test File: `tests/test_power.py`

import pytest
from calculator.calculator import Calculator
from code import power


# Test cases for normal functionality
@pytest.mark.parametrize(
    "base, exponent, expected",
    [
        (2, 3, 8),  # Positive base, positive exponent
        (5, 0, 1),  # Any base raised to the power of 0 is 1
        (2, -2, 0.25),  # Positive base, negative exponent
        (-2, 3, -8),  # Negative base, odd positive exponent
        (-2, 2, 4),  # Negative base, even positive exponent
        (10, 1, 10),  # Any base raised to the power of 1 is itself
        (1, 100, 1),  # 1 raised to any power is 1
        (0.5, 2, 0.25),  # Fractional base, positive exponent
        (4, 0.5, 2),  # Square root (exponent = 0.5)
    ],
)
def test_power_normal_cases(base, exponent, expected):
    # Test Calculator.power
    assert Calculator.power(base, exponent) == pytest.approx(expected, rel=1e-9)
    # Test standalone power function
    assert power(base, exponent) == pytest.approx(expected, rel=1e-9)


# Test cases for edge cases
@pytest.mark.parametrize(
    "base, exponent, expected",
    [
        (0, 0, 1),  # 0^0 is mathematically ambiguous but often defined as 1
        (0, 5, 0),  # 0 raised to any positive power is 0
    ],
)
def test_power_edge_cases(base, exponent, expected):
    # Test Calculator.power
    assert Calculator.power(base, exponent) == pytest.approx(expected, rel=1e-9)
    # Test standalone power function
    assert power(base, exponent) == pytest.approx(expected, rel=1e-9)


# Test cases for error conditions
@pytest.mark.parametrize(
    "base, exponent",
    [
        (0, -1),  # 0 raised to a negative power is undefined
        (0, -5),  # 0 raised to a negative power is undefined
    ],
)
def test_power_error_conditions(base, exponent):
    # Test Calculator.power
    with pytest.raises(
        ValueError, match="Base cannot be zero when the exponent is negative."
    ):
        Calculator.power(base, exponent)
    # Test standalone power function
    with pytest.raises(
        ValueError, match="Base cannot be zero when the exponent is negative."
    ):
        power(base, exponent)


# Test cases for large numbers
@pytest.mark.parametrize(
    "base, exponent, expected",
    [
        (10, 10, 1e10),  # Large positive exponent
        (2, 100, 1.2676506002282294e30),  # Very large exponent
    ],
)
def test_power_large_numbers(base, exponent, expected):
    # Test Calculator.power
    assert Calculator.power(base, exponent) == pytest.approx(expected, rel=1e-9)
    # Test standalone power function
    assert power(base, exponent) == pytest.approx(expected, rel=1e-9)


# Test cases for fractional exponents
@pytest.mark.parametrize(
    "base, exponent, expected",
    [
        (9, 0.5, 3),  # Square root
        (27, 1 / 3, 3),  # Cube root
        (16, 0.25, 2),  # Fourth root
    ],
)
def test_power_fractional_exponents(base, exponent, expected):
    # Test Calculator.power
    assert Calculator.power(base, exponent) == pytest.approx(expected, rel=1e-9)
    # Test standalone power function
    assert power(base, exponent) == pytest.approx(expected, rel=1e-9)


### Explanation of Test Cases

# 1. **Normal Functionality**:
#    - Tests common scenarios such as positive and negative bases, positive and negative exponents, fractional bases, and special cases like `base^0` and `base^1`.

# 2. **Edge Cases**:
#    - Covers edge cases like `0^0` (often defined as 1) and `0` raised to a positive power.

# 3. **Error Conditions**:
#    - Ensures that a `ValueError` is raised when the base is `0` and the exponent is negative, as this is mathematically undefined.

# 4. **Large Numbers**:
#    - Tests the function's ability to handle large bases and exponents without overflow or precision issues.

# 5. **Fractional Exponents**:
#    - Tests cases where the exponent is a fraction, such as square roots, cube roots, and other fractional powers.

# ### Notes:
# - **`pytest.approx`**: Used for floating-point comparisons to handle precision issues.
# - **`pytest.mark.parametrize`**: Used to parameterize test cases for better readability and maintainability.
# - **Error Matching**: The `match` argument in `pytest.raises` ensures that the correct error message is raised.

# ### Running the Tests
# To run the tests, execute the following command in the terminal:
# pytest tests/test_power.py
