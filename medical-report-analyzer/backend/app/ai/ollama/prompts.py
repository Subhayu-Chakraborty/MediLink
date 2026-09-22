"""
app/ai/ollama/prompts.py
─────────────────────────
Medical analysis prompt templates for the Ollama API.

The prompt instructs Ollama to return ONLY a valid JSON object
matching the AnalysisResult schema. The output is not medical diagnosis
— it is an AI-based risk assessment for informational purposes only.
"""

from __future__ import annotations

SYSTEM_CONTEXT = """You are a medical AI assistant that analyzes laboratory and diagnostic report text.
Your role is to extract structured information and provide AI-based risk assessments.

CRITICAL RULES:
1. Return ONLY a valid JSON object — no markdown code fences, no explanation text, no preamble.
2. Do NOT claim to diagnose any medical condition. Use risk level language only.
3. If a parameter is mentioned but no value is found, do not include it.
4. Use the exact risk levels: "Low Risk", "Moderate Risk", "High Risk", "Insufficient Data"
5. The summary must clearly state this is AI-based informational analysis, not a medical diagnosis.
"""

ANALYSIS_PROMPT_TEMPLATE = """
Analyze the following medical report text and return a structured JSON assessment.

MEDICAL REPORT TEXT:
---
{report_text}
---

Return ONLY the following JSON structure (no other text):
{{
  "summary": "Brief AI-generated summary of the report findings. Must include disclaimer that this is informational only and not a medical diagnosis.",
  "parameters": [
    {{
      "name": "Parameter name (e.g. Hemoglobin)",
      "value": "Numeric or text value",
      "unit": "Unit of measurement (e.g. g/dL)",
      "status": "Normal | Low | High | Critical",
      "reference_range": "e.g. 12-16 g/dL (leave empty string if not available)"
    }}
  ],
  "disease_risks": {{
    "diabetes": {{
      "level": "Low Risk | Moderate Risk | High Risk | Insufficient Data",
      "reason": "Brief explanation of relevant indicators found (e.g. HbA1c, FPG, glucose values)"
    }},
    "ckd": {{
      "level": "Low Risk | Moderate Risk | High Risk | Insufficient Data",
      "reason": "Brief explanation of relevant indicators found (e.g. creatinine, eGFR, BUN, uric acid)"
    }},
    "anemia": {{
      "level": "Low Risk | Moderate Risk | High Risk | Insufficient Data",
      "reason": "Brief explanation of relevant indicators found (e.g. hemoglobin, hematocrit, MCV, RBC)"
    }},
    "cardiovascular": {{
      "level": "Low Risk | Moderate Risk | High Risk | Insufficient Data",
      "reason": "Brief explanation of relevant indicators found (e.g. cholesterol, LDL, HDL, triglycerides)"
    }}
  }}
}}

Rules:
- Extract ALL numeric parameters mentioned in the report with their values, units, and reference ranges.
- Determine status (Normal/Low/High/Critical) based on reference ranges or standard clinical norms.
- For disease risks, base assessment on parameters present in the report.
- If insufficient data exists for a disease, use "Insufficient Data" level.
- The summary should be 2-3 sentences, patient-friendly language, with a disclaimer.
"""


def build_analysis_prompt(extracted_text: str) -> str:
    """
    Construct the full prompt to send to Ollama.

    Args:
        extracted_text: Plain text extracted from the PDF report.

    Returns:
        Formatted prompt string ready for the Ollama API.
    """
    return ANALYSIS_PROMPT_TEMPLATE.format(report_text=extracted_text[:8000])
