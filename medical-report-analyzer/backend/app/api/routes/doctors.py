"""
app/api/routes/doctors.py
──────────────────────────
Doctor-specific endpoints: search, requests, patient management.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import require_doctor_role, get_current_user
from app.models.user import User
from app.schemas.doctor import (
    DoctorProfileUpdateRequest,
    DoctorProfileResponse,
    DoctorSearchResult,
    NearbyDoctorResult,
    PatientRequestItem,
    PatientSummary,
    RespondToRequestPayload,
)
from app.schemas.report import ReportListItem, ReportDetailResponse
from app.services import doctor_service, report_service

router = APIRouter()


@router.get(
    "/search",
    response_model=DoctorSearchResult,
    summary="Search for a doctor by their unique Doctor ID",
)
async def search_doctor(
    doctor_id: str = Query(..., description="The doctor's public ID, e.g. DR-ABC123"),
    _current_user: User = Depends(get_current_user),
) -> DoctorSearchResult:
    """
    Find a doctor using their unique doctor_id.
    Any authenticated user (patient or doctor) can search.
    """
    return await doctor_service.search_doctor_by_id(doctor_id)


@router.get(
    "/profile",
    response_model=DoctorProfileResponse,
    summary="Get the logged-in doctor's profile",
)
async def get_my_profile(
    current_user: User = Depends(require_doctor_role),
) -> DoctorProfileResponse:
    """Return the full profile for the authenticated doctor."""
    return await doctor_service.get_doctor_profile(str(current_user.id))


@router.patch(
    "/profile",
    response_model=DoctorProfileResponse,
    summary="Update the logged-in doctor's profile",
)
async def update_my_profile(
    payload: DoctorProfileUpdateRequest,
    current_user: User = Depends(require_doctor_role),
) -> DoctorProfileResponse:
    """Partially update the authenticated doctor's profile and practice location."""
    return await doctor_service.update_doctor_profile(str(current_user.id), payload)


@router.get(
    "/nearby",
    response_model=List[NearbyDoctorResult],
    summary="Find doctors near a latitude/longitude point",
)
async def get_nearby_doctors(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, gt=0, le=100),
    _current_user: User = Depends(get_current_user),
) -> List[NearbyDoctorResult]:
    """Return doctors with saved practice coordinates sorted by distance."""
    return await doctor_service.get_nearby_doctors(lat, lng, radius_km)


@router.get(
    "/requests",
    response_model=List[PatientRequestItem],
    summary="List pending patient connection requests",
)
async def get_pending_requests(
    current_user: User = Depends(require_doctor_role),
) -> List[PatientRequestItem]:
    """Return all pending connection requests sent to the logged-in doctor."""
    return await doctor_service.get_pending_requests(str(current_user.id))


@router.patch(
    "/requests/{request_id}/respond",
    summary="Accept or reject a patient connection request",
)
async def respond_to_request(
    request_id: str,
    payload: RespondToRequestPayload,
    current_user: User = Depends(require_doctor_role),
) -> dict:
    """Accept (accept=true) or reject (accept=false) a patient's connection request."""
    return await doctor_service.respond_to_request(
        request_id=request_id,
        doctor_user_id=str(current_user.id),
        accept=payload.accept,
    )


@router.get(
    "/patients",
    response_model=List[PatientSummary],
    summary="List all connected patients",
)
async def get_my_patients(
    current_user: User = Depends(require_doctor_role),
) -> List[PatientSummary]:
    """Return the list of patients who have been accepted by this doctor."""
    return await doctor_service.get_accepted_patients(str(current_user.id))


@router.get(
    "/patients/{patient_id}/reports",
    response_model=List[ReportListItem],
    summary="List a connected patient's reports",
)
async def get_patient_reports(
    patient_id: str,
    current_user: User = Depends(require_doctor_role),
) -> List[ReportListItem]:
    """
    List all medical reports for a connected patient.
    Requires an accepted connection between this doctor and the patient.
    """
    connected = await doctor_service.verify_patient_connection(
        str(current_user.id), patient_id
    )
    if not connected:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail="You are not connected to this patient.",
        )
    return await report_service.list_reports(patient_id)


@router.get(
    "/patients/{patient_id}/reports/{report_id}",
    response_model=ReportDetailResponse,
    summary="View a connected patient's specific report",
)
async def get_patient_report(
    patient_id: str,
    report_id: str,
    current_user: User = Depends(require_doctor_role),
) -> ReportDetailResponse:
    """View the details and analysis of a specific report for a connected patient."""
    connected = await doctor_service.verify_patient_connection(
        str(current_user.id), patient_id
    )
    if not connected:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="You are not connected to this patient.")
    return await report_service.get_patient_report_for_doctor(report_id, patient_id)
