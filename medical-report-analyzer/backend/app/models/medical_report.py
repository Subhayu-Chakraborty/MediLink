"""
app/models/medical_report.py
──────────────────────────────
Beanie document model for the 'medical_reports' MongoDB collection.
Stores uploaded PDF metadata, extracted text, and the full Ollama analysis result.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from beanie import Document, Link
from pydantic import Field

from app.models.user import User


class ReportStatus(str, Enum):
    UPLOADED   = "uploaded"
    EXTRACTING = "extracting"
    EXTRACTED  = "extracted"
    ANALYZING  = "analyzing"
    ANALYZED   = "analyzed"
    FAILED     = "failed"


class MedicalReport(Document):
    """Beanie document model for the medical_reports collection."""

    patient: Link[User]
    original_filename: str
    stored_filename: str                 # UUID-prefixed filename on disk
    file_path: str                       # Relative path within UPLOAD_DIR
    status: ReportStatus = ReportStatus.UPLOADED

    # Set after text extraction service runs
    extracted_text: Optional[str] = None

    # Set after Ollama service runs — stores the full structured JSON
    analysis_result: Optional[Dict[str, Any]] = None

    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    analyzed_at: Optional[datetime] = None
    error_message: Optional[str] = None   # stores failure reason

    class Settings:
        name = "medical_reports"
        use_state_management = True
