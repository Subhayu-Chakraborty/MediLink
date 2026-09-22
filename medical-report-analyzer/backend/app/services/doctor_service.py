"""
app/services/doctor_service.py
───────────────────────────────
Business logic for doctor-specific operations.

Architecture: Routes → DoctorService → Beanie models
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import HTTPException, status

from app.models.doctor_profile import DoctorProfile
from app.models.doctor_patient_request import DoctorPatientRequest, RequestStatus
from app.models.patient_profile import PatientProfile
from app.models.medical_report import MedicalReport
from app.models.user import User
from app.schemas.doctor import (
    DoctorProfileResponse,
    DoctorSearchResult,
    PatientRequestItem,
    PatientSummary,
)

logger = logging.getLogger(__name__)


async def search_doctor_by_id(doctor_id: str) -> DoctorSearchResult:
    """
    Find a doctor by their unique public doctor_id.

    Raises:
        HTTPException 404: if no doctor with that ID exists.
    """
    profile = await DoctorProfile.find_one(
        DoctorProfile.doctor_id == doctor_id.strip().upper(),
        fetch_links=True,
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No doctor found with ID '{doctor_id}'.",
        )
    user: User = profile.user  # type: ignore[assignment]
    return DoctorSearchResult(
        user_id=str(user.id),
        doctor_id=profile.doctor_id,
        full_name=user.full_name,
        specialization=profile.specialization,
        experience=profile.experience,
        hospital=profile.hospital,
    )


async def get_doctor_profile(user_id: str) -> DoctorProfileResponse:
    """Return the DoctorProfile for a given user_id."""
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    profile = await DoctorProfile.find_one(
        DoctorProfile.user.id == ObjectId(user_id),  # type: ignore[attr-defined]
        fetch_links=True,
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Doctor profile not found.")

    return DoctorProfileResponse(
        id=str(profile.id),
        user_id=str(user.id),
        doctor_id=profile.doctor_id,
        full_name=user.full_name,
        email=user.email,
        specialization=profile.specialization,
        experience=profile.experience,
        hospital=profile.hospital,
        phone=profile.phone,
        bio=profile.bio,
    )


async def get_pending_requests(doctor_user_id: str) -> List[PatientRequestItem]:
    """Return all PENDING connection requests for the logged-in doctor."""
    requests = await DoctorPatientRequest.find(
        DoctorPatientRequest.doctor.id == ObjectId(doctor_user_id),  # type: ignore[attr-defined]
        DoctorPatientRequest.status == RequestStatus.PENDING,
        fetch_links=True,
    ).to_list()

    result = []
    for req in requests:
        patient: User = req.patient  # type: ignore[assignment]
        result.append(PatientRequestItem(
            request_id=str(req.id),
            patient_id=str(patient.id),
            patient_name=patient.full_name,
            patient_email=patient.email,
            status=req.status.value,
            requested_at=req.requested_at.isoformat(),
        ))
    return result


async def respond_to_request(
    request_id: str,
    doctor_user_id: str,
    accept: bool,
) -> dict:
    """
    Accept or reject a patient connection request.

    Raises:
        HTTPException 404: if the request doesn't exist.
        HTTPException 403: if the doctor doesn't own this request.
        HTTPException 409: if the request is already responded to.
    """
    req = await DoctorPatientRequest.get(request_id, fetch_links=True)
    if req is None:
        raise HTTPException(status_code=404, detail="Request not found.")

    doctor: User = req.doctor  # type: ignore[assignment]
    if str(doctor.id) != doctor_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to respond to this request.")

    if req.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Request has already been {req.status.value}.",
        )

    req.status = RequestStatus.ACCEPTED if accept else RequestStatus.REJECTED
    req.responded_at = datetime.utcnow()
    await req.save()

    action = "accepted" if accept else "rejected"
    logger.info("Doctor %s %s request %s", doctor_user_id, action, request_id)
    return {"message": f"Request has been {action}.", "status": req.status.value}


async def get_accepted_patients(doctor_user_id: str) -> List[PatientSummary]:
    """Return list of patients connected to this doctor (accepted requests)."""
    requests = await DoctorPatientRequest.find(
        DoctorPatientRequest.doctor.id == ObjectId(doctor_user_id),  # type: ignore[attr-defined]
        DoctorPatientRequest.status == RequestStatus.ACCEPTED,
        fetch_links=True,
    ).to_list()

    result = []
    for req in requests:
        patient: User = req.patient  # type: ignore[assignment]
        patient_profile = await PatientProfile.find_one(
            PatientProfile.user.id == patient.id,  # type: ignore[attr-defined]
        )
        report_count = await MedicalReport.find(
            MedicalReport.patient.id == patient.id,  # type: ignore[attr-defined]
        ).count()
        result.append(PatientSummary(
            user_id=str(patient.id),
            full_name=patient.full_name,
            email=patient.email,
            age=patient_profile.age if patient_profile else None,
            gender=patient_profile.gender if patient_profile else None,
            report_count=report_count,
        ))
    return result


async def verify_patient_connection(doctor_user_id: str, patient_user_id: str) -> bool:
    """
    Verify that the doctor has an accepted connection with the patient.
    Used to gate access to patient reports.
    """
    req = await DoctorPatientRequest.find_one(
        DoctorPatientRequest.doctor.id == ObjectId(doctor_user_id),  # type: ignore[attr-defined]
        DoctorPatientRequest.patient.id == ObjectId(patient_user_id),  # type: ignore[attr-defined]
        DoctorPatientRequest.status == RequestStatus.ACCEPTED,
    )
    return req is not None
