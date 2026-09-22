"""
tests/conftest.py
──────────────────
pytest fixtures shared across all test modules.

Provides:
  - A FastAPI TestClient configured with an in-memory test database.
  - Helper fixtures for creating test users (patient and doctor).

# TODO: Implement in Phase 1
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

# TODO: Implement in Phase 1 — override database dependency for testing


@pytest.fixture(scope="session")
def client() -> TestClient:
    """FastAPI test client fixture."""
    # TODO: Implement in Phase 1
    return TestClient(app)
