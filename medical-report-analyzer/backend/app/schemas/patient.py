"""
app/schemas/patient.py
───────────────────────
Pydantic schemas for patient profile management and doctor request status.
"""

from __future__ import annotations

from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class PatientProfileResponse(BaseModel):
    """Patient profile as returned by the API."""
    user_id: str
    full_name: str
    email: str
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None


class PatientProfileUpdateRequest(BaseModel):
    """Fields the patient may update on their own profile."""
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None


class SendDoctorRequestPayload(BaseModel):
    """Payload for POST /patients/doctor-requests."""
    doctor_id: str                 # The doctor's public doctor_id (e.g. "DR-000123")


class DoctorRequestStatusItem(BaseModel):
    """Status of a single doctor connection request sent by the patient."""
    request_id: str
    doctor_id: str
    doctor_name: str
    doctor_specialization: str
    status: str                   # "pending" | "accepted" | "rejected"
    requested_at: str
    responded_at: Optional[str] = None
