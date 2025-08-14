import pytest
from unittest.mock import patch
from io import StringIO
from req_002 import subtract_numbers, main


# Test cases for subtract_numbers function
def test_subtract_numbers_normal_cases():
    # Test normal subtraction
    assert subtract_numbers(10, 5) == 5
    assert subtract_numbers(0, 0) == 0
    assert subtract_numbers(-5, -3) == -2
    assert subtract_numbers(5.5, 2.2) == 3.3


def test_subtract_numbers_edge_cases():
    # Test subtraction with very large numbers
    assert subtract_numbers(1e308, 1e308) == 0
    assert subtract_numbers(-1e308, 1e308) == -2e308

    # Test subtraction with very small numbers
    assert subtract_numbers(1e-308, 1e-308) == 0
    assert subtract_numbers(-1e-308, 1e-308) == -2e-308


def test_subtract_numbers_invalid_inputs():
    # Test invalid inputs
    with pytest.raises(ValueError, match="Both inputs must be numbers."):
        subtract_numbers("a", 5)
    with pytest.raises(ValueError, match="Both inputs must be numbers."):
        subtract_numbers(5, "b")
    with pytest.raises(ValueError, match="Both inputs must be numbers."):
        subtract_numbers("a", "b")
    with pytest.raises(ValueError, match="Both inputs must be numbers."):
        subtract_numbers(None, 5)
    with pytest.raises(ValueError, match="Both inputs must be numbers."):
        subtract_numbers(5, None)


# Test cases for main function
def test_main_normal_case():
    # Simulate user input and capture output
    user_input = "10\n5\n"
    expected_output = (
        "Welcome to the Comprehensive Calculator - Subtraction Module\n"
        "Enter the first number (minuend): Enter the second number (subtrahend): "
        "The result of 10.0 - 5.0 is 5.0\n"
    )
    with patch("builtins.input", side_effect=user_input.splitlines()), patch(
        "sys.stdout", new_callable=StringIO
    ) as mock_stdout:
        main()
        assert mock_stdout.getvalue() == expected_output


def test_main_invalid_input():
    # Simulate invalid user input and capture output
    user_input = "abc\n5\n"
    expected_output = (
        "Welcome to the Comprehensive Calculator - Subtraction Module\n"
        "Enter the first number (minuend): Error: could not convert string to float: 'abc'\n"
    )
    with patch("builtins.input", side_effect=user_input.splitlines()), patch(
        "sys.stdout", new_callable=StringIO
    ) as mock_stdout:
        main()
        assert expected_output in mock_stdout.getvalue()


def test_main_unexpected_error():
    # Simulate unexpected error (e.g., input function is mocked to raise an exception)
    with patch("builtins.input", side_effect=Exception("Unexpected error")), patch(
        "sys.stderr", new_callable=StringIO
    ) as mock_stderr:
        main()
        assert (
            "An unexpected error occurred: Unexpected error" in mock_stderr.getvalue()
        )


def test_main_edge_case_zero_subtraction():
    # Simulate user input for zero subtraction and capture output
    user_input = "0\n0\n"
    expected_output = (
        "Welcome to the Comprehensive Calculator - Subtraction Module\n"
        "Enter the first number (minuend): Enter the second number (subtrahend): "
        "The result of 0.0 - 0.0 is 0.0\n"
    )
    with patch("builtins.input", side_effect=user_input.splitlines()), patch(
        "sys.stdout", new_callable=StringIO
    ) as mock_stdout:
        main()
        assert mock_stdout.getvalue() == expected_output


def test_main_negative_numbers():
    # Simulate user input for negative numbers and capture output
    user_input = "-10\n-5\n"
    expected_output = (
        "Welcome to the Comprehensive Calculator - Subtraction Module\n"
        "Enter the first number (minuend): Enter the second number (subtrahend): "
        "The result of -10.0 - -5.0 is -5.0\n"
    )
    with patch("builtins.input", side_effect=user_input.splitlines()), patch(
        "sys.stdout", new_callable=StringIO
    ) as mock_stdout:
        main()
        assert mock_stdout.getvalue() == expected_output
