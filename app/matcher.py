"""
Candidate matcher — rule-based pre-filtering.

This is the "efficiency" part of our hybrid approach. Before we ask the LLM
to score candidates (which costs time and compute), we quickly filter out
obviously bad matches using simple rules.

Why rules first?
  - Scoring 500 candidates with an LLM would take ~100 API calls (5 per batch)
    and several minutes. That's slow.
  - Rules are instant — we can scan all 500 in milliseconds.
  - By narrowing 500 → ~100, we save 80% of LLM calls.

How I picked the weights:
  - Title (40 pts): Most important signal — if the job title is completely
    different, the candidate probably isn't relevant.
  - Location (30 pts): Second most important — recruiters usually care about
    where the candidate is based.
  - Experience (20 pts): Important but missing data is common (13%).
  - Industry (10 pts): Soft signal — people change industries all the time.

Key principle for missing data:
  - Never exclude a candidate just because one field is blank
  - Missing industry? Partial credit. Missing experience? Partial credit.
  - The LLM will handle missing data during scoring by judging holistically
"""

import logging
from typing import Optional

from app.models import Candidate, ParsedRequirement

logger = logging.getLogger(__name__)


def prefilter_candidates(
    candidates: list[Candidate],
    requirement: ParsedRequirement,
    max_candidates: int = 150,
) -> list[Candidate]:
    """
    Narrow down candidates using rule-based matching.

    Each candidate gets a score (0-100) based on title match, location,
    experience, and industry. We keep the top max_candidates.

    I use percentage scores instead of hard cutoffs because:
    - Percentages let me rank candidates by relevance
    - I can set max_candidates to control LLM workload
    - The top N candidates are the most promising ones

    Args:
        candidates: Full list of 500 candidates.
        requirement: Parsed requirement from the LLM.
        max_candidates: Max shortlist size (keeps LLM scoring manageable).

    Returns:
        Shortlist of the most promising candidates.
    """
    # If there's no filter criteria, just return the first N candidates
    # This handles the edge case where LLM parsing failed
    if not requirement.title_keywords and not requirement.locations:
        logger.info("No filters to apply, returning first %d candidates", max_candidates)
        return candidates[:max_candidates]

    scored: list[tuple[Candidate, int]] = []

    for candidate in candidates:
        score = 0
        max_score = 0

        # ── Title Match (weight: 40 points) ──
        title_score, title_max = _match_title(candidate, requirement.title_keywords)
        score += title_score
        max_score += title_max

        # ── Location Match (weight: 30 points) ──
        loc_score, loc_max = _match_location(candidate, requirement.locations)
        score += loc_score
        max_score += loc_max

        # ── Experience Match (weight: 20 points) ──
        exp_score, exp_max = _match_experience(candidate, requirement.min_experience)
        score += exp_score
        max_score += exp_max

        # ── Industry Match (weight: 10 points — soft signal) ──
        ind_score, ind_max = _match_industry(candidate, requirement.industries)
        score += ind_score
        max_score += ind_max

        # Calculate percentage score
        if max_score > 0:
            pct = (score / max_score) * 100
        else:
            pct = 0

        # Only keep candidates with at least SOME title or location relevance
        # If neither matches, it's probably not a good fit
        if title_score > 0 or loc_score > 0:
            scored.append((candidate, pct))

    # Sort by match percentage (highest first)
    scored.sort(key=lambda x: x[1], reverse=True)

    shortlist = [c for c, _ in scored[:max_candidates]]
    logger.info(
        "Pre-filter: %d candidates → %d shortlisted",
        len(candidates),
        len(shortlist),
    )
    return shortlist


def _match_title(candidate: Candidate, title_keywords: list[str]) -> tuple[int, int]:
    """
    Check if the candidate's job title contains the required keywords.

    I split the title into keyword matching instead of exact title matching
    because:
    - "Customer Success Manager" should match "Senior Customer Success Manager"
    - "Customer Success Associate" is related to "Customer Success Manager"
    
    Returns (score, max_score). Max is 40 when keywords are provided.
    """
    if not title_keywords:
        return (10, 10)  # No title filter = neutral score

    title_lower = candidate.title.lower()
    # Count how many of the required keywords appear in the candidate's title
    matched = sum(1 for kw in title_keywords if kw.lower() in title_lower)

    if matched == 0:
        return (0, 40)

    # Partial match — some keywords matched, give proportional score
    ratio = matched / len(title_keywords)
    return (int(40 * ratio), 40)


def _match_location(
    candidate: Candidate, target_locations: list[str]
) -> tuple[int, int]:
    """
    Check if the candidate is in one of the target locations.

    I consider "Remote" candidates as flexible — they can work from anywhere,
    so they get partial credit even if the target is a specific city.

    Returns (score, max_score). Max is 30.
    """
    if not target_locations:
        return (15, 30)  # No location filter = neutral

    candidate_loc = candidate.location.lower()

    for target in target_locations:
        target_lower = target.lower()
        # Exact match (e.g., "Bangalore" == "Bangalore")
        if target_lower == candidate_loc:
            return (30, 30)
        # Partial match (e.g., "Delhi NCR" contains "delhi", or vice versa)
        if target_lower in candidate_loc or candidate_loc in target_lower:
            return (25, 30)

    # Remote candidates can work from anywhere — give partial credit
    if candidate.location.lower() == "remote":
        return (15, 30)

    return (0, 30)


def _match_experience(
    candidate: Candidate, min_experience: Optional[int]
) -> tuple[int, int]:
    """
    Check if the candidate has enough experience.

    If candidate's experience is missing (null), we give partial credit (8 out of 20)
    instead of excluding them. The LLM can judge their level from other signals.

    If they're close (within 1 year), we give partial credit too.
    
    Returns (score, max_score). Max is 20.
    """
    if min_experience is None:
        return (10, 20)  # No experience filter = neutral

    if candidate.years_experience is None:
        # Experience unknown — don't exclude, but give partial score
        # The LLM will assess their level during scoring
        return (8, 20)

    if candidate.years_experience >= min_experience:
        return (20, 20)
    else:
        # Close enough (within 1 year) — give some credit
        if candidate.years_experience >= max(0, min_experience - 1):
            return (10, 20)
        return (0, 20)


def _match_industry(
    candidate: Candidate, target_industries: list[str]
) -> tuple[int, int]:
    """
    Check if the candidate's industry is relevant.

    This is intentionally a soft signal (only 10 points max) because:
    - 25% of records have no industry listed
    - People switch industries all the time
    - A great candidate from a different industry can still be a good fit
    
    Returns (score, max_score). Max is 10.
    """
    if not target_industries:
        return (5, 10)  # No industry filter = neutral

    if candidate.industry is None:
        return (3, 10)  # Unknown industry — partial credit

    candidate_ind = candidate.industry.lower()

    for target in target_industries:
        target_lower = target.lower()
        if target_lower == candidate_ind:
            return (10, 10)
        # Partial match (e.g., "financial services" contains "financial")
        if target_lower in candidate_ind or candidate_ind in target_lower:
            return (8, 10)

    return (0, 10)
