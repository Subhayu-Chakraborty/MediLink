"""
app/schemas/chat.py
───────────────────
Pydantic schemas for patient-doctor chat messages.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessageCreate(BaseModel):
    """Payload for sending a chat message over REST-like websocket JSON."""

    receiver_id: str
    content: str = Field(..., min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    """Chat message returned to the frontend."""

    id: str
    sender_id: str
    receiver_id: str
    content: str
    is_read: bool
    created_at: datetime
