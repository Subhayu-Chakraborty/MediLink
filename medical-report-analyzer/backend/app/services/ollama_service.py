"""
app/services/ollama_service.py
───────────────────────────────
Ollama API integration — the ONLY place that calls the local Ollama API.

Architecture: Routes/Services → analyse_report_text() → Ollama API
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.ai.ollama.prompts import build_analysis_prompt, SYSTEM_CONTEXT

logger = logging.getLogger(__name__)


async def analyse_report_text(extracted_text: str) -> Dict[str, Any]:
    """
    Send extracted medical report text to the local Ollama API and return
    a structured analysis result as a Python dictionary.

    Args:
        extracted_text: Plain text extracted from the PDF report.

    Returns:
        Parsed dictionary matching the AnalysisResult schema.

    Raises:
        HTTPException 503: if the Ollama API call fails.
        HTTPException 422: if Ollama returns invalid/unparseable JSON.
    """
    if not extracted_text or len(extracted_text.strip()) < 50:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Extracted text is too short to analyse. Please upload a valid medical report.",
        )

    prompt = build_analysis_prompt(extracted_text)
    
    # We combine system and prompt for models that don't support system roles, 
    # but the Ollama API supports system roles via /api/generate
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "system": SYSTEM_CONTEXT,
        "stream": False,
        "format": "json",
        # Force Ollama to use CPU to bypass the CUDA "shared object initialization failed" error
        "options": {
            "num_gpu": 0
        }
    }
    
    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"

    try:
        logger.info("Sending report text (%d chars) to Ollama (%s)…", len(extracted_text), settings.OLLAMA_MODEL)
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            raw_text = response.json().get("response", "")
            
        logger.info("Ollama response received (%d chars).", len(raw_text))
    except httpx.RequestError as exc:
        logger.error("Ollama API call failed (Network Error): %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI analysis service (Ollama) is temporarily unavailable. Make sure Ollama is running! (Error: {exc})",
        )
    except httpx.HTTPStatusError as exc:
        logger.error("Ollama API call failed (HTTP %s): %s", exc.response.status_code, exc.response.text)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI analysis service returned an error. (HTTP {exc.response.status_code})",
        )
    except Exception as exc:
        logger.error("Ollama API call failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI analysis service failed. (Error: {exc})",
        )

    return _parse_ollama_response(raw_text)


def _parse_ollama_response(raw_response: str) -> Dict[str, Any]:
    """
    Extract and validate the JSON payload from Ollama's text response.
    Handles markdown code fences if present, though `format: json` usually omits them.

    Raises:
        HTTPException 422: if JSON cannot be parsed or is structurally invalid.
    """
    # Strip markdown code fences if present
    cleaned = raw_response.strip()
    fence_pattern = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)
    match = fence_pattern.search(cleaned)
    if match:
        cleaned = match.group(1).strip()

    # Try to parse the JSON
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        # Try to find first { ... } block
        brace_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if brace_match:
            try:
                data = json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                logger.error("Failed to parse Ollama JSON: %s", raw_response[:500])
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="AI returned an invalid response format. Please try again.",
                )
        else:
            logger.error("No JSON found in Ollama response: %s", raw_response[:500])
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="AI returned an invalid response format. Please try again.",
            )

    # Validate required top-level keys
    required_keys = {"summary", "parameters", "disease_risks"}
    missing = required_keys - set(data.keys())
    if missing:
        logger.warning("Ollama JSON missing keys: %s", missing)
        # Fill defaults rather than raising — graceful degradation
        if "summary" not in data:
            data["summary"] = "Analysis completed. Please consult a medical professional for interpretation."
        if "parameters" not in data:
            data["parameters"] = []
        if "disease_risks" not in data:
            data["disease_risks"] = {
                "diabetes":       {"level": "Insufficient Data", "reason": "No relevant markers found."},
                "ckd":            {"level": "Insufficient Data", "reason": "No relevant markers found."},
                "anemia":         {"level": "Insufficient Data", "reason": "No relevant markers found."},
                "cardiovascular": {"level": "Insufficient Data", "reason": "No relevant markers found."},
            }

    return data
