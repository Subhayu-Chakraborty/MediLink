"""Helpers for querying Beanie links consistently across MongoDB drivers."""

from __future__ import annotations

from bson import DBRef, ObjectId
from fastapi import HTTPException, status


def object_id(value: str, detail: str = "Invalid identifier.") -> ObjectId:
    """Parse a public string ID and return a client-safe 404 on invalid input."""
    if not ObjectId.is_valid(value):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return ObjectId(value)


def user_reference(user_id: str | ObjectId) -> DBRef:
    """Create the exact DBRef stored by Beanie for a User link."""
    identifier = user_id if isinstance(user_id, ObjectId) else object_id(user_id)
    return DBRef("users", identifier)
