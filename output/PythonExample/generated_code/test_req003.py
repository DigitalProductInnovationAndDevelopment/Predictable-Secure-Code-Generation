# Here is the updated and comprehensive test suite for the `Calculator.calculate_percentage` method. The test cases cover normal functionality, edge cases, and error conditions.

# File: tests/test_calculator.py

import pytest
from calculator.calculator import Calculator


class TestCalculator:
    """
    Test suite for the Calculator class.
    """

    # Normal functionality tests
    def test_calculate_percentage_valid(self):
        """
        Test calculate_percentage with valid inputs.
        """
        assert Calculator.calculate_percentage(50, 200) == 25.0
        assert Calculator.calculate_percentage(30, 60) == 50.0
        assert Calculator.calculate_percentage(0, 100) == 0.0
        assert Calculator.calculate_percentage(100, 100) == 100.0
        assert Calculator.calculate_percentage(1, 4) == 25.0

    # Edge case tests
    def test_calculate_percentage_small_values(self):
        """
        Test calculate_percentage with very small values.
        """
        assert Calculator.calculate_percentage(0.0001, 0.0002) == 50.0
        assert Calculator.calculate_percentage(0.0, 0.0001) == 0.0

    def test_calculate_percentage_large_values(self):
        """
        Test calculate_percentage with very large values.
        """
        assert Calculator.calculate_percentage(1e9, 2e9) == 50.0
        assert Calculator.calculate_percentage(1e12, 1e12) == 100.0

    def test_calculate_percentage_negative_values(self):
        """
        Test calculate_percentage with negative values.
        """
        assert Calculator.calculate_percentage(-50, 200) == -25.0
        assert Calculator.calculate_percentage(50, -200) == -25.0
        assert Calculator.calculate_percentage(-50, -200) == 25.0

    def test_calculate_percentage_zero_value(self):
        """
        Test calculate_percentage when value is zero.
        """
        assert Calculator.calculate_percentage(0, 100) == 0.0
        assert Calculator.calculate_percentage(0, 1e9) == 0.0

    # Error condition tests
    def test_calculate_percentage_zero_total(self):
        """
        Test calculate_percentage raises ValueError when total is zero.
        """
        with pytest.raises(
            ValueError, match="Total cannot be zero when calculating percentage."
        ):
            Calculator.calculate_percentage(50, 0)

    def test_calculate_percentage_non_numeric(self):
        """
        Test calculate_percentage raises TypeError for non-numeric inputs.
        """
        with pytest.raises(TypeError, match="Both value and total must be numeric"):
            Calculator.calculate_percentage("50", 200)

        with pytest.raises(TypeError, match="Both value and total must be numeric"):
            Calculator.calculate_percentage(50, "200")

        with pytest.raises(TypeError, match="Both value and total must be numeric"):
            Calculator.calculate_percentage("50", "200")

        with pytest.raises(TypeError, match="Both value and total must be numeric"):
            Calculator.calculate_percentage(None, 200)

        with pytest.raises(TypeError, match="Both value and total must be numeric"):
            Calculator.calculate_percentage(50, None)

    def test_calculate_percentage_infinity(self):
        """
        Test calculate_percentage with infinity values.
        """
        with pytest.raises(
            ValueError, match="Total cannot be zero when calculating percentage."
        ):
            Calculator.calculate_percentage(50, float("inf"))

        with pytest.raises(
            ValueError, match="Total cannot be zero when calculating percentage."
        ):
            Calculator.calculate_percentage(50, float("-inf"))

    def test_calculate_percentage_nan(self):
        """
        Test calculate_percentage with NaN (Not a Number) values.
        """
        with pytest.raises(TypeError, match="Both value and total must be numeric"):
            Calculator.calculate_percentage(float("nan"), 200)

        with pytest.raises(TypeError, match="Both value and total must be numeric"):
            Calculator.calculate_percentage(50, float("nan"))


### Explanation of Test Cases

# 1. **Normal Functionality Tests**:
#    - These tests ensure that the method works correctly for typical inputs, including integers and floats.

# 2. **Edge Case Tests**:
#    - Small values: Tests the method's behavior with very small numbers.
#    - Large values: Tests the method's behavior with very large numbers.
#    - Negative values: Tests the method's behavior when either or both inputs are negative.
#    - Zero value: Tests the method's behavior when the `value` is zero.

# 3. **Error Condition Tests**:
#    - Zero total: Ensures that the method raises a `ValueError` when the `total` is zero.
#    - Non-numeric inputs: Ensures that the method raises a `TypeError` when inputs are not numeric.
#    - Infinity: Ensures that the method handles infinity values appropriately.
#    - NaN: Ensures that the method raises a `TypeError` when inputs are NaN.

# 4. **Comprehensive Coverage**:
#    - The test suite ensures that all edge cases and potential error conditions are covered, providing confidence in the robustness of the `calculate_percentage` method.

# ### Running the Tests
# To run the tests, execute the following command in the terminal:
# pytest tests/test_calculator.py
