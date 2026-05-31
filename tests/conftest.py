"""
Shared test fixtures for unit tests.

Provides sample Candidate objects with various data quality scenarios
(missing fields, empty skills, etc.) so tests don't need to load
the real candidates.json.
"""

import pytest

from app.models import Candidate, ParsedRequirement


@pytest.fixture
def sample_candidates():
    """Return a list of sample candidates with various data scenarios."""
    return [
        Candidate(
            id="cand_001",
            name="Priya Sharma",
            title="Customer Success Manager",
            company="Fintech Corp",
            industry="financial services",
            location="Bangalore",
            years_experience=5,
            skills=["Communication", "CRM", "Customer Onboarding", "Data Analysis"],
        ),
        Candidate(
            id="cand_002",
            name="Rahul Verma",
            title="Senior Customer Success Manager",
            company="TechStartup",
            industry="computer software",
            location="Delhi NCR",
            years_experience=8,
            skills=["Team Leadership", "Account Management", "Renewals", "Negotiation"],
        ),
        Candidate(
            id="cand_003",
            name="Ananya Gupta",
            title="Customer Success Associate",
            company="FinServ Inc",
            industry="financial services",
            location="Mumbai",
            years_experience=2,
            skills=["Communication", "Customer Onboarding", "Zendesk"],
        ),
        Candidate(
            id="cand_004",
            name="Vikram Patel",
            title="Account Manager",
            company=None,  # Missing company
            industry=None,  # Missing industry
            location="Bangalore",
            years_experience=None,  # Missing experience
            skills=["Negotiation", "Client Relations", "Sales"],
        ),
        Candidate(
            id="cand_005",
            name="Neha Singh",
            title="Software Engineer",
            company="TechCorp",
            industry="computer software",
            location="Pune",
            years_experience=4,
            skills=["Python", "JavaScript", "Docker", "AWS"],
        ),
        Candidate(
            id="cand_006",
            name="Amit Kumar",
            title="Customer Success Manager",
            company="InsureCo",
            industry="insurance",
            location="Remote",
            years_experience=6,
            skills=["Churn Reduction", "Renewals", "Data Analysis", "Communication"],
        ),
        Candidate(
            id="cand_007",
            name="Deepika Reddy",
            title="Content Marketing Specialist",
            company="MarketingPro",
            industry="marketing and advertising",
            location="Hyderabad",
            years_experience=3,
            skills=["SEO", "Content Strategy", "HubSpot", "Data Analysis"],
        ),
        Candidate(
            id="cand_008",
            name="Suresh Nair",
            title="Customer Success Manager",
            company="BankTech",
            industry="financial services",
            location="Delhi NCR",
            years_experience=4,
            skills=["Customer Onboarding", "Account Management", "Compliance", "CRM"],
        ),
        Candidate(
            id="cand_009",
            name="Maya Joshi",
            title="Technical Support Specialist",
            company=None,
            industry=None,
            location="Bangalore",
            years_experience=3,
            skills=["Communication", "Problem Solving", "Zendesk", "Technical Support"],
        ),
        Candidate(
            id="cand_010",
            name="Raj Kapoor",
            title="Customer Success Lead",
            company="DataFlow",
            industry="information technology and services",
            location="Gurgaon",
            years_experience=7,
            skills=["Team Leadership", "Customer Onboarding", "Strategic Planning", "Analytics"],
        ),
    ]


@pytest.fixture
def csm_requirement():
    """Return a ParsedRequirement for CSM role."""
    return ParsedRequirement(
        title_keywords=["customer", "success", "manager"],
        min_experience=3,
        industries=["financial services", "fintech"],
        locations=["Bangalore", "Delhi NCR"],
        required_skills=["Communication", "CRM"],
    )


@pytest.fixture
def empty_requirement():
    """Return an empty requirement (no filters)."""
    return ParsedRequirement()
