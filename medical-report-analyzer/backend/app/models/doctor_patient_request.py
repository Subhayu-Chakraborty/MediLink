"""
app/models/doctor_patient_request.py
──────────────────────────────────────
Beanie document model for the 'doctor_patient_requests' MongoDB collection.
Tracks connection requests sent by patients to doctors.
Status lifecycle: pending → accepted | rejected
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from beanie import Document, Link
from pydantic import Field

from app.models.user import User
from app.utils.time_utils import utc_now


class RequestStatus(str, Enum):
    PENDING  = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class DoctorPatientRequest(Document):
    """Beanie document model for doctor_patient_requests collection."""

    patient: Link[User]
    doctor: Link[User]
    status: RequestStatus = RequestStatus.PENDING
    requested_at: datetime = Field(default_factory=utc_now)
    responded_at: Optional[datetime] = None

    class Settings:
        name = "doctor_patient_requests"
        use_state_management = True
