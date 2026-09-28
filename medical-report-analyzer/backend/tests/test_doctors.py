"""Doctor discovery, connection, and chat integration tests."""

from fastapi.testclient import TestClient

from tests.conftest import auth_headers


def test_nearby_connection_and_websocket_chat(
    client: TestClient,
    register_user,
) -> None:
    patient = register_user()
    doctor = register_user(
        role="doctor",
        specialization="Cardiology",
        latitude=22.5726,
        longitude=88.3639,
    )
    patient_headers = auth_headers(patient)
    doctor_headers = auth_headers(doctor)

    profile = client.get("/doctors/profile", headers=doctor_headers)
    assert profile.status_code == 200
    doctor_id = profile.json()["doctor_id"]

    nearby = client.get(
        "/doctors/nearby",
        headers=patient_headers,
        params={"lat": 22.5726, "lng": 88.3639, "radius_km": 5},
    )
    assert nearby.status_code == 200
    assert any(item["doctor_id"] == doctor_id for item in nearby.json())

    connection = client.post(
        "/patients/doctor-requests",
        headers=patient_headers,
        json={"doctor_id": doctor_id},
    )
    assert connection.status_code == 201
    request_id = connection.json()["request_id"]

    pending = client.get("/doctors/requests", headers=doctor_headers)
    assert any(item["request_id"] == request_id for item in pending.json())

    accepted = client.patch(
        f"/doctors/requests/{request_id}/respond",
        headers=doctor_headers,
        json={"accept": True},
    )
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "accepted"

    connected = client.get("/doctors/patients", headers=doctor_headers)
    assert connected.status_code == 200
    assert connected.json()[0]["user_id"] == patient["user"]["id"]

    patient_ws_url = f"/chat/ws?token={patient['access_token']}"
    doctor_ws_url = f"/chat/ws?token={doctor['access_token']}"
    with client.websocket_connect(patient_ws_url) as patient_ws:
        with client.websocket_connect(doctor_ws_url) as doctor_ws:
            patient_ws.send_json(
                {
                    "receiver_id": doctor["user"]["id"],
                    "content": "Integration test message",
                }
            )
            patient_event = patient_ws.receive_json()
            doctor_event = doctor_ws.receive_json()

    assert patient_event["type"] == "message"
    assert doctor_event["message"]["content"] == "Integration test message"

    history = client.get(
        f"/chat/messages/{doctor['user']['id']}",
        headers=patient_headers,
    )
    assert history.status_code == 200
    assert history.json()[0]["content"] == "Integration test message"
