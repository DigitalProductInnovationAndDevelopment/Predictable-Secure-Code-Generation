import pytest
from io import StringIO
import sys
from divide_module import divide_numbers  # Assuming the code is saved in a file named divide_module.py

@pytest.mark.parametrize(
    "dividend, divisor, expected_result",
    [
        (10, 2, 5.0),          # Normal case with integers
        (10.0, 2.0, 5.0),      # Normal case with floats
        (7, 3, 7 / 3),         # Division resulting in a float
        (-10, 2, -5.0),        # Negative dividend
        (10, -2, -5.0),        # Negative divisor
        (-10, -2, 5.0),        # Both negative
        (0, 5, 0.0),           # Zero dividend
        (5, 0.5, 10.0),        # Divisor is a fraction
    ]
)
def test_divide_numbers_valid_cases(dividend, divisor, expected_result):
    """
    Test divide_numbers with valid inputs.
    """
    result = divide_numbers(dividend, divisor)
    assert result == pytest.approx(expected_result), f"Expected {expected_result}, got {result}"


@pytest.mark.parametrize(
    "dividend, divisor",
    [
        (10, 0),               # Division by zero
        (10.0, 0),             # Division by zero with float
    ]
)
def test_divide_numbers_division_by_zero(dividend, divisor):
    """
    Test divide_numbers for division by zero.
    """
    result = divide_numbers(dividend, divisor)
    assert result is None, "Expected None for division by zero"


@pytest.mark.parametrize(
    "dividend, divisor",
    [
        ("10", 2),             # Invalid type for dividend
        (10, "2"),             # Invalid type for divisor
        ("10", "2"),           # Both arguments are invalid types
        (None, 2),             # None as dividend
        (10, None),            # None as divisor
        ([], 2),               # List as dividend
        (10, {}),              # Dictionary as divisor
    ]
)
def test_divide_numbers_invalid_types(dividend, divisor):
    """
    Test divide_numbers with invalid input types.
    """
    result = divide_numbers(dividend, divisor)
    assert result is None, "Expected None for invalid input types"


def test_divide_numbers_error_messages(capsys):
    """
    Test that appropriate error messages are printed to stderr.
    """
    # Test division by zero
    divide_numbers(10, 0)
    captured = capsys.readouterr()
    assert "Division by zero is not allowed." in captured.err

    # Test invalid input types
    divide_numbers("10", 2)
    captured = capsys.readouterr()
    assert "Invalid input types" in captured.err


def test_main_function_valid_input(monkeypatch, capsys):
    """
    Test the main function with valid inputs.
    """
    inputs = iter(["10", "2"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("sys.stdout", StringIO())  # Suppress stdout for cleaner test output

    from divide_module import main  # Import main function
    main()

    captured = capsys.readouterr()
    assert "The result of dividing 10.0 by 2.0 is: 5.0" in captured.out


def test_main_function_invalid_input(monkeypatch, capsys):
    """
    Test the main function with invalid inputs.
    """
    inputs = iter(["abc", "2"])  # Invalid dividend
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("sys.stdout", StringIO())  # Suppress stdout for cleaner test output

    from divide_module import main  # Import main function
    main()

    captured = capsys.readouterr()
    assert "Error: Please enter valid numeric inputs." in captured.err


def test_main_function_division_by_zero(monkeypatch, capsys):
    """
    Test the main function with division by zero.
    """
    inputs = iter(["10", "0"])  # Division by zero
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("sys.stdout", StringIO())  # Suppress stdout for cleaner test output

    from divide_module import main  # Import main function
    main()

    captured = capsys.readouterr()
    assert "Division by zero is not allowed." in captured.err


def test_main_function_non_numeric_divisor(monkeypatch, capsys):
    """
    Test the main function with a non-numeric divisor.
    """
    inputs = iter(["10", "abc"])  # Invalid divisor
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("sys.stdout", StringIO())  # Suppress stdout for cleaner test output

    from divide_module import main  # Import main function
    main()

    captured = capsys.readouterr()
    assert "Error: Please enter valid numeric inputs." in captured.err