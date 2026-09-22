"""
app/schemas/report.py
──────────────────────
Pydantic schemas for report upload responses and list items.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReportUploadResponse(BaseModel):
    """Returned immediately after POST /reports/upload."""
    id: str
    original_filename: str
    status: str
    uploaded_at: datetime


class ReportListItem(BaseModel):
    """Single item in the report list."""
    id: str
    original_filename: str
    status: str
    uploaded_at: datetime
    analyzed_at: Optional[datetime] = None
    has_analysis: bool = False


class ReportDetailResponse(BaseModel):
    """Full report detail including extracted text."""
    id: str
    original_filename: str
    status: str
    extracted_text: Optional[str] = None
    uploaded_at: datetime
    analyzed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    has_analysis: bool = False
