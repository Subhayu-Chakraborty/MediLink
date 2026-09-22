"""
app/ai/ocr/paddle_ocr.py
─────────────────────────
Future Phase 2: PaddleOCR-based text extraction pipeline.
Handles scanned medical reports (image-based PDFs with no text layer).

This module is called exclusively by text_extraction_service.py.
It will NOT be imported until Phase 2 is implemented.

# TODO: Implement in Phase 2 — requires: paddleocr==2.7.0, paddlepaddle==2.5.2
"""

from __future__ import annotations

from pathlib import Path


def extract_with_paddle(file_path: Path) -> str:
    """
    Run PaddleOCR on all pages of a PDF and return concatenated text.

    Steps (Phase 2):
      1. Convert PDF pages to images using pdf2image or PyMuPDF
      2. Run OpenCV preprocessing (see preprocessing.py)
      3. Pass preprocessed images through PaddleOCR
      4. Concatenate and clean text output

    # TODO: Implement in Phase 2
    """
    pass  # type: ignore[return-value]
