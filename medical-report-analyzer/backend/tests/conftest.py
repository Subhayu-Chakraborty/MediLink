"""Shared integration fixtures for the FastAPI backend."""

from __future__ import annotations

import os
from typing import Callable
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# Tests must never read or write the developer's persistent Atlas database.
os.environ["USE_IN_MEMORY_DB"] = "true"
os.environ["DATABASE_NAME"] = "medical_report_analyzer_test"
os.environ["AI_MODE"] = "offline"

from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def register_user(client: TestClient) -> Callable[..., dict]:
    def register(role: str = "patient", **overrides: object) -> dict:
        unique = uuid4().hex
        payload: dict[str, object] = {
            "full_name": f"Test {role.title()}",
            "email": f"{role}-{unique}@example.com",
            "password": "Pass123!",
            "role": role,
        }
        if role == "doctor":
            payload["specialization"] = "General Medicine"
        payload.update(overrides)

        response = client.post("/auth/register", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return register


def auth_headers(token_response: dict) -> dict[str, str]:
    return {"Authorization": f"Bearer {token_response['access_token']}"}
