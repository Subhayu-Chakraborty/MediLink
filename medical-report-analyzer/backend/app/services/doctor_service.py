"""
app/services/doctor_service.py
───────────────────────────────
Business logic for doctor-specific operations.

Architecture: Routes → DoctorService → Beanie models
"""

from __future__ import annotations

import logging
import math
from typing import List

from fastapi import HTTPException, status

from app.models.doctor_profile import DoctorProfile
from app.models.doctor_patient_request import DoctorPatientRequest, RequestStatus
from app.models.patient_profile import PatientProfile
from app.models.medical_report import MedicalReport
from app.models.user import User
from app.schemas.doctor import (
    DoctorProfileResponse,
    DoctorSearchResult,
    DoctorProfileUpdateRequest,
    NearbyDoctorResult,
    PatientRequestItem,
    PatientSummary,
)
from app.utils.link_utils import user_reference
from app.utils.time_utils import utc_now

logger = logging.getLogger(__name__)


async def search_doctor_by_id(doctor_id: str) -> DoctorSearchResult:
    """
    Find a doctor by their unique public doctor_id.

    Raises:
        HTTPException 404: if no doctor with that ID exists.
    """
    profile = await DoctorProfile.find_one(
        DoctorProfile.doctor_id == doctor_id.strip().upper(),
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No doctor found with ID '{doctor_id}'.",
        )
    await profile.fetch_link(DoctorProfile.user)
    user: User = profile.user  # type: ignore[assignment]
    return DoctorSearchResult(
        user_id=str(user.id),
        doctor_id=profile.doctor_id,
        full_name=user.full_name,
        specialization=profile.specialization,
        experience=profile.experience,
        hospital=profile.hospital,
        latitude=profile.latitude,
        longitude=profile.longitude,
    )


async def get_doctor_profile(user_id: str) -> DoctorProfileResponse:
    """Return the DoctorProfile for a given user_id."""
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    profile = await DoctorProfile.find_one(
        {"user": user_reference(user_id)},
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
        latitude=profile.latitude,
        longitude=profile.longitude,
    )


async def update_doctor_profile(
    user_id: str,
    updates: DoctorProfileUpdateRequest,
) -> DoctorProfileResponse:
    """Apply partial updates to a doctor's profile, including practice location."""
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    profile = await DoctorProfile.find_one(
        {"user": user_reference(user_id)},
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Doctor profile not found.")

    update_data = updates.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    await profile.save()

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
        latitude=profile.latitude,
        longitude=profile.longitude,
    )


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the Haversine distance between two points in kilometers."""
    earth_radius_km = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    start_lat = math.radians(lat1)
    end_lat = math.radians(lat2)
    haversine = (
        math.sin(d_lat / 2) ** 2
        + math.cos(start_lat) * math.cos(end_lat) * math.sin(d_lon / 2) ** 2
    )
    return 2 * earth_radius_km * math.asin(math.sqrt(haversine))


async def get_nearby_doctors(
    latitude: float,
    longitude: float,
    radius_km: float,
) -> List[NearbyDoctorResult]:
    """Return doctors with saved coordinates inside the requested radius."""
    profiles = await DoctorProfile.find_all().to_list()

    nearby: List[NearbyDoctorResult] = []
    for profile in profiles:
        if profile.latitude is None or profile.longitude is None:
            continue

        distance = _distance_km(latitude, longitude, profile.latitude, profile.longitude)
        if distance > radius_km:
            continue

        await profile.fetch_link(DoctorProfile.user)
        user: User = profile.user  # type: ignore[assignment]
        nearby.append(NearbyDoctorResult(
            user_id=str(user.id),
            doctor_id=profile.doctor_id,
            full_name=user.full_name,
            specialization=profile.specialization,
            experience=profile.experience,
            hospital=profile.hospital,
            latitude=profile.latitude,
            longitude=profile.longitude,
            distance_km=round(distance, 1),
        ))

    nearby.sort(key=lambda doctor: doctor.distance_km)
    return nearby


async def get_pending_requests(doctor_user_id: str) -> List[PatientRequestItem]:
    """Return all PENDING connection requests for the logged-in doctor."""
    requests = await DoctorPatientRequest.find(
        {"doctor": user_reference(doctor_user_id)},
        DoctorPatientRequest.status == RequestStatus.PENDING,
    ).to_list()

    result = []
    for req in requests:
        await req.fetch_link(DoctorPatientRequest.patient)
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
    req = await DoctorPatientRequest.get(request_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Request not found.")

    await req.fetch_link(DoctorPatientRequest.doctor)
    doctor: User = req.doctor  # type: ignore[assignment]
    if str(doctor.id) != doctor_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to respond to this request.")

    if req.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Request has already been {req.status.value}.",
        )

    req.status = RequestStatus.ACCEPTED if accept else RequestStatus.REJECTED
    req.responded_at = utc_now()
    await req.save()

    action = "accepted" if accept else "rejected"
    logger.info("Doctor %s %s request %s", doctor_user_id, action, request_id)
    return {"message": f"Request has been {action}.", "status": req.status.value}


async def get_accepted_patients(doctor_user_id: str) -> List[PatientSummary]:
    """Return list of patients connected to this doctor (accepted requests)."""
    requests = await DoctorPatientRequest.find(
        {"doctor": user_reference(doctor_user_id)},
        DoctorPatientRequest.status == RequestStatus.ACCEPTED,
    ).to_list()

    result = []
    for req in requests:
        await req.fetch_link(DoctorPatientRequest.patient)
        patient: User = req.patient  # type: ignore[assignment]
        patient_profile = await PatientProfile.find_one(
            {"user": user_reference(patient.id)},
        )
        report_count = await MedicalReport.find(
            {"patient": user_reference(patient.id)},
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
        {"doctor": user_reference(doctor_user_id)},
        {"patient": user_reference(patient_user_id)},
        DoctorPatientRequest.status == RequestStatus.ACCEPTED,
    )
    return req is not None
