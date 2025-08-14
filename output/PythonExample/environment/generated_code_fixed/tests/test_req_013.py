import pytest
from req_013 import calculate_square_root

# Test cases for calculate_square_root function
@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        (0, 0),  # Edge case: square root of 0
        (1, 1),  # Square root of 1
        (4, 2),  # Perfect square
        (9, 3),  # Perfect square
        (2, 1.41421356237),  # Non-perfect square
        (0.25, 0.5),  # Fractional input
        (100, 10),  # Larger perfect square
    ],
)
def test_calculate_square_root_valid(input_value, expected_output):
    """
    Test calculate_square_root with valid inputs.
    """
    result = calculate_square_root(input_value)
    assert pytest.approx(result, rel=1e-9) == expected_output


@pytest.mark.parametrize(
    "input_value",
    [
        -1,  # Negative number
        -0.01,  # Small negative number
        -100,  # Large negative number
    ],
)
def test_calculate_square_root_negative(input_value):
    """
    Test calculate_square_root with negative inputs, which should raise ValueError.
    """
    with pytest.raises(ValueError, match="Cannot calculate the square root of a negative number."):
        calculate_square_root(input_value)


def test_calculate_square_root_invalid_type():
    """
    Test calculate_square_root with invalid input types.
    """
    with pytest.raises(TypeError):
        calculate_square_root("string")  # Invalid type: string

    with pytest.raises(TypeError):
        calculate_square_root(None)  # Invalid type: None

    with pytest.raises(TypeError):
        calculate_square_root([4])  # Invalid type: list

    with pytest.raises(TypeError):
        calculate_square_root({"number": 4})  # Invalid type: dictionary


# Mocking input/output for main function
def test_main_valid_input(monkeypatch, capsys):
    """
    Test the main function with valid user input.
    """
    from req_013 import main

    # Mock user input
    monkeypatch.setattr("builtins.input", lambda _: "16")

    # Run the main function
    main()

    # Capture the output
    captured = capsys.readouterr()

    # Assert the output contains the expected result
    assert "The square root of 16.0 is 4.00000" in captured.out
    assert "Thank you for using the Square Root Calculator!" in captured.out


def test_main_invalid_input(monkeypatch, capsys):
    """
    Test the main function with invalid user input (non-numeric).
    """
    from req_013 import main

    # Mock user input
    monkeypatch.setattr("builtins.input", lambda _: "invalid")

    # Run the main function
    main()

    # Capture the output
    captured = capsys.readouterr()

    # Assert the output contains the expected error message
    assert "Error: could not convert string to float: 'invalid'" in captured.out
    assert "Thank you for using the Square Root Calculator!" in captured.out


def test_main_negative_input(monkeypatch, capsys):
    """
    Test the main function with a negative number as input.
    """
    from req_013 import main

    # Mock user input
    monkeypatch.setattr("builtins.input", lambda _: "-9")

    # Run the main function
    main()

    # Capture the output
    captured = capsys.readouterr()

    # Assert the output contains the expected error message
    assert "Error: Cannot calculate the square root of a negative number." in captured.out
    assert "Thank you for using the Square Root Calculator!" in captured.out


def test_main_unexpected_error(monkeypatch, capsys):
    """
    Test the main function with an unexpected error (e.g., input causing a crash).
    """
    from req_013 import main

    # Mock user input to raise an unexpected error
    def mock_input(prompt):
        raise RuntimeError("Unexpected error")

    monkeypatch.setattr("builtins.input", mock_input)

    # Run the main function
    main()

    # Capture the output
    captured = capsys.readouterr()

    # Assert the output contains the unexpected error message
    assert "An unexpected error occurred: Unexpected error" in captured.out
    assert "Thank you for using the Square Root Calculator!" in captured.out