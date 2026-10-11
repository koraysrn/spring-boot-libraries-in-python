import os
import sys
from unittest.mock import Mock

import pytest

# Make the local modules importable when pytest runs from this folder.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service import AccountService, Repository


@pytest.fixture
def mock_repository():
    return Mock(spec=Repository)


@pytest.fixture
def service(mock_repository):
    return AccountService(mock_repository)
