"""
Requirement parser — uses the LLM to understand what the recruiter is looking for.

The problem: a recruiter types something like "Customer Success Manager, 3+ years,
fintech / financial services background, in Bangalore or Delhi NCR" in plain English.

How do we extract structured fields from this? A regular expression would be fragile:
- "fintech background" should map to "financial services" industry
- "Bangalore or Delhi NCR" are two locations
- "3+ years" means minimum experience of 3

I decided to use the LLM for this because:
1. It understands synonyms and context ("fintech" = "financial services")
2. It handles varied phrasing ("3+ years", "at least 3 years", "3yr exp")
3. If the LLM fails, we just return an empty requirement and match everyone

The structured fields then get passed to the rule-based matcher for pre-filtering.
"""

import logging
from typing import Optional

from app.llm_client import LLMClient
from app.models import ParsedRequirement

logger = logging.getLogger(__name__)

# ── Prompt Engineering ─────────────────────────────────────────────────────
# I spent some time crafting this prompt. Key decisions:
# - I ask for "title_keywords" instead of "title" because breaking the title
#   into individual words makes matching more flexible (e.g., "Customer Success
#   Manager" → ["customer", "success", "manager"] matches "Customer Success Associate")
# - I include common mappings for industry terms (fintech → financial services)
# - I explicitly tell the LLM to return empty lists instead of null for missing fields
# - Example input/output helps the LLM understand the expected format

PARSE_SYSTEM_PROMPT = """You are a requirement parser for a recruiting system. 
Your job is to extract structured information from a plain-language hiring requirement.

Extract the following fields from the requirement text:
1. title_keywords: Key words from the job title (e.g., for "Customer Success Manager", extract ["customer", "success", "manager"])
2. min_experience: The minimum years of experience required (as a number). If no experience mentioned, set to null.
3. industries: Target industries mentioned (e.g., "fintech" → ["financial services", "fintech"]). Map common terms:
   - "fintech" → ["financial services", "fintech"]
   - "tech" → ["technology", "computer software", "internet"]
   - "healthcare" → ["hospital & health care"]
   If no industry mentioned, use empty list [].
4. locations: Target locations. Extract city names. If "remote" is mentioned or implied, include "Remote". 
   Multiple locations may be mentioned (e.g., "Bangalore or Delhi NCR").
   If no location mentioned, use empty list [].
5. required_skills: Key skills explicitly mentioned (e.g., "communication", "leadership"). Empty list if none.

Return ONLY valid JSON. No markdown, no explanation.

Example input: "Customer Success Manager, 3+ years, fintech background, in Bangalore"
Example output:
{
  "title_keywords": ["customer", "success", "manager"],
  "min_experience": 3,
  "industries": ["financial services", "fintech"],
  "locations": ["Bangalore"],
  "required_skills": []
}
"""


def parse_requirement(
    text: str,
    llm_client: Optional[LLMClient] = None,
) -> ParsedRequirement:
    """
    Turn a plain-English hiring requirement into structured ParsedRequirement.

    Steps:
    1. Check if the text is empty (return empty requirement if so)
    2. Send the text to the LLM with the parsing prompt
    3. Parse the JSON response into a ParsedRequirement object
    4. If anything fails, return an empty requirement (graceful degradation)

    I chose graceful degradation (return empty instead of crashing) because
    an empty requirement means "match everyone" which is better than
    "the API is broken".

    Args:
        text: The hiring requirement in plain English.
        llm_client: LLM client to use. Creates a new one if not provided.

    Returns:
        ParsedRequirement with extracted fields (or all defaults if parsing failed).
    """
    if not text or not text.strip():
        logger.warning("Empty requirement text received — returning empty requirement")
        return ParsedRequirement()

    client = llm_client or LLMClient()

    try:
        logger.info("Parsing requirement: '%s'", text[:100])
        result = client.call_json(prompt=text, system_prompt=PARSE_SYSTEM_PROMPT)

        parsed = ParsedRequirement(
            title_keywords=result.get("title_keywords", []),
            min_experience=result.get("min_experience"),
            industries=result.get("industries", []),
            locations=result.get("locations", []),
            required_skills=result.get("required_skills", []),
        )

        logger.info(
            "Parsed: title=%s, exp=%s, industry=%s, location=%s, skills=%s",
            parsed.title_keywords,
            parsed.min_experience,
            parsed.industries,
            parsed.locations,
            parsed.required_skills,
        )

        return parsed

    except (ValueError, ConnectionError, RuntimeError) as e:
        # If LLM parsing fails, return empty requirement
        # The matcher will just return all candidates un-filtered
        # This is better than crashing the whole request
        logger.error("Failed to parse requirement (returning empty): %s", e)
        return ParsedRequirement()
