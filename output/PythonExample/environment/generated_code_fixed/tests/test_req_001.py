import pytest
from io import StringIO
from unittest.mock import patch
from req_001 import add_numbers, main


# Test cases for add_numbers function
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (1, 2, 3),  # Normal case with integers
        (1.5, 2.5, 4.0),  # Normal case with floats
        (1, 2.5, 3.5),  # Mixed integer and float
        (0, 0, 0),  # Edge case with zeros
        (-1, -2, -3),  # Negative integers
        (-1.5, -2.5, -4.0),  # Negative floats
        (1e10, 1e10, 2e10),  # Large numbers
        (1e-10, 1e-10, 2e-10),  # Small numbers
    ],
)
def test_add_numbers_valid(a, b, expected):
    """Test add_numbers with valid inputs."""
    assert add_numbers(a, b) == expected


@pytest.mark.parametrize(
    "a, b, expected_exception, expected_message",
    [
        ("1", 2, ValueError, "Invalid input types"),  # String input
        (1, "2", ValueError, "Invalid input types"),  # String input
        (None, 2, ValueError, "Invalid input types"),  # None input
        (1, None, ValueError, "Invalid input types"),  # None input
        ([1], 2, ValueError, "Invalid input types"),  # List input
        (1, {2}, ValueError, "Invalid input types"),  # Set input
    ],
)
def test_add_numbers_invalid(a, b, expected_exception, expected_message):
    """Test add_numbers with invalid inputs."""
    with pytest.raises(expected_exception) as excinfo:
        add_numbers(a, b)
    assert expected_message in str(excinfo.value)


# Test cases for main function
def test_main_valid_inputs():
    """Test main function with valid inputs."""
    user_inputs = ["3", "4"]
    expected_output = (
        "Welcome to the calculator!\n" "The result of adding 3 and 4 is: 7\n"
    )

    with patch("builtins.input", side_effect=user_inputs), patch(
        "sys.stdout", new_callable=StringIO
    ) as mock_stdout:
        main()
        assert mock_stdout.getvalue() == expected_output


def test_main_invalid_inputs():
    """Test main function with invalid inputs."""
    user_inputs = ["abc", "4"]
    expected_output = (
        "Welcome to the calculator!\n"
        "Input Error: Both inputs must be numeric values.\n"
    )

    with patch("builtins.input", side_effect=user_inputs), patch(
        "sys.stdout", new_callable=StringIO
    ) as mock_stdout, patch("sys.stderr", new_callable=StringIO) as mock_stderr:
        main()
        assert (
            "Input Error: Both inputs must be numeric values." in mock_stderr.getvalue()
        )


def test_main_unexpected_error():
    """Test main function with unexpected error."""
    user_inputs = ["3", None]  # Simulate unexpected error
    expected_output = (
        "Welcome to the calculator!\n"
        "An unexpected error occurred: unsupported operand type(s) for +: 'int' and 'NoneType'\n"
    )

    with patch("builtins.input", side_effect=user_inputs), patch(
        "sys.stdout", new_callable=StringIO
    ) as mock_stdout, patch("sys.stderr", new_callable=StringIO) as mock_stderr:
        main()
        assert "An unexpected error occurred" in mock_stderr.getvalue()


def test_main_edge_case_zero():
    """Test main function with edge case inputs (zero)."""
    user_inputs = ["0", "0"]
    expected_output = (
        "Welcome to the calculator!\n" "The result of adding 0 and 0 is: 0\n"
    )

    with patch("builtins.input", side_effect=user_inputs), patch(
        "sys.stdout", new_callable=StringIO
    ) as mock_stdout:
        main()
        assert mock_stdout.getvalue() == expected_output
