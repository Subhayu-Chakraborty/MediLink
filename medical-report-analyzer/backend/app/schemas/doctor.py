"""
app/schemas/doctor.py
──────────────────────
Pydantic schemas for doctor profile views and search results.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


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


class DoctorSearchResult(BaseModel):
    """Single result from GET /doctors/search?doctor_id=DR-XXXXX."""
    user_id: str
    doctor_id: str
    full_name: str
    specialization: str
    experience: int
    hospital: Optional[str] = None


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
