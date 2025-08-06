# Here is a comprehensive set of pytest test cases for the provided `code.py` file. These test cases cover normal functionality, edge cases, and error conditions.

# File: test_code.py

import pytest
from code import store_in_memory, recall_memory, clear_memory


def test_store_in_memory_and_recall():
    """
    Test storing a value in memory and recalling it.
    """
    # Store a value
    store_in_memory(42.5)
    # Recall the value and assert correctness
    assert recall_memory() == 42.5


def test_clear_memory():
    """
    Test clearing the memory.
    """
    # Store a value
    store_in_memory(100.0)
    # Clear the memory
    clear_memory()
    # Assert that memory is cleared (reset to 0.0)
    assert recall_memory() == 0.0


def test_store_in_memory_with_integer():
    """
    Test storing an integer value in memory.
    """
    # Store an integer value
    store_in_memory(10)
    # Recall the value and assert correctness
    assert recall_memory() == 10.0  # Should be converted to float


def test_store_in_memory_with_negative_value():
    """
    Test storing a negative value in memory.
    """
    # Store a negative value
    store_in_memory(-25.75)
    # Recall the value and assert correctness
    assert recall_memory() == -25.75


def test_store_in_memory_with_zero():
    """
    Test storing zero in memory.
    """
    # Store zero
    store_in_memory(0)
    # Recall the value and assert correctness
    assert recall_memory() == 0.0


def test_store_in_memory_with_large_value():
    """
    Test storing a very large value in memory.
    """
    large_value = 1e100
    # Store a large value
    store_in_memory(large_value)
    # Recall the value and assert correctness
    assert recall_memory() == large_value


def test_store_in_memory_with_invalid_type():
    """
    Test storing a non-numeric value in memory, which should raise a ValueError.
    """
    with pytest.raises(
        ValueError, match="Only numeric values can be stored in memory."
    ):
        store_in_memory("invalid")  # Passing a string


def test_store_in_memory_with_none():
    """
    Test storing None in memory, which should raise a ValueError.
    """
    with pytest.raises(
        ValueError, match="Only numeric values can be stored in memory."
    ):
        store_in_memory(None)


def test_memory_persistence():
    """
    Test that memory persists until explicitly cleared.
    """
    # Store a value
    store_in_memory(55.5)
    # Recall the value and assert correctness
    assert recall_memory() == 55.5
    # Recall again to ensure persistence
    assert recall_memory() == 55.5


def test_memory_reset_after_clear():
    """
    Test that memory is reset to 0.0 after clearing.
    """
    # Store a value
    store_in_memory(123.45)
    # Clear the memory
    clear_memory()
    # Assert that memory is reset
    assert recall_memory() == 0.0


def test_multiple_operations():
    """
    Test a sequence of operations: store, recall, clear, and recall again.
    """
    # Store a value
    store_in_memory(75.25)
    # Recall the value and assert correctness
    assert recall_memory() == 75.25
    # Clear the memory
    clear_memory()
    # Recall again and assert memory is cleared
    assert recall_memory() == 0.0


def test_store_in_memory_with_float_edge_cases():
    """
    Test storing edge case float values in memory.
    """
    # Store positive infinity
    store_in_memory(float("inf"))
    assert recall_memory() == float("inf")

    # Store negative infinity
    store_in_memory(float("-inf"))
    assert recall_memory() == float("-inf")

    # Store NaN (Not a Number)
    store_in_memory(float("nan"))
    assert recall_memory() != recall_memory()  # NaN is not equal to itself


# Run the tests
if __name__ == "__main__":
    pytest.main()

### Explanation of Test Cases:
# 1. **Normal Functionality**:
#    - `test_store_in_memory_and_recall`: Tests storing and recalling a value.
#    - `test_clear_memory`: Tests clearing the memory.
#    - `test_store_in_memory_with_integer`: Tests storing an integer value.
#    - `test_store_in_memory_with_negative_value`: Tests storing a negative value.
#    - `test_store_in_memory_with_zero`: Tests storing zero.
#    - `test_store_in_memory_with_large_value`: Tests storing a very large value.

# 2. **Edge Cases**:
#    - `test_store_in_memory_with_float_edge_cases`: Tests storing special float values like infinity and NaN.
#    - `test_memory_persistence`: Ensures memory persists until explicitly cleared.
#    - `test_memory_reset_after_clear`: Ensures memory is reset after clearing.

# 3. **Error Conditions**:
#    - `test_store_in_memory_with_invalid_type`: Tests storing a non-numeric value (e.g., string).
#    - `test_store_in_memory_with_none`: Tests storing `None`.

# 4. **Sequence of Operations**:
#    - `test_multiple_operations`: Tests a sequence of operations (store, recall, clear, recall again).

# ### Notes:
# - The `pytest.raises` context manager is used to test error conditions.
# - Edge cases like `float('inf')`, `float('-inf')`, and `float('nan')` are tested to ensure robustness.
# - The tests are designed to be independent and comprehensive.
