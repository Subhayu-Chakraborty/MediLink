"""
app/schemas/auth.py
────────────────────
Pydantic schemas for authentication request payloads and responses.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


class PatientRegisterExtra(BaseModel):
    """Optional extra fields when registering as a patient."""
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None


class DoctorRegisterExtra(BaseModel):
    """Required extra fields when registering as a doctor."""
    specialization: str
    experience: int = Field(default=0, ge=0)
    hospital: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None


class RegisterRequest(BaseModel):
    """Payload for POST /auth/register."""
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    role: UserRole

    # Doctor-specific (required when role == doctor)
    specialization: Optional[str] = None
    experience: Optional[int] = Field(default=None, ge=0, le=80)
    hospital: Optional[str] = None
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)

    # Patient-specific (optional)
    age: Optional[int] = Field(default=None, ge=0, le=130)
    gender: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("role")
    @classmethod
    def prevent_public_admin_registration(cls, value: UserRole) -> UserRole:
        if value == UserRole.ADMIN:
            raise ValueError("Admin accounts cannot be created through public registration.")
        return value

    @field_validator("specialization")
    @classmethod
    def normalize_specialization(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class LoginRequest(BaseModel):
    """Payload for POST /auth/login."""
    email: EmailStr
    password: str


class UserInfo(BaseModel):
    """Embedded user info returned in token responses."""
    id: str
    email: str
    full_name: str
    role: UserRole


class TokenResponse(BaseModel):
    """Response returned after successful login or registration."""
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class MeResponse(BaseModel):
    """Response for GET /auth/me."""
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
