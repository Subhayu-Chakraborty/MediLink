"""
app/api/dependencies.py
────────────────────────
FastAPI dependency injection: JWT validation, user fetch, role guards.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.security import decode_access_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Decode the JWT Bearer token and return the corresponding User document.

    Raises:
        HTTPException 401: if the token is invalid, expired, or the user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub", "")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await User.get(user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def require_patient_role(
    current_user: User = Depends(get_current_user),
) -> User:
    """Enforce that the authenticated user has the 'patient' role."""
    if current_user.role != UserRole.PATIENT and getattr(current_user.role, "value", current_user.role) != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to patients.",
        )
    return current_user


async def require_doctor_role(
    current_user: User = Depends(get_current_user),
) -> User:
    """Enforce that the authenticated user has the 'doctor' role."""
    if current_user.role != UserRole.DOCTOR and getattr(current_user.role, "value", current_user.role) != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to doctors.",
        )
    return current_user
