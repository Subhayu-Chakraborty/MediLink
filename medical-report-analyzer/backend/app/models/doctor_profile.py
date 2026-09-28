"""
app/models/doctor_profile.py
──────────────────────────────
Beanie document model for the 'doctor_profiles' MongoDB collection.
Each doctor User has exactly one DoctorProfile.
The doctor_id is the unique public identifier used for patient searches.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from beanie import Document, Indexed, Link
from pydantic import Field

from app.models.user import User
from app.utils.time_utils import utc_now


class DoctorProfile(Document):
    """Beanie document model for the doctor_profiles collection."""

    user: Link[User]
    doctor_id: Indexed(str, unique=True)  # type: ignore[valid-type]  e.g. "DR-000123"
    specialization: str
    experience: int = 0               # years of experience
    hospital: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "doctor_profiles"
        use_state_management = True
