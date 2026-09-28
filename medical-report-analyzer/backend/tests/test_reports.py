"""PDF upload, extraction, and analysis integration tests."""

from pathlib import Path

from fastapi.testclient import TestClient

from tests.conftest import auth_headers


def test_upload_and_analyze_report(client: TestClient, register_user) -> None:
    patient = register_user()
    headers = auth_headers(patient)
    sample_pdf = Path(__file__).parents[2] / "test_report_aditya.pdf"

    with sample_pdf.open("rb") as report_file:
        upload = client.post(
            "/reports/upload",
            headers=headers,
            files={"file": (sample_pdf.name, report_file, "application/pdf")},
        )

    assert upload.status_code == 201, upload.text
    report_id = upload.json()["id"]

    analysis = client.post(f"/analysis/{report_id}", headers=headers)
    assert analysis.status_code == 200, analysis.text
    assert analysis.json()["status"] == "analyzed"

    result = client.get(f"/analysis/{report_id}", headers=headers)
    assert result.status_code == 200
    assert result.json()["summary"]
    assert result.json()["disease_risks"]["diabetes"]["level"] == "Insufficient Data"

    reports = client.get("/reports/list", headers=headers)
    assert reports.status_code == 200
    assert any(item["id"] == report_id and item["has_analysis"] for item in reports.json())


def test_upload_rejects_non_pdf(client: TestClient, register_user) -> None:
    patient = register_user()
    response = client.post(
        "/reports/upload",
        headers=auth_headers(patient),
        files={"file": ("notes.txt", b"not a PDF", "text/plain")},
    )

    assert response.status_code == 400


def test_upload_rejects_fake_pdf(client: TestClient, register_user) -> None:
    patient = register_user()
    response = client.post(
        "/reports/upload",
        headers=auth_headers(patient),
        files={"file": ("fake.pdf", b"not really a PDF", "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "The uploaded file is not a valid PDF document."
