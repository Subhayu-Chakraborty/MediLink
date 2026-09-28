"""
app/schemas/doctor.py
──────────────────────
Pydantic schemas for doctor profile views and search results.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class DoctorProfileResponse(BaseModel):
    """Doctor profile returned by API endpoints."""
    id: str
    user_id: str
    doctor_id: str
    full_name: str
    email: str
    specialization: str
    experience: int
    hospital: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DoctorSearchResult(BaseModel):
    """Single result from GET /doctors/search?doctor_id=DR-XXXXX."""
    user_id: str
    doctor_id: str
    full_name: str
    specialization: str
    experience: int
    hospital: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class NearbyDoctorResult(DoctorSearchResult):
    """Doctor search result with calculated distance from the patient."""
    distance_km: float


class DoctorProfileUpdateRequest(BaseModel):
    """Fields a doctor may update on their own profile."""
    specialization: Optional[str] = None
    experience: Optional[int] = Field(default=None, ge=0, le=80)
    hospital: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)


class RespondToRequestPayload(BaseModel):
    """Payload for PATCH /doctors/requests/{id}/respond."""
    accept: bool


class PatientSummary(BaseModel):
    """Basic patient info shown in doctor's patient list."""
    user_id: str
    full_name: str
    email: str
    age: Optional[int] = None
    gender: Optional[str] = None
    report_count: int = 0


class PatientRequestItem(BaseModel):
    """Single request item in doctor's pending requests list."""
    request_id: str
    patient_id: str
    patient_name: str
    patient_email: str
    status: str
    requested_at: str
