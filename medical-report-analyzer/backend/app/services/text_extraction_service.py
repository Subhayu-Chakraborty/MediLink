"""
app/services/text_extraction_service.py
────────────────────────────────────────
PDF text extraction with a pluggable extractor interface.

Phase 1: PyMuPDF (primary) → pdfplumber (fallback).
Phase 2: PaddleOCR will be added as a third strategy here without changing
         any route or analysis code.

Public API: extract_text(file_path) -> str
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Minimum character count to consider extraction "successful"
MIN_TEXT_LENGTH = 50


async def extract_text(file_path: str | Path) -> str:
    """
    Extract all text from a PDF file.

    Strategy:
      1. Try PyMuPDF (fast, accurate for text-layer PDFs).
      2. If result is empty or below threshold, fallback to pdfplumber.
      3. If both fail, raise ValueError with a descriptive message.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted plain text string.

    Raises:
        ValueError: if extraction fails from both extractors.
        FileNotFoundError: if the PDF file does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    # Try PyMuPDF first
    try:
        text = _extract_with_pymupdf(path)
        if text and len(text.strip()) >= MIN_TEXT_LENGTH:
            logger.info("PyMuPDF extraction succeeded: %d chars", len(text))
            return text.strip()
        logger.warning("PyMuPDF returned insufficient text (%d chars), trying pdfplumber.", len(text))
    except Exception as exc:
        logger.warning("PyMuPDF extraction failed: %s — trying pdfplumber.", exc)

    # Fallback to pdfplumber
    try:
        text = _extract_with_pdfplumber(path)
        if text and len(text.strip()) >= MIN_TEXT_LENGTH:
            logger.info("pdfplumber extraction succeeded: %d chars", len(text))
            return text.strip()
        logger.warning("pdfplumber also returned insufficient text (%d chars).", len(text))
    except Exception as exc:
        logger.warning("pdfplumber extraction failed: %s", exc)

    # Both failed
    raise ValueError(
        "Could not extract meaningful text from the PDF. "
        "The file may be scanned/image-based. OCR support will be added in Phase 2."
    )


def _extract_with_pymupdf(file_path: Path) -> str:
    """
    Extract text from PDF using PyMuPDF (fitz).
    Fast and accurate for text-layer PDFs.
    """
    import fitz  # PyMuPDF

    text_parts = []
    with fitz.open(str(file_path)) as doc:
        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text("text")
            if page_text.strip():
                text_parts.append(f"--- Page {page_num} ---\n{page_text}")

    return "\n\n".join(text_parts)


def _extract_with_pdfplumber(file_path: Path) -> str:
    """
    Fallback text extraction using pdfplumber.
    Better at handling tables and complex column layouts.
    """
    import pdfplumber

    text_parts = []
    with pdfplumber.open(str(file_path)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(f"--- Page {page_num} ---\n{page_text}")

    return "\n\n".join(text_parts)
