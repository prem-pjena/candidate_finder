"""
Tests for the candidate matcher module.

Focuses on:
- Title matching
- Location matching
- Experience filtering (including null handling)
- Industry soft matching
- Combined scoring
- Edge cases
"""

from app.matcher import (
    _match_experience,
    _match_industry,
    _match_location,
    _match_title,
    prefilter_candidates,
)
from app.models import Candidate, ParsedRequirement


def test_title_match_exact():
    """Exact title match should return max score."""
    c = Candidate(id="1", name="Test", title="Customer Success Manager", location="Bangalore")
    score, max_score = _match_title(c, ["customer", "success", "manager"])
    assert score == 40
    assert max_score == 40


def test_title_match_partial():
    """Partial title match should return partial score."""
    c = Candidate(id="1", name="Test", title="Customer Success Associate", location="Bangalore")
    score, max_score = _match_title(c, ["customer", "success", "manager"])
    # "customer" and "success" match, "manager" doesn't → 2/3 of 40
    assert score > 0
    assert score < 40


def test_title_match_none():
    """No title match should return 0."""
    c = Candidate(id="1", name="Test", title="Software Engineer", location="Bangalore")
    score, max_score = _match_title(c, ["customer", "success", "manager"])
    assert score == 0
    assert max_score == 40


def test_title_match_no_keywords():
    """No title keywords should return neutral score."""
    c = Candidate(id="1", name="Test", title="Anything", location="Bangalore")
    score, max_score = _match_title(c, [])
    assert score == 10
    assert max_score == 10


def test_location_exact_match():
    """Exact location match should return max score."""
    c = Candidate(id="1", name="Test", title="CSM", location="Bangalore")
    score, max_score = _match_location(c, ["Bangalore"])
    assert score == 30
    assert max_score == 30


def test_location_partial_match():
    """Partial location match should return partial score."""
    c = Candidate(id="1", name="Test", title="CSM", location="Delhi NCR")
    score, max_score = _match_location(c, ["Delhi NCR"])
    assert score == 30  # Exact match for "Delhi NCR"
    assert max_score == 30


def test_location_remote_gets_partial():
    """Remote candidates should get partial credit when location is specified."""
    c = Candidate(id="1", name="Test", title="CSM", location="Remote")
    score, max_score = _match_location(c, ["Bangalore"])
    assert score == 15  # Partial credit
    assert max_score == 30


def test_location_no_match():
    """No location match should return 0."""
    c = Candidate(id="1", name="Test", title="CSM", location="Mumbai")
    score, max_score = _match_location(c, ["Bangalore"])
    assert score == 0
    assert max_score == 30


def test_location_no_filter():
    """No location filter should return neutral score."""
    c = Candidate(id="1", name="Test", title="CSM", location="Mumbai")
    score, max_score = _match_location(c, [])
    assert score == 15
    assert max_score == 30


def test_experience_meets_requirement():
    """Candidate with enough experience should get max score."""
    c = Candidate(id="1", name="Test", title="CSM", location="Bangalore", years_experience=5)
    score, max_score = _match_experience(c, 3)
    assert score == 20
    assert max_score == 20


def test_experience_below_requirement():
    """Candidate below minimum experience should get 0."""
    c = Candidate(id="1", name="Test", title="CSM", location="Bangalore", years_experience=1)
    score, max_score = _match_experience(c, 5)
    assert score == 0
    assert max_score == 20


def test_experience_close_enough():
    """Candidate within 1 year of requirement should get partial score."""
    c = Candidate(id="1", name="Test", title="CSM", location="Bangalore", years_experience=2)
    score, max_score = _match_experience(c, 3)
    assert score == 10
    assert max_score == 20


def test_experience_null_gets_partial():
    """Candidate with null experience should get partial credit (not excluded)."""
    c = Candidate(id="1", name="Test", title="CSM", location="Bangalore", years_experience=None)
    score, max_score = _match_experience(c, 3)
    assert score == 8  # Partial credit
    assert max_score == 20


def test_experience_no_filter():
    """No experience filter should return neutral score."""
    c = Candidate(id="1", name="Test", title="CSM", location="Bangalore", years_experience=5)
    score, max_score = _match_experience(c, None)
    assert score == 10
    assert max_score == 20


def test_industry_exact_match():
    """Exact industry match should return max score."""
    c = Candidate(id="1", name="Test", title="CSM", location="Bangalore", industry="financial services")
    score, max_score = _match_industry(c, ["financial services"])
    assert score == 10
    assert max_score == 10


def test_industry_null_gets_partial():
    """Candidate with null industry should get partial credit."""
    c = Candidate(id="1", name="Test", title="CSM", location="Bangalore", industry=None)
    score, max_score = _match_industry(c, ["financial services"])
    assert score == 3  # Partial credit
    assert max_score == 10


def test_industry_no_match():
    """No industry match should return 0."""
    c = Candidate(id="1", name="Test", title="CSM", location="Bangalore", industry="retail")
    score, max_score = _match_industry(c, ["financial services"])
    assert score == 0
    assert max_score == 10


def test_industry_no_filter():
    """No industry filter should return neutral score."""
    c = Candidate(id="1", name="Test", title="CSM", location="Bangalore", industry="anything")
    score, max_score = _match_industry(c, [])
    assert score == 5
    assert max_score == 10


def test_prefilter_csm_in_bangalore(sample_candidates, csm_requirement):
    """
    Integration test: prefilter with CSM requirement.
    Should find CSM-related candidates in Bangalore/Delhi NCR with 3+ years.
    """
    result = prefilter_candidates(sample_candidates, csm_requirement)
    names = [c.name for c in result]

    # Priya (CSM, fintech, Bangalore, 5yr) should match well
    assert "Priya Sharma" in names
    # Rahul (Sr CSM, software, Delhi NCR, 8yr) should match
    assert "Rahul Verma" in names
    # Ananya (CS Associate, fintech, Mumbai, 2yr) — title related, but Mumbai not Bangalore
    assert "Ananya Gupta" in names  # Title has "customer" and "success"
    # Suresh (CSM, fintech, Delhi NCR, 4yr) should match well
    assert "Suresh Nair" in names
    # Neha (SWE, Pune) should NOT be in results
    assert "Neha Singh" not in names


def test_prefilter_no_requirement(sample_candidates, empty_requirement):
    """
    With no filters, should return up to max candidates (first N).
    """
    result = prefilter_candidates(sample_candidates, empty_requirement, max_candidates=150)
    assert len(result) == len(sample_candidates)


def test_prefilter_with_partial_matches(sample_candidates):
    """
    Candidates with missing data should still be included if they have title match.
    """
    req = ParsedRequirement(
        title_keywords=["customer", "success", "manager"],
        locations=["Bangalore"],
    )
    result = prefilter_candidates(sample_candidates, req)
    names = [c.name for c in result]

    # Vikram (Account Manager, no industry/exp, Bangalore) — title doesn't have "customer success"
    # So might not appear. But Deepika (Content Marketing, Hyderabad) definitely not.
    # Maya (Tech Support, Bangalore) — might appear due to location match
    assert "Maya Joshi" in names
