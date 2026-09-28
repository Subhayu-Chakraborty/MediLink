"""
app/api/routes/chat.py
──────────────────────
REST history and WebSocket delivery for patient-doctor chat.
"""

from __future__ import annotations

from typing import Dict, List, Set

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from jose import JWTError
from pydantic import ValidationError

from app.api.dependencies import get_current_user
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse
from app.services import chat_service

router = APIRouter()


class ConnectionManager:
    """Tracks active websocket connections by user id."""

    def __init__(self) -> None:
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.setdefault(user_id, set()).add(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        sockets = self.active_connections.get(user_id)
        if not sockets:
            return
        sockets.discard(websocket)
        if not sockets:
            self.active_connections.pop(user_id, None)

    async def send_to_user(self, user_id: str, payload: dict) -> None:
        for websocket in list(self.active_connections.get(user_id, set())):
            try:
                await websocket.send_json(payload)
            except Exception:  # A stale socket must not interrupt message delivery.
                self.disconnect(user_id, websocket)


manager = ConnectionManager()


async def _get_user_from_token(token: str) -> User | None:
    try:
        payload = decode_access_token(token)
    except JWTError:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = await User.get(user_id)
    if user is None or not user.is_active:
        return None
    return user


@router.get(
    "/messages/{other_user_id}",
    response_model=List[ChatMessageResponse],
    summary="List chat history with a connected patient or doctor",
)
async def list_messages(
    other_user_id: str,
    current_user: User = Depends(get_current_user),
) -> List[ChatMessageResponse]:
    return await chat_service.list_conversation(current_user, other_user_id)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
) -> None:
    current_user = await _get_user_from_token(token)
    if current_user is None:
        await websocket.close(code=1008, reason="Invalid authentication token.")
        return

    current_user_id = str(current_user.id)
    await manager.connect(current_user_id, websocket)
    try:
        while True:
            raw_payload = await websocket.receive_json()
            try:
                payload = ChatMessageCreate.model_validate(raw_payload)
                message = await chat_service.create_message(
                    sender=current_user,
                    receiver_id=payload.receiver_id,
                    content=payload.content,
                )
            except (ValidationError, ValueError) as exc:
                await websocket.send_json({"type": "error", "detail": str(exc)})
                continue
            except Exception as exc:  # noqa: BLE001
                await websocket.send_json({"type": "error", "detail": getattr(exc, "detail", str(exc))})
                continue

            message_payload = {
                "type": "message",
                "message": message.model_dump(mode="json"),
            }
            await manager.send_to_user(message.receiver_id, message_payload)
            await manager.send_to_user(message.sender_id, message_payload)
    except WebSocketDisconnect:
        manager.disconnect(current_user_id, websocket)
