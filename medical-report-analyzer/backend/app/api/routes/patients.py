"""
app/api/routes/patients.py
───────────────────────────
Patient-specific endpoints: profile, doctor connection requests.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from app.api.dependencies import require_patient_role
from app.models.user import User
from app.schemas.patient import (
    DoctorRequestStatusItem,
    PatientProfileResponse,
    PatientProfileUpdateRequest,
    SendDoctorRequestPayload,
)
from app.services import patient_service

router = APIRouter()


@router.get(
    "/profile",
    response_model=PatientProfileResponse,
    summary="Get the logged-in patient's profile",
)
async def get_profile(
    current_user: User = Depends(require_patient_role),
) -> PatientProfileResponse:
    """Return the profile of the authenticated patient."""
    return await patient_service.get_patient_profile(str(current_user.id))


@router.patch(
    "/profile",
    response_model=PatientProfileResponse,
    summary="Update the logged-in patient's profile",
)
async def update_profile(
    payload: PatientProfileUpdateRequest,
    current_user: User = Depends(require_patient_role),
) -> PatientProfileResponse:
    """Partially update the authenticated patient's profile."""
    return await patient_service.update_patient_profile(str(current_user.id), payload)


@router.post(
    "/doctor-requests",
    status_code=201,
    summary="Send a connection request to a doctor",
)
async def send_doctor_request(
    payload: SendDoctorRequestPayload,
    current_user: User = Depends(require_patient_role),
) -> dict:
    """
    Send a connection request to a doctor identified by their doctor_id.
    A patient can only send one request per doctor.
    """
    return await patient_service.send_doctor_request(
        patient_user_id=str(current_user.id),
        doctor_id_str=payload.doctor_id,
    )


@router.get(
    "/doctor-requests",
    response_model=List[DoctorRequestStatusItem],
    summary="List all doctor connection requests sent by the patient",
)
async def get_doctor_requests(
    current_user: User = Depends(require_patient_role),
) -> List[DoctorRequestStatusItem]:
    """List all doctor connection requests the patient has sent, with their current status."""
    return await patient_service.list_patient_requests(str(current_user.id))
