"""
app/services/chat_service.py
────────────────────────────
Business logic for persisted patient-doctor chat.
"""

from __future__ import annotations

from typing import List

from fastapi import HTTPException, status

from app.models.chat_message import ChatMessage
from app.models.doctor_patient_request import DoctorPatientRequest, RequestStatus
from app.models.user import User, UserRole
from app.schemas.chat import ChatMessageResponse
from app.utils.link_utils import user_reference


def _role_value(user: User) -> str:
    return getattr(user.role, "value", user.role)


async def verify_chat_allowed(current_user: User, other_user_id: str) -> User:
    """
    Ensure the users are an accepted patient-doctor pair and return the other user.
    """
    if str(current_user.id) == other_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot start a chat with yourself.",
        )

    other_user = await User.get(other_user_id)
    if other_user is None or not other_user.is_active:
        raise HTTPException(status_code=404, detail="User not found.")

    current_role = _role_value(current_user)
    other_role = _role_value(other_user)
    valid_roles = {UserRole.PATIENT.value, UserRole.DOCTOR.value}
    if {current_role, other_role} != valid_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chat is only available between connected patients and doctors.",
        )

    if current_role == UserRole.PATIENT.value:
        patient_id = str(current_user.id)
        doctor_id = str(other_user.id)
    else:
        patient_id = str(other_user.id)
        doctor_id = str(current_user.id)

    connection = await DoctorPatientRequest.find_one(
        {"patient": user_reference(patient_id)},
        {"doctor": user_reference(doctor_id)},
        DoctorPatientRequest.status == RequestStatus.ACCEPTED,
    )
    if connection is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chat requires an accepted doctor-patient connection.",
        )

    return other_user


def to_chat_response(message: ChatMessage) -> ChatMessageResponse:
    """Convert a ChatMessage document into an API response."""
    sender: User = message.sender  # type: ignore[assignment]
    receiver: User = message.receiver  # type: ignore[assignment]
    return ChatMessageResponse(
        id=str(message.id),
        sender_id=str(sender.id),
        receiver_id=str(receiver.id),
        content=message.content,
        is_read=message.is_read,
        created_at=message.created_at,
    )


async def create_message(
    sender: User,
    receiver_id: str,
    content: str,
) -> ChatMessageResponse:
    """Validate, persist, and return a chat message."""
    clean_content = content.strip()
    if not clean_content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message content cannot be empty.",
        )

    receiver = await verify_chat_allowed(sender, receiver_id)
    message = ChatMessage(
        sender=sender,
        receiver=receiver,
        content=clean_content,
    )
    await message.insert()
    return to_chat_response(message)


async def list_conversation(
    current_user: User,
    other_user_id: str,
) -> List[ChatMessageResponse]:
    """Return all messages exchanged by the current user and another connected user."""
    other_user = await verify_chat_allowed(current_user, other_user_id)
    sent = await ChatMessage.find(
        {"sender": user_reference(current_user.id)},
        {"receiver": user_reference(other_user.id)},
    ).to_list()
    received = await ChatMessage.find(
        {"sender": user_reference(other_user.id)},
        {"receiver": user_reference(current_user.id)},
    ).to_list()

    for message in [*sent, *received]:
        await message.fetch_link(ChatMessage.sender)
        await message.fetch_link(ChatMessage.receiver)

    unread_received = [message for message in received if not message.is_read]
    for message in unread_received:
        message.is_read = True
        await message.save()

    messages = [*sent, *received]
    messages.sort(key=lambda message: message.created_at)
    return [to_chat_response(message) for message in messages]
