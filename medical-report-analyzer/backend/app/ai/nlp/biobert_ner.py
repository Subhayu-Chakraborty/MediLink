"""
app/ai/nlp/biobert_ner.py
──────────────────────────
Future Phase 2: BioBERT / ClinicalBERT Named Entity Recognition pipeline.
Extracts medical entities: diseases, symptoms, medications, lab values.

# TODO: Implement in Phase 2 — requires: transformers==4.40.0, torch==2.2.2
"""

from __future__ import annotations

from typing import List, Dict, Any


def run_ner(text: str) -> List[Dict[str, Any]]:
    """
    Run BioBERT NER on medical text and return a list of entity spans.

    Returns list of dicts like:
      [{"entity": "B-Disease", "word": "diabetes", "start": 10, "end": 17}, ...]

    # TODO: Implement in Phase 2
    """
    pass  # type: ignore[return-value]
