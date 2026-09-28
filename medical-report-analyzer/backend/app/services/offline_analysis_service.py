"""Conservative report analysis used when no Ollama model is configured."""

from __future__ import annotations

import re
from typing import Any, Dict


_PARAMETER_PATTERN = re.compile(
    r"^(?P<name>[A-Za-z][A-Za-z0-9 ()/%+.-]{1,50}?)\s*[:=-]?\s+"
    r"(?P<value>-?\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z%/0-9^.-]{0,15})"
    r"(?:\s+(?P<range>\d+(?:\.\d+)?\s*[-–]\s*\d+(?:\.\d+)?))?"
    r"(?:\s+(?P<flag>high|low|normal|critical))?$",
    re.IGNORECASE,
)


def analyse_report_text_offline(extracted_text: str) -> Dict[str, Any]:
    """Extract obvious lab rows without making unsupported medical predictions."""
    parameters = []
    seen = set()

    for raw_line in extracted_text.splitlines():
        line = " ".join(raw_line.strip().split())
        if not line or line.startswith("--- Page"):
            continue

        match = _PARAMETER_PATTERN.match(line)
        if not match:
            continue

        name = match.group("name").strip(" :-")
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)

        raw_value = match.group("value")
        value: int | float
        value = float(raw_value) if "." in raw_value else int(raw_value)
        flag = (match.group("flag") or "Unknown").title()
        parameters.append(
            {
                "name": name,
                "value": value,
                "unit": match.group("unit") or "",
                "status": flag,
                "reference_range": match.group("range"),
            }
        )
        if len(parameters) >= 40:
            break

    unavailable_reason = (
        "A local AI model is not configured, so no clinical risk estimate was made."
    )
    no_risk = {"level": "Insufficient Data", "reason": unavailable_reason}
    return {
        "summary": (
            "The report text was extracted successfully. Basic laboratory rows were "
            "identified locally; a clinician should verify all values and interpretation."
        ),
        "parameters": parameters,
        "disease_risks": {
            "diabetes": dict(no_risk),
            "ckd": dict(no_risk),
            "anemia": dict(no_risk),
            "cardiovascular": dict(no_risk),
        },
    }
