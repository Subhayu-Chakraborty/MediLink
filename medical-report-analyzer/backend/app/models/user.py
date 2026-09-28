"""
app/models/user.py
───────────────────
Beanie document model for the 'users' MongoDB collection.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from beanie import Document, Indexed
from pydantic import EmailStr, Field
from app.utils.time_utils import utc_now


class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR  = "doctor"
    ADMIN   = "admin"


class User(Document):
    """Beanie document model for the users collection."""

    email: Indexed(EmailStr, unique=True)  # type: ignore[valid-type]
    hashed_password: str
    full_name: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "users"
        use_state_management = True
