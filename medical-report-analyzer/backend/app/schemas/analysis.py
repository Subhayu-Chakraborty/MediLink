"""
app/schemas/analysis.py
────────────────────────
Pydantic schemas for the structured analysis result returned by Ollama.
These match the exact JSON contract that the Ollama prompt produces.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel


class MedicalParameter(BaseModel):
    """A single extracted laboratory parameter from the report."""
    name: str
    value: Any                            # can be float or string
    unit: str
    status: str                           # "Normal" | "Low" | "High" | "Critical"
    reference_range: Optional[str] = None


class DiseaseRiskItem(BaseModel):
    """Risk assessment for a single disease."""
    level: str                            # "Low Risk" | "Moderate Risk" | "High Risk" | "Insufficient Data"
    reason: str


class DiseaseRisks(BaseModel):
    """Disease risk breakdown for the four supported conditions."""
    diabetes: DiseaseRiskItem
    ckd: DiseaseRiskItem
    anemia: DiseaseRiskItem
    cardiovascular: DiseaseRiskItem


class AnalysisResult(BaseModel):
    """
    Full analysis result — mirrors the exact JSON returned by Ollama.
    Also returned by GET /analysis/{report_id}.
    """
    report_id: str
    summary: str
    parameters: List[MedicalParameter] = []
    disease_risks: DiseaseRisks
    analyzed_at: datetime


class AnalysisTriggerResponse(BaseModel):
    """Returned by POST /analysis/{report_id} after triggering analysis."""
    report_id: str
    status: str
    message: str
