"""
app/ai/nlp/entity_extractor.py
───────────────────────────────
Future Phase 2: Post-processes BioBERT NER output into structured entities.
Maps raw entity spans to a clean {disease, medication, lab_value} schema.

# TODO: Implement in Phase 2
"""

from __future__ import annotations

from typing import Any, Dict, List


def extract_entities(ner_output: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Convert raw NER spans into a structured entity dictionary.

    Returns:
      {
        "diseases": ["Diabetes Mellitus", "Hypertension"],
        "medications": ["Metformin"],
        "lab_values": ["HbA1c: 8.2%"]
      }

    # TODO: Implement in Phase 2
    """
    pass  # type: ignore[return-value]
