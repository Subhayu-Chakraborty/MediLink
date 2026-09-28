"""
app/api/routes/analysis.py
───────────────────────────
Analysis trigger and result retrieval endpoints.
This route orchestrates: text extraction → Ollama analysis → result storage.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, require_patient_role
from app.models.medical_report import MedicalReport, ReportStatus
from app.models.user import User
from app.schemas.analysis import AnalysisResult, AnalysisTriggerResponse, DiseaseRisks, DiseaseRiskItem, MedicalParameter
from app.services import ollama_service, report_service, text_extraction_service
from app.services.report_service import update_report_status
from app.utils.time_utils import utc_now

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/{report_id}",
    response_model=AnalysisTriggerResponse,
    summary="Trigger AI analysis for an uploaded report",
)
async def trigger_analysis(
    report_id: str,
    current_user: User = Depends(require_patient_role),
) -> AnalysisTriggerResponse:
    """
    Run the full analysis pipeline for a report:
      1. Verify report ownership
      2. Extract text from PDF (PyMuPDF → pdfplumber fallback)
      3. Send extracted text to Ollama
      4. Store the structured result in the MedicalReport document

    Returns immediately with status=analyzing; the patient then
    polls GET /analysis/{report_id} to retrieve the completed result.

    Note: For MVP, this is synchronous. Phase 2 will use background tasks.
    """
    report = await MedicalReport.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")

    await report.fetch_link(MedicalReport.patient)
    patient: User = report.patient  # type: ignore[assignment]
    if str(patient.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied.")

    # Don't re-analyze if already done
    if report.analysis_result is not None:
        return AnalysisTriggerResponse(
            report_id=report_id,
            status="analyzed",
            message="This report has already been analysed.",
        )

    # ── Step 1: Extract text ──────────────────────────────────────────────
    await update_report_status(report, ReportStatus.EXTRACTING)
    try:
        extracted_text = await text_extraction_service.extract_text(report.file_path)
        await update_report_status(report, ReportStatus.EXTRACTED, extracted_text=extracted_text)
    except (ValueError, FileNotFoundError) as exc:
        await update_report_status(
            report, ReportStatus.FAILED, error_message=str(exc)
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    # ── Step 2: Ollama analysis ───────────────────────────────────────────
    await update_report_status(report, ReportStatus.ANALYZING)
    try:
        analysis_result = await ollama_service.analyse_report_text(extracted_text)
        await update_report_status(
            report,
            ReportStatus.ANALYZED,
            analysis_result=analysis_result,
        )
    except HTTPException:
        await update_report_status(
            report,
            ReportStatus.FAILED,
            error_message="Ollama analysis failed.",
        )
        raise

    logger.info("Analysis complete for report %s", report_id)
    return AnalysisTriggerResponse(
        report_id=report_id,
        status="analyzed",
        message="Analysis completed successfully.",
    )


@router.get(
    "/{report_id}",
    response_model=AnalysisResult,
    summary="Retrieve analysis results for a report",
)
async def get_analysis_results(
    report_id: str,
    current_user: User = Depends(get_current_user),
) -> AnalysisResult:
    """
    Return the stored analysis result for an analysed report.
    Accessible by the owning patient OR any connected doctor.
    """
    report = await MedicalReport.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")

    await report.fetch_link(MedicalReport.patient)
    patient: User = report.patient  # type: ignore[assignment]

    # Authorization: patient owns it OR doctor is connected
    from app.models.user import UserRole
    if str(patient.id) != str(current_user.id):
        if current_user.role == UserRole.DOCTOR:
            from app.services.doctor_service import verify_patient_connection
            connected = await verify_patient_connection(
                str(current_user.id), str(patient.id)
            )
            if not connected:
                raise HTTPException(status_code=403, detail="Access denied.")
        else:
            raise HTTPException(status_code=403, detail="Access denied.")

    if report.analysis_result is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This report has not been analysed yet.",
        )

    raw = report.analysis_result

    # Build the typed AnalysisResult from the stored dict
    disease_risks_raw = raw.get("disease_risks", {})
    disease_risks = DiseaseRisks(
        diabetes=DiseaseRiskItem(
            level=disease_risks_raw.get("diabetes", {}).get("level", "Insufficient Data"),
            reason=disease_risks_raw.get("diabetes", {}).get("reason", ""),
        ),
        ckd=DiseaseRiskItem(
            level=disease_risks_raw.get("ckd", {}).get("level", "Insufficient Data"),
            reason=disease_risks_raw.get("ckd", {}).get("reason", ""),
        ),
        anemia=DiseaseRiskItem(
            level=disease_risks_raw.get("anemia", {}).get("level", "Insufficient Data"),
            reason=disease_risks_raw.get("anemia", {}).get("reason", ""),
        ),
        cardiovascular=DiseaseRiskItem(
            level=disease_risks_raw.get("cardiovascular", {}).get("level", "Insufficient Data"),
            reason=disease_risks_raw.get("cardiovascular", {}).get("reason", ""),
        ),
    )

    parameters = [
        MedicalParameter(**p) for p in raw.get("parameters", [])
    ]

    return AnalysisResult(
        report_id=report_id,
        summary=raw.get("summary", ""),
        parameters=parameters,
        disease_risks=disease_risks,
        analyzed_at=report.analyzed_at or utc_now(),
    )
