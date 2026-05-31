"""
Tests for the data loader module.

Focuses on:
- Loading valid JSON data
- Handling missing fields
- Handling malformed records
- Edge cases (empty arrays, null values)
"""

import json
import tempfile
from pathlib import Path

import pytest

from app.data_loader import load_candidates


def test_load_valid_candidates():
    """Should load valid candidate records correctly."""
    data = [
        {
            "id": "cand_001",
            "name": "Priya Sharma",
            "title": "Customer Success Manager",
            "company": "Fintech Corp",
            "industry": "financial services",
            "location": "Bangalore",
            "years_experience": 5,
            "skills": ["Communication", "CRM"],
        }
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f_path = f.name

    try:
        candidates = load_candidates(f_path)
        assert len(candidates) == 1
        assert candidates[0].name == "Priya Sharma"
        assert candidates[0].industry == "financial services"
        assert candidates[0].years_experience == 5
        assert candidates[0].skills == ["Communication", "CRM"]
    finally:
        Path(f_path).unlink(missing_ok=True)


def test_missing_optional_fields():
    """Should handle missing optional fields (industry, company, years_experience) with None."""
    data = [
        {
            "id": "cand_002",
            "name": "Rahul Verma",
            "title": "Engineer",
            "location": "Bangalore",
            # Missing: company, industry, years_experience
        }
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f_path = f.name

    try:
        candidates = load_candidates(f_path)
        assert len(candidates) == 1
        assert candidates[0].company is None
        assert candidates[0].industry is None
        assert candidates[0].years_experience is None
    finally:
        Path(f_path).unlink(missing_ok=True)


def test_missing_skills():
    """Missing skills field should become an empty list."""
    data = [
        {
            "id": "cand_003",
            "name": "Ananya",
            "title": "Manager",
            "location": "Mumbai",
        }
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f_path = f.name

    try:
        candidates = load_candidates(f_path)
        assert len(candidates) == 1
        assert candidates[0].skills == []
    finally:
        Path(f_path).unlink(missing_ok=True)


def test_null_skills():
    """Null skills field should become an empty list."""
    data = [
        {
            "id": "cand_004",
            "name": "Test",
            "title": "CSM",
            "location": "Remote",
            "skills": None,
        }
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f_path = f.name

    try:
        candidates = load_candidates(f_path)
        assert len(candidates) == 1
        assert candidates[0].skills == []
    finally:
        Path(f_path).unlink(missing_ok=True)


def test_skip_records_without_id():
    """Records without an id should be skipped."""
    data = [
        {
            "name": "No ID",
            "title": "Engineer",
            "location": "Bangalore",
        },
        {
            "id": "cand_005",
            "name": "Has ID",
            "title": "Manager",
            "location": "Pune",
        },
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f_path = f.name

    try:
        candidates = load_candidates(f_path)
        assert len(candidates) == 1
        assert candidates[0].name == "Has ID"
    finally:
        Path(f_path).unlink(missing_ok=True)


def test_skip_records_without_name():
    """Records without a name should be skipped."""
    data = [
        {
            "id": "cand_006",
            "title": "Engineer",
            "location": "Bangalore",
        },
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f_path = f.name

    try:
        candidates = load_candidates(f_path)
        assert len(candidates) == 0
    finally:
        Path(f_path).unlink(missing_ok=True)


def test_file_not_found():
    """Should raise FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError):
        load_candidates("/nonexistent/path/candidates.json")


def test_empty_json_array():
    """Empty JSON array should return empty list."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([], f)
        f_path = f.name

    try:
        candidates = load_candidates(f_path)
        assert candidates == []
    finally:
        Path(f_path).unlink(missing_ok=True)
