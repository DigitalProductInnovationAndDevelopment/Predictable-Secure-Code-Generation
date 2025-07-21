# Calculator Project

A simple Python calculator project that provides basic mathematical operations.

## Features

- Basic arithmetic operations (addition, subtraction, multiplication, division)
- List sum calculation
- Input validation and error handling
- Comprehensive test coverage

## Installation

1. Clone or navigate to this directory
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Operations

```python
from calculator import Calculator

calc = Calculator()

# Basic arithmetic
result = calc.add(5, 3)  # Returns 8
result = calc.subtract(10, 4)  # Returns 6
result = calc.multiply(6, 7)  # Returns 42
result = calc.divide(20, 5)  # Returns 4.0

# List operations
result = calc.sum_list([1, 2, 3, 4, 5])  # Returns 15
```

### Command Line Interface

Run the main script to see example calculations:

```bash
python main.py
```

## Testing

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=calculator
```

## Code Quality

Format code with Black:

```bash
black .
```

Check code style with flake8:

```bash
flake8 .
```

## Project Structure

```
code/
├── calculator/
│   ├── __init__.py
│   └── calculator.py
├── tests/
│   ├── __init__.py
│   └── test_calculator.py
├── main.py
├── requirements.txt
└── README.md
```

## License

This project is open source and available under the MIT License.
