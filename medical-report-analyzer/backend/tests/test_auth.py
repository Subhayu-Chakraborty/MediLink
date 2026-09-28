"""Authentication and role-security integration tests."""

from uuid import uuid4

from fastapi.testclient import TestClient

from tests.conftest import auth_headers


def test_register_and_read_current_patient(
    client: TestClient,
    register_user,
) -> None:
    patient = register_user(age=32, gender="female")
    response = client.get("/auth/me", headers=auth_headers(patient))

    assert response.status_code == 200
    assert response.json()["role"] == "patient"


def test_login_and_reject_wrong_password(client: TestClient) -> None:
    email = f"login-{uuid4().hex}@example.com"
    registration = {
        "full_name": "Login Patient",
        "email": email,
        "password": "Pass123!",
        "role": "patient",
    }
    assert client.post("/auth/register", json=registration).status_code == 201

    login = client.post(
        "/auth/login",
        json={"email": email.upper(), "password": "Pass123!"},
    )
    wrong = client.post(
        "/auth/login",
        json={"email": email, "password": "wrong-password"},
    )

    assert login.status_code == 200
    assert login.json()["access_token"]
    assert wrong.status_code == 401


def test_public_registration_rejects_admin_role(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Unauthorized Admin",
            "email": f"admin-{uuid4().hex}@example.com",
            "password": "Pass123!",
            "role": "admin",
        },
    )

    assert response.status_code == 422
