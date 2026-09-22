"""
app/api/routes/reports.py
──────────────────────────
Medical report management endpoints: upload, list, detail.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.dependencies import require_patient_role
from app.models.user import User
from app.schemas.report import ReportDetailResponse, ReportListItem, ReportUploadResponse
from app.services import report_service

router = APIRouter()


@router.post(
    "/upload",
    response_model=ReportUploadResponse,
    status_code=201,
    summary="Upload a medical report PDF",
)
async def upload_report(
    file: UploadFile = File(..., description="PDF medical report file"),
    current_user: User = Depends(require_patient_role),
) -> ReportUploadResponse:
    """
    Upload a PDF medical report.
    Returns the report ID which can be used to trigger analysis.
    """
    report = await report_service.save_report(file, current_user)
    return ReportUploadResponse(
        id=str(report.id),
        original_filename=report.original_filename,
        status=report.status.value,
        uploaded_at=report.uploaded_at,
    )


@router.get(
    "/list",
    response_model=List[ReportListItem],
    summary="List all reports uploaded by the current patient",
)
async def list_reports(
    current_user: User = Depends(require_patient_role),
) -> List[ReportListItem]:
    """Return a list of all medical reports uploaded by the authenticated patient."""
    return await report_service.list_reports(str(current_user.id))


@router.get(
    "/{report_id}",
    response_model=ReportDetailResponse,
    summary="Get full details of a single report",
)
async def get_report(
    report_id: str,
    current_user: User = Depends(require_patient_role),
) -> ReportDetailResponse:
    """
    Return full details of a report including extracted text.
    Only the owning patient can access their own report.
    """
    return await report_service.get_report_by_id(report_id, str(current_user.id))
