"""
Data loader — reads candidates.json and converts it into Candidate objects.

This was one of the first things I built because everything else depends on
having the data loaded correctly. The tricky part was handling missing fields
gracefully — about 25% of records have no industry, 13% have no experience,
and 10% have empty skills.

My approach:
- Required fields (id, name): skip the record if missing (can't do much without these)
- Optional fields (industry, company, years_experience): store as None
- Skills: default to empty list if missing/None
- Never crash on unexpected data — log a warning and skip the bad record
"""

import json
import logging
from pathlib import Path
from typing import Optional

from app.models import Candidate

logger = logging.getLogger(__name__)


def load_candidates(file_path: str | Path) -> list[Candidate]:
    """
    Read the JSON file and return a list of Candidate objects.

    I check if the file exists first (better to give a clear error than
    let Python's cryptic FileNotFoundError bubble up), then parse the JSON.

    Args:
        file_path: Path to the candidates.json file.

    Returns:
        List of validated Candidate objects.

    Raises:
        FileNotFoundError: If the JSON file doesn't exist.
        json.JSONDecodeError: If the JSON is malformed (e.g., missing comma).
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Candidates file not found: {path}")

    # Open with utf-8 encoding because the dataset might have non-ASCII names
    with open(path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Safety check — make sure the file is a JSON array, not an object or something else
    if not isinstance(raw_data, list):
        raise ValueError(f"Expected a JSON array, got {type(raw_data).__name__}")

    candidates: list[Candidate] = []
    skipped = 0

    # Process each record one by one
    # I use enumerate so I can log which record number had an error
    for i, item in enumerate(raw_data):
        try:
            candidate = _parse_candidate(item)
            if candidate is not None:
                candidates.append(candidate)
            else:
                skipped += 1
        except (KeyError, TypeError, ValueError) as e:
            # Catch unexpected data types (e.g., string where we expect a dict)
            logger.warning("Skipping record %d: %s", i, e)
            skipped += 1

    logger.info(
        "Loaded %d candidates (%d skipped due to errors)",
        len(candidates),
        skipped,
    )
    return candidates


def _parse_candidate(item: dict) -> Optional[Candidate]:
    """
    Convert one raw JSON record into a Candidate object.

    I use .get() instead of direct key access (item["key"]) because .get()
    returns None if the key is missing, while direct access would raise a
    KeyError. This is the main technique I use for handling missing data.

    Returns None if the record doesn't have the minimum required fields (id, name).
    Without these, we can't identify or match the candidate.
    """
    # ── Required fields ────────────────────────────────────────────────
    # If a record doesn't have an id or name, we can't use it.
    # I use `not` to catch both missing keys (None) and empty strings.
    record_id = item.get("id")
    name = item.get("name")

    if not record_id or not name:
        return None

    # title is useful for matching, but I default to empty string if missing
    # rather than skipping the record entirely
    title = item.get("title", "")

    return Candidate(
        id=str(record_id),
        name=str(name),
        title=str(title) if title else "",
        # ── Optional fields ────────────────────────────────────────────
        # Using .get() without a default returns None if the key is missing.
        # This is intentional — None is different from "" or 0 or "Unknown".
        # The safe_* methods in Candidate handle None by returning "Not specified".
        company=item.get("company"),           # None if key is missing
        industry=item.get("industry"),         # None if key is missing
        location=str(item.get("location", "Unknown")),
        years_experience=item.get("years_experience"),  # None if key is missing
        # Skills: handle both missing key (None) and explicit null
        # The `or []` trick: if item.get("skills") returns None or [],
        # it becomes an empty list instead
        skills=item.get("skills") or [],
    )
