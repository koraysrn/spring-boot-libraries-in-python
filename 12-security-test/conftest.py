import os
import sys

import pytest
from fastapi.testclient import TestClient

# Make the local modules importable when pytest runs from this folder.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, get_current_user


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def override_current_user():
    """Override get_current_user and always clear it afterwards."""

    def setter(user):
        app.dependency_overrides[get_current_user] = lambda: user

    yield setter
    app.dependency_overrides.clear()
