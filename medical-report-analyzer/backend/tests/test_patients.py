"""Patient profile integration tests."""

from fastapi.testclient import TestClient

from tests.conftest import auth_headers


def test_patient_can_update_profile(client: TestClient, register_user) -> None:
    patient = register_user()
    headers = auth_headers(patient)

    response = client.patch(
        "/patients/profile",
        headers=headers,
        json={
            "age": 44,
            "blood_group": "O+",
            "address": "Kolkata",
            "emergency_contact": "+91-9000000000",
        },
    )

    assert response.status_code == 200
    assert response.json()["blood_group"] == "O+"
    assert client.get("/patients/profile", headers=headers).json()["age"] == 44


def test_doctor_cannot_access_patient_profile(
    client: TestClient,
    register_user,
) -> None:
    doctor = register_user(role="doctor")
    response = client.get("/patients/profile", headers=auth_headers(doctor))

    assert response.status_code == 403
