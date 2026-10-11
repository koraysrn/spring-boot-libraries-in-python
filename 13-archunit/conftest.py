import os
import sys

import pytest

# Make the local modules importable when pytest runs from this folder.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from arch import ArchitectureRules


@pytest.fixture
def rules():
    return ArchitectureRules()
