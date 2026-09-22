"""
app/services/report_service.py
───────────────────────────────
Business logic for medical report file handling and CRUD operations.

Architecture: Routes → ReportService → Beanie + file_utils
              ReportService triggers text_extraction_service and ollama_service
              for analysis.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import List

from bson import ObjectId
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings
from app.models.medical_report import MedicalReport, ReportStatus
from app.models.user import User
from app.schemas.report import ReportDetailResponse, ReportListItem, ReportUploadResponse
from app.utils.file_utils import (
    generate_unique_filename,
    save_upload_file,
    validate_content_type,
    validate_file_extension,
)

logger = logging.getLogger(__name__)


def _get_upload_dir() -> Path:
    """Return the resolved upload directory path, creating it if needed."""
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


async def save_report(file: UploadFile, patient_user: User) -> MedicalReport:
    """
    Validate and save an uploaded PDF, then create a MedicalReport document.

    Raises:
        HTTPException 400: invalid file type or size.
    """
    # Validate file extension
    if not validate_file_extension(file.filename or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted. Please upload a .pdf file.",
        )

    # Validate content type
    if not validate_content_type(file.content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only application/pdf is accepted.",
        )

    # Read content and check size
    content = await file.read()
    await file.seek(0)

    max_bytes = settings.max_file_size_bytes
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds the {settings.MAX_FILE_SIZE_MB} MB limit.",
        )

    # Generate unique filename and save to disk
    stored_name = generate_unique_filename(file.filename or "report.pdf")
    upload_dir = _get_upload_dir()
    dest = upload_dir / stored_name
    await save_upload_file(file, dest)

    # Create MedicalReport document
    report = MedicalReport(
        patient=patient_user,  # type: ignore[arg-type]
        original_filename=file.filename or "report.pdf",
        stored_filename=stored_name,
        file_path=str(dest),
        status=ReportStatus.UPLOADED,
    )
    await report.insert()

    logger.info("Report saved: %s → %s", file.filename, stored_name)
    return report


async def list_reports(patient_user_id: str) -> List[ReportListItem]:
    """Return all MedicalReport documents for the authenticated patient."""
    reports = await MedicalReport.find(
        MedicalReport.patient.id == ObjectId(patient_user_id),  # type: ignore[attr-defined]
    ).sort(-MedicalReport.uploaded_at).to_list()

    return [
        ReportListItem(
            id=str(r.id),
            original_filename=r.original_filename,
            status=r.status.value,
            uploaded_at=r.uploaded_at,
            analyzed_at=r.analyzed_at,
            has_analysis=r.analysis_result is not None,
        )
        for r in reports
    ]


async def get_report_by_id(report_id: str, patient_user_id: str) -> ReportDetailResponse:
    """
    Retrieve a single report, verifying patient ownership.

    Raises:
        HTTPException 404: if report not found.
        HTTPException 403: if the authenticated patient does not own it.
    """
    report = await MedicalReport.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")

    await report.fetch_link(MedicalReport.patient)
    patient: User = report.patient  # type: ignore[assignment]
    if str(patient.id) != patient_user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    return ReportDetailResponse(
        id=str(report.id),
        original_filename=report.original_filename,
        status=report.status.value,
        extracted_text=report.extracted_text,
        uploaded_at=report.uploaded_at,
        analyzed_at=report.analyzed_at,
        error_message=report.error_message,
        has_analysis=report.analysis_result is not None,
    )


async def update_report_status(
    report: MedicalReport,
    status_value: ReportStatus,
    extracted_text: str | None = None,
    analysis_result: dict | None = None,
    error_message: str | None = None,
) -> MedicalReport:
    """Helper: update report fields and save."""
    report.status = status_value
    if extracted_text is not None:
        report.extracted_text = extracted_text
    if analysis_result is not None:
        report.analysis_result = analysis_result
        report.analyzed_at = datetime.utcnow()
    if error_message is not None:
        report.error_message = error_message
    await report.save()
    return report


async def get_analysis_result(report_id: str, patient_user_id: str) -> dict:
    """
    Return the stored analysis_result for an analysed report.

    Raises:
        HTTPException 404: report not found.
        HTTPException 403: not the owner.
        HTTPException 422: report not yet analysed.
    """
    report = await MedicalReport.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")

    await report.fetch_link(MedicalReport.patient)
    patient: User = report.patient  # type: ignore[assignment]
    if str(patient.id) != patient_user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    if report.analysis_result is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This report has not been analysed yet. Please trigger analysis first.",
        )

    return report.analysis_result


async def get_patient_report_for_doctor(
    report_id: str, patient_user_id: str
) -> ReportDetailResponse:
    """
    Doctor-accessible version: returns a patient's report (no ownership check —
    caller must have already verified the doctor-patient connection).
    """
    report = await MedicalReport.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")

    await report.fetch_link(MedicalReport.patient)
    patient: User = report.patient  # type: ignore[assignment]
    if str(patient.id) != patient_user_id:
        raise HTTPException(status_code=404, detail="Report not found for this patient.")

    return ReportDetailResponse(
        id=str(report.id),
        original_filename=report.original_filename,
        status=report.status.value,
        extracted_text=report.extracted_text,
        uploaded_at=report.uploaded_at,
        analyzed_at=report.analyzed_at,
        error_message=report.error_message,
        has_analysis=report.analysis_result is not None,
    )
