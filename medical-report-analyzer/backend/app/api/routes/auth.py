"""
app/api/routes/auth.py
───────────────────────
Authentication endpoints: register, login, logout, me.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, MeResponse, RegisterRequest, TokenResponse
from app.services import auth_service

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=201,
    summary="Register a new user account (patient or doctor)",
)
async def register(payload: RegisterRequest) -> TokenResponse:
    """
    Create a new patient or doctor account.
    Returns a JWT access token immediately (no separate login step needed).
    """
    return await auth_service.register_user(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive an access token",
)
async def login(payload: LoginRequest) -> TokenResponse:
    """
    Authenticate with email and password.
    Returns a JWT Bearer access token valid for the configured duration.
    """
    return await auth_service.login_user(payload)


@router.post(
    "/logout",
    summary="Logout (client-side token removal)",
)
async def logout() -> dict:
    """
    JWT is stateless. Actual session invalidation is done client-side
    by discarding the stored token. This endpoint confirms the action.
    """
    return {"message": "Logged out successfully."}


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Get the currently authenticated user",
)
async def me(current_user: User = Depends(get_current_user)) -> MeResponse:
    """Return the profile of the currently authenticated user."""
    return MeResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
    )
