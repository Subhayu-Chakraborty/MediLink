"""
app/services/auth_service.py
─────────────────────────────
Authentication business logic: user registration, login, JWT creation.

Architecture: Routes → AuthService → Beanie models + security utilities
"""

from __future__ import annotations

import logging
import secrets
import string

from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User, UserRole
from app.models.doctor_profile import DoctorProfile
from app.models.patient_profile import PatientProfile
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserInfo

logger = logging.getLogger(__name__)


def _generate_doctor_id() -> str:
    """Generate a unique doctor ID in format DR-XXXXXX (6 uppercase alphanumeric chars)."""
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(secrets.choice(chars) for _ in range(6))
    return f"DR-{suffix}"


async def _ensure_unique_doctor_id() -> str:
    """Generate a doctor_id that does not already exist in the database."""
    for _ in range(10):  # max 10 attempts
        doctor_id = _generate_doctor_id()
        existing = await DoctorProfile.find_one(DoctorProfile.doctor_id == doctor_id)
        if existing is None:
            return doctor_id
    raise RuntimeError("Failed to generate a unique doctor ID after 10 attempts.")


async def register_user(payload: RegisterRequest) -> TokenResponse:
    """
    Create a new user account (patient or doctor).

    Steps:
      1. Check email uniqueness.
      2. Hash the password.
      3. Create User document.
      4. Create role-specific profile document.
      5. Return a JWT access token.
    """
    # 1. Check email uniqueness
    existing = await User.find_one(User.email == payload.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Validate doctor fields
    if payload.role == UserRole.DOCTOR and not payload.specialization:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Doctors must provide a specialization.",
        )

    # 2. Hash password
    hashed = hash_password(payload.password)

    # 3. Create User document
    user = User(
        email=payload.email,
        hashed_password=hashed,
        full_name=payload.full_name,
        role=payload.role,
    )
    await user.insert()

    # 4. Create profile
    if payload.role == UserRole.DOCTOR:
        doctor_id = await _ensure_unique_doctor_id()
        profile = DoctorProfile(
            user=user,
            doctor_id=doctor_id,
            specialization=payload.specialization or "General",
            experience=payload.experience or 0,
            hospital=payload.hospital,
        )
        await profile.insert()
        logger.info("Doctor registered: %s (doctor_id=%s)", user.email, doctor_id)
    else:
        profile = PatientProfile(
            user=user,
            age=payload.age,
            gender=payload.gender,
            phone=payload.phone,
        )
        await profile.insert()
        logger.info("Patient registered: %s", user.email)

    # 5. Issue JWT
    token = create_access_token(
        subject=str(user.id),
        extra_claims={"role": user.role.value, "email": user.email},
    )

    return TokenResponse(
        access_token=token,
        user=UserInfo(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
        ),
    )


async def login_user(payload: LoginRequest) -> TokenResponse:
    """
    Authenticate an existing user with email and password.

    Returns a JWT access token on success.
    Raises HTTP 401 on invalid credentials.
    """
    user = await User.find_one(User.email == payload.email)

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    token = create_access_token(
        subject=str(user.id),
        extra_claims={"role": user.role.value, "email": user.email},
    )

    logger.info("User logged in: %s", user.email)

    return TokenResponse(
        access_token=token,
        user=UserInfo(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
        ),
    )
