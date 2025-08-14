import pytest
from typing import Union
from your_module_name import multiply_numbers  # Replace 'your_module_name' with the actual module name

# Test cases for normal scenarios
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (2, 3, 6),                # Two positive integers
        (-2, 3, -6),              # One negative and one positive integer
        (2.5, 4, 10.0),           # Float and integer
        (0, 5, 0),                # Zero and positive integer
        (0, 0, 0),                # Zero and zero
        (1.5, 2.5, 3.75),         # Two positive floats
        (-1.5, -2.5, 3.75),       # Two negative floats
        (1e10, 1e10, 1e20),       # Large numbers
        (1e-10, 1e-10, 1e-20),    # Small numbers
    ],
)
def test_multiply_numbers_valid_inputs(a: Union[int, float], b: Union[int, float], expected: Union[int, float]):
    """Test multiply_numbers with valid inputs."""
    result = multiply_numbers(a, b)
    assert result == expected, f"Expected {expected}, but got {result}"

# Test cases for invalid inputs
@pytest.mark.parametrize(
    "a, b, expected_exception, expected_message",
    [
        ("2", 3, ValueError, "Invalid input types: str, int. Must be int or float."),  # String and integer
        (2, "3", ValueError, "Invalid input types: int, str. Must be int or float."),  # Integer and string
        (None, 3, ValueError, "Invalid input types: NoneType, int. Must be int or float."),  # None and integer
        (2, None, ValueError, "Invalid input types: int, NoneType. Must be int or float."),  # Integer and None
        ([2], 3, ValueError, "Invalid input types: list, int. Must be int or float."),  # List and integer
        (2, {3}, ValueError, "Invalid input types: int, set. Must be int or float."),  # Integer and set
    ],
)
def test_multiply_numbers_invalid_inputs(a, b, expected_exception, expected_message):
    """Test multiply_numbers with invalid inputs."""
    with pytest.raises(expected_exception) as exc_info:
        multiply_numbers(a, b)
    assert str(exc_info.value) == expected_message, f"Expected message '{expected_message}', but got '{str(exc_info.value)}'"

# Test cases for edge cases
def test_multiply_numbers_edge_cases():
    """Test multiply_numbers with edge cases."""
    # Multiplying by infinity
    assert multiply_numbers(float('inf'), 2) == float('inf')
    assert multiply_numbers(2, float('inf')) == float('inf')
    assert multiply_numbers(float('-inf'), 2) == float('-inf')
    assert multiply_numbers(2, float('-inf')) == float('-inf')

    # Multiplying by NaN
    assert multiply_numbers(float('nan'), 2) != multiply_numbers(float('nan'), 2)  # NaN is not equal to itself
    assert multiply_numbers(2, float('nan')) != multiply_numbers(2, float('nan'))

# Test cases for unexpected exceptions
def test_multiply_numbers_unexpected_exception_handling(monkeypatch):
    """Test multiply_numbers for unexpected exceptions."""
    def mock_isinstance(obj, types):
        raise RuntimeError("Unexpected error in isinstance")

    monkeypatch.setattr("builtins.isinstance", mock_isinstance)

    with pytest.raises(RuntimeError) as exc_info:
        multiply_numbers(2, 3)
    assert str(exc_info.value) == "Unexpected error in isinstance"

# Test cases for large numbers
def test_multiply_numbers_large_numbers():
    """Test multiply_numbers with very large numbers."""
    large_num1 = 1e308
    large_num2 = 2
    result = multiply_numbers(large_num1, large_num2)
    assert result == float('inf'), "Expected result to be infinity for overflow"

# Test cases for small numbers
def test_multiply_numbers_small_numbers():
    """Test multiply_numbers with very small numbers."""
    small_num1 = 1e-308
    small_num2 = 1e-308
    result = multiply_numbers(small_num1, small_num2)
    assert result == 0, "Expected result to be 0 due to underflow"

# Run the tests
if __name__ == "__main__":
    pytest.main()