"""
Tests for HandleGeneric package.

This module contains all test files and test utilities.
"""

__version__ = "1.0.0"

# Test configuration
import pytest
import sys
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import test modules
from .test_core import *
from .test_providers import *
from .test_modules import *
from .test_utils import *
from .test_integration import *
