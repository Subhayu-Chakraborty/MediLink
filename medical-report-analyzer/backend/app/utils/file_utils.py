"""
app/utils/file_utils.py
────────────────────────
File system utilities: validation, unique filename generation, async file save.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import UploadFile

ALLOWED_EXTENSIONS = {".pdf"}
ALLOWED_CONTENT_TYPES = {"application/pdf"}


def validate_file_extension(filename: str) -> bool:
    """Return True if the filename has an allowed extension (.pdf only)."""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def validate_content_type(content_type: str | None) -> bool:
    """Return True if the MIME type is an allowed content type."""
    if content_type is None:
        return False
    return content_type.lower() in ALLOWED_CONTENT_TYPES


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a collision-free storage filename.
    Format: <uuid4>_<sanitised_original_name>
    """
    ext = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4().hex
    # Sanitise the stem: replace spaces and special chars with underscores
    stem = Path(original_filename).stem
    safe_stem = "".join(c if c.isalnum() or c in "-_" else "_" for c in stem)[:50]
    return f"{unique_id}_{safe_stem}{ext}"


async def save_upload_file(upload_file: UploadFile, destination: Path) -> Path:
    """
    Asynchronously read an UploadFile in chunks and write to the destination path.

    Args:
        upload_file: FastAPI UploadFile object.
        destination: Full absolute path where the file will be written.

    Returns:
        The destination path.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    content = await upload_file.read()
    destination.write_bytes(content)
    # Rewind so the caller can re-read if needed
    await upload_file.seek(0)
    return destination
