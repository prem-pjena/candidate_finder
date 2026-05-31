"""
Pydantic models for the Candidate Finder API.

This file defines all the data structures used in the app. I'm using Pydantic
(built into FastAPI) because it gives us:
- Automatic validation — if someone sends bad data, Pydantic catches it early
- Type hints — makes the code self-documenting
- JSON serialization — FastAPI automatically converts these to/from JSON
- Default values — missing fields don't crash the app, they get sensible defaults

I put all models in one file because they're closely related and it's easier
to see everything at a glance. If the project grew bigger, I'd split them up.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════
# Internal Domain Models
# ═══════════════════════════════════════════════════════════════════════════
# These are used inside the app for business logic, not directly exposed to
# the API (though they may appear in responses).


class Candidate(BaseModel):
    """
    Represents one candidate from the dataset.

    I made company, industry, and years_experience Optional because the
    dataset has missing values for these fields. Using Optional means:
    - If the field is present → use the value
    - If the field is missing → store as None (don't crash!)
    
    Skills defaults to an empty list because some records have missing/null
    skills, and an empty list is easier to work with than None.
    """

    id: str
    name: str
    title: str
    company: Optional[str] = None
    industry: Optional[str] = None
    location: str
    years_experience: Optional[int] = None
    skills: list[str] = Field(default_factory=list)

    # ── "Safe" helper methods ──────────────────────────────────────────
    # These methods handle the None case by returning a placeholder string.
    # I use them when building prompts for the LLM so it never sees "None".
    # I learned this pattern from reading FastAPI examples — it's cleaner
    # than writing "if x is None else x" everywhere.

    def safe_industry(self) -> str:
        """Return the industry name, or 'Not specified' if it's missing."""
        return self.industry if self.industry else "Not specified"

    def safe_company(self) -> str:
        """Return the company name, or 'Not specified' if it's missing."""
        return self.company if self.company else "Not specified"

    def safe_experience(self) -> str:
        """
        Return years of experience as a string.
        
        If the experience is missing (None), we say 'Not specified' instead
        of crashing or showing 'None'. The LLM will handle this gracefully
        during scoring.
        """
        if self.years_experience is not None:
            return str(self.years_experience)
        return "Not specified"

    def safe_skills(self) -> str:
        """
        Return skills as a comma-separated string.
        
        If the skills list is empty, we say 'None listed' so the LLM knows
        the candidate has no listed skills (vs. missing data).
        """
        if self.skills:
            return ", ".join(self.skills)
        return "None listed"

    def to_profile_string(self) -> str:
        """
        Format the candidate as a readable one-line profile for LLM prompts.
        
        I created this method because I was copy-pasting the same format
        string everywhere. Now if I want to change how candidates appear
        in prompts, I just edit it in one place.
        """
        return (
            f"- {self.name}: {self.title} at {self.safe_company()}, "
            f"{self.safe_experience()} years exp, "
            f"Industry: {self.safe_industry()}, "
            f"Location: {self.location}, "
            f"Skills: [{self.safe_skills()}]"
        )


class ParsedRequirement(BaseModel):
    """
    Structured fields extracted from the plain-text hiring requirement.
    
    The LLM parses something like "Customer Success Manager, 3+ years,
    fintech background, in Bangalore" into these structured fields.
    The matcher then uses these fields to pre-filter candidates.
    
    All fields default to empty values so the app doesn't crash if the
    LLM fails to extract something.
    """

    title_keywords: list[str] = Field(
        default_factory=list,
        description="Keywords from the job title (e.g., ['customer', 'success', 'manager'])",
    )
    min_experience: Optional[int] = Field(
        default=None,
        description="Minimum years of experience required (None = not specified)",
    )
    industries: list[str] = Field(
        default_factory=list,
        description="Target industries (e.g., ['financial services', 'fintech'])",
    )
    locations: list[str] = Field(
        default_factory=list,
        description="Target locations (e.g., ['Bangalore', 'Delhi NCR'])",
    )
    required_skills: list[str] = Field(
        default_factory=list,
        description="Key skills mentioned in the requirement",
    )


class ScoredCandidate(BaseModel):
    """
    A candidate after LLM scoring — includes the match score and reason.
    
    This is what gets returned to the recruiter. The rank is assigned
    after sorting all scored candidates by score descending.
    """

    rank: int = 0
    name: str
    title: str
    location: str
    experience: Optional[int] = None
    score: int = Field(ge=0, le=100, description="Match score from 0 to 100")
    reason: str = Field(description="Short explanation of why this candidate matched")


# ═══════════════════════════════════════════════════════════════════════════
# API Request/Response Models
# ═══════════════════════════════════════════════════════════════════════════
# These are the models that FastAPI uses for request validation and response
# serialization. FastAPI automatically generates OpenAPI docs from these.


class SearchRequest(BaseModel):
    """
    What the recruiter sends to the /search endpoint.
    
    The 'requirement' field is required (min_length=1 ensures it's not empty).
    The 'broaden' field is optional and defaults to False.
    
    I used Field(min_length=1) instead of just str so FastAPI automatically
    returns a 400 error if someone sends an empty string, instead of the
    app crashing later with a confusing error.
    """

    requirement: str = Field(
        min_length=1,
        description=(
            "Plain-language hiring requirement. "
            "Example: 'Customer Success Manager, 3+ years, fintech background'"
        ),
    )
    broaden: bool = Field(
        default=False,
        description="Auto-broaden search if fewer than 20 good candidates are found",
    )


class SearchResponse(BaseModel):
    """
    The response sent back after searching.
    
    Contains the original query (so the recruiter can verify what they searched),
    the count of results, whether broadening was used, and the actual results.
    """

    query: str = Field(description="The original search query")
    total_results: int = Field(description="Number of results returned")
    broaden_used: bool = Field(
        description="Whether the search was automatically broadened"
    )
    results: list[ScoredCandidate] = Field(
        description="Top matching candidates, ranked by score"
    )


class HealthResponse(BaseModel):
    """Response for the health check endpoint."""

    status: str
    candidates_loaded: int
