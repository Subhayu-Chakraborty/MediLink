"""
app/services/patient_service.py
────────────────────────────────
Business logic for patient-specific operations.

Architecture: Routes → PatientService → Beanie models
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import HTTPException, status

from app.models.doctor_patient_request import DoctorPatientRequest, RequestStatus
from app.models.doctor_profile import DoctorProfile
from app.models.patient_profile import PatientProfile
from app.models.user import User
from app.schemas.patient import (
    DoctorRequestStatusItem,
    PatientProfileResponse,
    PatientProfileUpdateRequest,
)

logger = logging.getLogger(__name__)


async def get_patient_profile(user_id: str) -> PatientProfileResponse:
    """Retrieve the PatientProfile and User info for a given user_id."""
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    profile = await PatientProfile.find_one(
        PatientProfile.user.id == ObjectId(user_id),  # type: ignore[attr-defined]
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Patient profile not found.")

    return PatientProfileResponse(
        user_id=str(user.id),
        full_name=user.full_name,
        email=user.email,
        age=profile.age,
        gender=profile.gender,
        blood_group=profile.blood_group,
        phone=profile.phone,
        address=profile.address,
        emergency_contact=profile.emergency_contact,
    )


async def update_patient_profile(
    user_id: str,
    updates: PatientProfileUpdateRequest,
) -> PatientProfileResponse:
    """Apply partial updates to a patient's profile."""
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    profile = await PatientProfile.find_one(
        PatientProfile.user.id == ObjectId(user_id),  # type: ignore[attr-defined]
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Patient profile not found.")

    update_data = updates.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    profile.updated_at = datetime.utcnow()
    await profile.save()

    return PatientProfileResponse(
        user_id=str(user.id),
        full_name=user.full_name,
        email=user.email,
        age=profile.age,
        gender=profile.gender,
        blood_group=profile.blood_group,
        phone=profile.phone,
        address=profile.address,
        emergency_contact=profile.emergency_contact,
    )


async def send_doctor_request(patient_user_id: str, doctor_id_str: str) -> dict:
    """
    Create a new DoctorPatientRequest from patient to doctor.

    Raises:
        HTTPException 404: if doctor_id doesn't match any doctor.
        HTTPException 409: if a request already exists between this pair.
    """
    # Find the doctor by their public doctor_id
    doctor_profile = await DoctorProfile.find_one(
        DoctorProfile.doctor_id == doctor_id_str.strip().upper(),
        fetch_links=True,
    )
    if doctor_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No doctor found with ID '{doctor_id_str}'.",
        )

    doctor_user: User = doctor_profile.user  # type: ignore[assignment]
    doctor_user_id = str(doctor_user.id)
    patient_obj_id = ObjectId(patient_user_id)
    doctor_obj_id = ObjectId(doctor_user_id)

    # Check for existing request (any status)
    existing = await DoctorPatientRequest.find_one(
        DoctorPatientRequest.patient.id == patient_obj_id,  # type: ignore[attr-defined]
        DoctorPatientRequest.doctor.id == doctor_obj_id,    # type: ignore[attr-defined]
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A request to Dr. {doctor_user.full_name} already exists (status: {existing.status.value}).",
        )

    # Get Patient user object for the link
    patient_user = await User.get(patient_user_id)

    req = DoctorPatientRequest(
        patient=patient_user,  # type: ignore[arg-type]
        doctor=doctor_user,    # type: ignore[arg-type]
    )
    await req.insert()

    logger.info(
        "Patient %s sent connection request to doctor %s",
        patient_user_id,
        doctor_id_str,
    )

    return {
        "message": f"Connection request sent to Dr. {doctor_user.full_name}.",
        "request_id": str(req.id),
        "status": req.status.value,
    }


async def list_patient_requests(patient_user_id: str) -> List[DoctorRequestStatusItem]:
    """List all doctor connection requests sent by a patient."""
    requests = await DoctorPatientRequest.find(
        DoctorPatientRequest.patient.id == ObjectId(patient_user_id),  # type: ignore[attr-defined]
        fetch_links=True,
    ).to_list()

    result = []
    for req in requests:
        doctor_user: User = req.doctor  # type: ignore[assignment]
        doctor_profile = await DoctorProfile.find_one(
            DoctorProfile.user.id == doctor_user.id,  # type: ignore[attr-defined]
        )
        result.append(DoctorRequestStatusItem(
            request_id=str(req.id),
            doctor_id=doctor_profile.doctor_id if doctor_profile else "UNKNOWN",
            doctor_name=doctor_user.full_name,
            doctor_specialization=doctor_profile.specialization if doctor_profile else "Unknown",
            status=req.status.value,
            requested_at=req.requested_at.isoformat(),
            responded_at=req.responded_at.isoformat() if req.responded_at else None,
        ))
    return result
