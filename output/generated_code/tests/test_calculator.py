"""
Test cases for the Calculator class.
"""
import logging
import datetime
from typing import List, Union
from typing import Union

import pytest
from calculator.calculator import Calculator


class TestCalculator:
    """Test cases for Calculator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.calc = Calculator()

    def test_add_integers(self):
        """Test addition with integers."""
        assert self.calc.add(5, 3) == 8
        assert self.calc.add(-1, 1) == 0
        assert self.calc.add(0, 0) == 0

    def test_add_floats(self):
        """Test addition with floats."""
        assert self.calc.add(5.5, 3.2) == 8.7
        assert self.calc.add(-1.5, 1.5) == 0.0
        assert self.calc.add(0.1, 0.2) == pytest.approx(0.3)

    def test_subtract_integers(self):
        """Test subtraction with integers."""
        assert self.calc.subtract(5, 3) == 2
        assert self.calc.subtract(1, 1) == 0
        assert self.calc.subtract(0, 5) == -5

    def test_subtract_floats(self):
        """Test subtraction with floats."""
        assert self.calc.subtract(5.5, 3.2) == 2.3
        assert self.calc.subtract(1.0, 1.0) == 0.0
        assert self.calc.subtract(0.1, 0.2) == pytest.approx(-0.1)

    def test_multiply_integers(self):
        """Test multiplication with integers."""
        assert self.calc.multiply(5, 3) == 15
        assert self.calc.multiply(-2, 3) == -6
        assert self.calc.multiply(0, 5) == 0

    def test_multiply_floats(self):
        """Test multiplication with floats."""
        assert self.calc.multiply(2.5, 2.0) == 5.0
        assert self.calc.multiply(-1.5, 2.0) == -3.0
        assert self.calc.multiply(0.1, 0.2) == 0.02

    def test_multiply_type_error(self):
        """Test multiplication with invalid types."""
        with pytest.raises(TypeError):
            self.calc.multiply("5", 3)
        with pytest.raises(TypeError):
            self.calc.multiply(5, "3")

    def test_divide_integers(self):
        """Test division with integers."""
        assert self.calc.divide(6, 2) == 3.0
        assert self.calc.divide(5, 2) == 2.5
        assert self.calc.divide(0, 5) == 0.0

    def test_divide_floats(self):
        """Test division with floats."""
        assert self.calc.divide(6.0, 2.0) == 3.0
        assert self.calc.divide(5.0, 2.0) == 2.5
        assert self.calc.divide(0.0, 5.0) == 0.0

    def test_divide_by_zero(self):
        """Test division by zero."""
        with pytest.raises(ValueError, match="Division by zero is not allowed"):
            self.calc.divide(5, 0)

    def test_divide_type_error(self):
        """Test division with invalid types."""
        with pytest.raises(TypeError):
            self.calc.divide("6", 2)
        with pytest.raises(TypeError):
            self.calc.divide(6, "2")

    def test_add_and_multiply_by_two(self):
        """Test add_and_multiply_by_two method."""
        assert self.calc.add_and_multiply_by_two(3, 2) == 10
        assert self.calc.add_and_multiply_by_two(-1, 1) == 0
        assert self.calc.add_and_multiply_by_two(0.5, 0.5) == 2.0

    def test_add_and_multiply_by_two_type_error(self):
        """Test add_and_multiply_by_two with invalid types."""
        with pytest.raises(TypeError):
            self.calc.add_and_multiply_by_two("3", 2)
        with pytest.raises(TypeError):
            self.calc.add_and_multiply_by_two(3, "2")

    def test_sum_list_integers(self):
        """Test sum_list with integers."""
        assert self.calc.sum_list([1, 2, 3, 4, 5]) == 15
        assert self.calc.sum_list([-1, 1]) == 0
        assert self.calc.sum_list([0]) == 0

    def test_sum_list_floats(self):
        """Test sum_list with floats."""
        assert self.calc.sum_list([1.5, 2.5, 3.0]) == 7.0
        assert self.calc.sum_list([-1.5, 1.5]) == 0.0
        assert self.calc.sum_list([0.1, 0.2, 0.3]) == pytest.approx(0.6)

    def test_sum_list_mixed(self):
        """Test sum_list with mixed integer and float values."""
        assert self.calc.sum_list([1, 2.5, 3]) == 6.5
        assert self.calc.sum_list([0, 1.5, -1.5]) == 0.0

    def test_sum_list_empty(self):
        """Test sum_list with empty list."""
        with pytest.raises(ValueError, match="The list cannot be empty"):
            self.calc.sum_list([])

    def test_sum_list_not_list(self):
        """Test sum_list with non-list input."""
        with pytest.raises(TypeError, match="Input must be a list"):
            self.calc.sum_list("1,2,3")
        with pytest.raises(TypeError, match="Input must be a list"):
            self.calc.sum_list(123)

    def test_sum_list_non_numeric(self):
        """Test sum_list with non-numeric elements."""
        with pytest.raises(TypeError, match="All elements in the list must be numeric"):
            self.calc.sum_list([1, 2, "3"])
        with pytest.raises(TypeError, match="All elements in the list must be numeric"):
            self.calc.sum_list([1, None, 3])
