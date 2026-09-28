"""
app/models/chat_message.py
──────────────────────────
Persisted chat messages exchanged between connected patients and doctors.
"""

from __future__ import annotations

from datetime import datetime

from beanie import Document, Link
from pydantic import Field

from app.models.user import User
from app.utils.time_utils import utc_now


class ChatMessage(Document):
    """Beanie document model for the chat_messages collection."""

    sender: Link[User]
    receiver: Link[User]
    content: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "chat_messages"
        use_state_management = True
