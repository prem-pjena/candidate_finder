"""
Candidate scorer — uses the LLM to judge how well each candidate fits.

After the rule-based pre-filter narrows candidates down, this module uses
the LLM for the actual scoring. The LLM can understand nuance that rules
can't:
  - "Content Marketing Specialist" → transferable customer-facing skills?
  - "3 years in telecommunications" → relevant for fintech?
  - "Account Manager" → similar enough to "Customer Success Manager"?

I batch candidates (5 per call) to reduce API calls. With ~150 candidates
and 5 per batch, that's ~30 LLM calls instead of 150.
"""

import json
import logging
from typing import Optional

from app.config import settings
from app.llm_client import LLMClient
from app.models import Candidate, ParsedRequirement, ScoredCandidate

logger = logging.getLogger(__name__)

# ── Scoring Prompt ─────────────────────────────────────────────────────────
# I spent time designing this prompt to get consistent, fair scores.
# Key design decisions:
# 1. Explicit scoring guidelines (90-100, 70-89, etc.) — helps the LLM calibrate
# 2. Mention missing data handling explicitly — "don't penalize heavily"
# 3. Ask for transferable skills consideration — catches career changers
# 4. JSON format requirement — makes parsing automatic
# 5. Low temperature (0.2) — keeps scores consistent across calls

SCORING_SYSTEM_PROMPT = """You are a recruiter evaluating candidates for a job opening.
You will be given a job requirement and a list of candidates.
For each candidate, evaluate how well they match the requirement.

Consider:
1. **Title match**: Is the candidate's job title related to the required role? (e.g., "Customer Success Associate" matches "Customer Success Manager" — related)
2. **Experience**: Does the candidate have enough years of experience? If experience is "Not specified", make a reasonable assumption based on their title and skills.
3. **Industry**: Is the candidate's industry relevant? If industry is "Not specified", don't penalize heavily.
4. **Location**: Is the candidate in a target location? "Remote" candidates can work from anywhere.
5. **Skills**: Does the candidate have relevant skills?

For each candidate, respond with:
- "score": A number from 0 to 100 (0 = no match, 100 = perfect match)
- "reason": A brief, specific reason (10-20 words) explaining the score. Mention what matched and what didn't.

Be fair to candidates with missing data — don't give 0 just because industry or experience is unknown.
Consider transferable skills and career transitions.

Scoring guidelines:
- 90-100: Perfect match on title, experience, industry, location, and skills
- 70-89: Strong match — most criteria align
- 50-69: Decent match — some criteria align, some don't
- 25-49: Weak match — few criteria align
- 0-24: Poor match — most criteria don't align

You MUST respond with valid JSON in this exact format:
{"scores": [{"name": "Candidate Name", "score": 85, "reason": "..."}, ...]}
"""


def score_candidates(
    candidates: list[Candidate],
    requirement: ParsedRequirement,
    llm_client: Optional[LLMClient] = None,
) -> list[ScoredCandidate]:
    """
    Score all shortlisted candidates using the LLM.

    Process:
    1. Build a readable description of the requirement
    2. Split candidates into batches of 5
    3. Send each batch to the LLM for scoring
    4. Parse the JSON responses
    5. Sort by score descending and assign ranks

    If batch scoring fails, we fall back to scoring one candidate at a time.
    If that also fails, we assign a default score of 30 (so the candidate
    isn't completely lost).

    Args:
        candidates: Shortlisted candidates from the pre-filter.
        requirement: The parsed hiring requirement.
        llm_client: LLM client to use. Creates one if not provided.

    Returns:
        Scored candidates sorted by score (highest first).
    """
    if not candidates:
        logger.warning("No candidates to score — returning empty list")
        return []

    client = llm_client or LLMClient()
    all_scores: list[ScoredCandidate] = []
    batch_size = settings.BATCH_SIZE

    # Convert the parsed requirement into a readable string for the LLM
    req_description = _build_requirement_description(requirement)

    # Process candidates in batches
    # I use range(0, len, batch_size) to create non-overlapping chunks
    total_batches = (len(candidates) + batch_size - 1) // batch_size
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i : i + batch_size]
        batch_num = i // batch_size + 1
        logger.info(
            "Scoring batch %d/%d (%d candidates)",
            batch_num,
            total_batches,
            len(batch),
        )

        batch_scores = _score_batch(batch, req_description, client)
        all_scores.extend(batch_scores)

    # Sort by score descending (best matches first)
    all_scores.sort(key=lambda x: x.score, reverse=True)

    # Assign ranks (1 = best match)
    for rank, scored in enumerate(all_scores, start=1):
        scored.rank = rank

    logger.info("Scoring complete: %d candidates scored", len(all_scores))
    return all_scores


def _build_requirement_description(requirement: ParsedRequirement) -> str:
    """
    Turn the structured requirement into readable text for the LLM.
    
    Format:
        Job Title: Customer Success Manager
        Minimum Experience: 3 years
        Industry: financial services, fintech
        Location: Bangalore, Delhi NCR
    """
    parts = []

    if requirement.title_keywords:
        parts.append(f"Job Title: {' '.join(requirement.title_keywords).title()}")

    if requirement.min_experience is not None:
        parts.append(f"Minimum Experience: {requirement.min_experience} years")

    if requirement.industries:
        parts.append(f"Industry: {', '.join(requirement.industries)}")

    if requirement.locations:
        parts.append(f"Location: {', '.join(requirement.locations)}")

    if requirement.required_skills:
        parts.append(f"Required Skills: {', '.join(requirement.required_skills)}")

    return "\n".join(parts) if parts else "General position (no specific criteria)"


def _score_batch(
    batch: list[Candidate],
    req_description: str,
    client: LLMClient,
) -> list[ScoredCandidate]:
    """
    Send a batch of candidates to the LLM for scoring.

    If the batch JSON call fails, falls back to scoring candidates
    individually. This two-tier approach handles the common failure mode
    where the LLM returns malformed JSON for large batches.
    """
    # Build the prompt with all candidates in this batch
    candidates_text = "\n".join(
        f"[{i+1}] {c.to_profile_string()}" for i, c in enumerate(batch)
    )

    prompt = f"""Job Requirement:
{req_description}

Candidates to evaluate:
{candidates_text}

Evaluate each candidate and return scores and reasons as JSON.
"""

    try:
        response = client.call_json(
            prompt=prompt,
            system_prompt=SCORING_SYSTEM_PROMPT,
            temperature=0.2,
            max_tokens=2000,
        )

        return _parse_scores_from_response(response, batch)

    except (ValueError, RuntimeError, ConnectionError) as e:
        logger.warning("Batch scoring failed, trying fallback: %s", e)
        return _fallback_scoring(batch, req_description, client)


def _parse_scores_from_response(
    response: dict, batch: list[Candidate]
) -> list[ScoredCandidate]:
    """
    Convert the LLM's JSON response into ScoredCandidate objects.
    
    The LLM returns something like:
    {"scores": [{"name": "Priya Sharma", "score": 92, "reason": "..."}, ...]}
    
    I match candidates by name (case-insensitive) because the LLM might
    not preserve the exact case from the input.
    """
    scores_data = response.get("scores", [])
    if not scores_data:
        logger.warning("No 'scores' key or empty scores array in LLM response")
        return []

    # Build a lookup by lowercase name for case-insensitive matching
    name_to_candidate = {c.name.lower(): c for c in batch}

    results = []
    for item in scores_data:
        name = item.get("name", "")
        score = item.get("score", 0)
        reason = item.get("reason", "No reason provided")

        # Clamp score to valid range (0-100)
        # The LLM might return 110 or -5, so we enforce bounds
        score = max(0, min(100, int(score)))

        # Find the matching candidate by name
        candidate = name_to_candidate.get(name.lower().strip())
        if candidate is None:
            logger.warning("LLM returned score for unknown candidate: %s", name)
            continue

        results.append(
            ScoredCandidate(
                name=candidate.name,
                title=candidate.title,
                location=candidate.location,
                experience=candidate.years_experience,
                score=score,
                reason=reason,
            )
        )

    return results


def _fallback_scoring(
    batch: list[Candidate],
    req_description: str,
    client: LLMClient,
) -> list[ScoredCandidate]:
    """
    Fallback when batch scoring fails — score one candidate at a time.

    Why a fallback? Local LLMs can sometimes return wonky JSON when given
    too many candidates at once. By scoring one at a time with simpler
    prompts, we're more likely to get valid responses.

    The downside is it's slower (one API call per candidate instead of
    one per 5 candidates), but it's better than returning no scores.
    """
    results = []

    for candidate in batch:
        try:
            # Simpler prompt with just one candidate
            prompt = f"""Job Requirement:
{req_description}

Candidate:
{candidate.to_profile_string()}

Rate this candidate's fit for the job from 0-100. Respond with ONLY a JSON object:
{{"score": <number>, "reason": "<brief reason>"}}"""

            response = client.call_json(
                prompt=prompt,
                system_prompt="You are a recruiter evaluating a candidate.",
                temperature=0.2,
                max_tokens=500,
            )

            score = max(0, min(100, int(response.get("score", 0))))
            reason = response.get("reason", "No reason provided")

            results.append(
                ScoredCandidate(
                    name=candidate.name,
                    title=candidate.title,
                    location=candidate.location,
                    experience=candidate.years_experience,
                    score=score,
                    reason=reason,
                )
            )

        except Exception as e:
            # Even individual scoring failed — give a default score of 30
            # I picked 30 because it's below the threshold (50), so the
            # candidate won't appear in results unless we're desperate.
            # But it's not 0, which would completely exclude them.
            logger.warning("Fallback scoring failed for %s: %s", candidate.name, e)
            results.append(
                ScoredCandidate(
                    name=candidate.name,
                    title=candidate.title,
                    location=candidate.location,
                    experience=candidate.years_experience,
                    score=30,
                    reason="Could not evaluate with LLM — assigned default score",
                )
            )

    return results
