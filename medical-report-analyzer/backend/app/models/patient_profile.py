"""
app/models/patient_profile.py
───────────────────────────────
Beanie document model for the 'patient_profiles' MongoDB collection.
Each patient User has exactly one PatientProfile.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from beanie import Document, Link
from pydantic import Field

from app.models.user import User
from app.utils.time_utils import utc_now


class PatientProfile(Document):
    """Beanie document model for the patient_profiles collection."""

    user: Link[User]
    age: Optional[int] = None
    gender: Optional[str] = None           # "male" | "female" | "other"
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "patient_profiles"
        use_state_management = True
