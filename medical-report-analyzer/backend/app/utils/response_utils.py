"""
app/utils/response_utils.py
────────────────────────────
Standard API response helpers for consistent response envelopes.
All routes use these helpers to maintain a uniform response shape.
"""

from __future__ import annotations

from typing import Any, Optional


def success_response(data: Any, message: str = "Success") -> dict:
    """
    Wrap a successful payload in a standard envelope.

    Returns:
        {"success": True, "message": "...", "data": ...}
    """
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(message: str, code: Optional[str] = None) -> dict:
    """
    Construct a standard error response envelope.

    Returns:
        {"success": False, "message": "...", "error_code": "..."}
    """
    result: dict = {
        "success": False,
        "message": message,
    }
    if code:
        result["error_code"] = code
    return result
