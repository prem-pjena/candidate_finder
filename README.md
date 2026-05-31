# 🎯 Candidate Finder API

> A FastAPI-powered service that uses local LLMs to find the best-matching candidates from a dataset based on plain-language hiring requirements.

Built for the **SkillVeda Engineering Assignment (Junior)**.

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)
- [Configuration](#configuration)
- [API Usage](#api-usage)
- [How It Works (Deep Dive)](#how-it-works-deep-dive)
- [Handling Missing Data](#handling-missing-data)
- [Sample Run](#sample-run)
- [Running Tests](#running-tests)
- [What I'd Improve With More Time](#what-id-improve-with-more-time)
- [Project Structure](#project-structure)

---

## ✨ Features

- **🔍 Plain-language search** — Recruiters describe what they want in normal English, no complex query syntax needed
- **🤖 LLM-powered understanding** — Uses a local LLM (LM Studio) to parse requirements and score candidates
- **🎯 Smart scoring** — Each candidate gets a 0-100 match score with a human-readable explanation
- **🔄 Auto-broaden** (bonus) — If fewer than 20 good candidates are found, automatically relaxes constraints once
- **🛡️ Missing data handling** — Never crashes on missing fields. Handles null industry, experience, skills gracefully

---

## 🏗️ Architecture

The system uses a **hybrid approach**: combine fast rule-based pre-filtering with nuanced LLM scoring.

```
Recruiter: "Customer Success Manager, 3+ years, fintech background, Bangalore"
     │
     ▼
┌── Step 1: Parse ──────────────────────────────────────────────┐
│  Send requirement text to LLM                                 │
│  LLM extracts: title_keywords, min_experience, industries,    │
│               locations, required_skills                      │
│                                                                │
│  Why LLM here?                                                 │
│  "Fintech background" → rules can't map this to               │
│  "financial services" industry. The LLM understands context.  │
└────────────────────────────────────────────────────────────────┘
     │
     ▼
┌── Step 2: Pre-filter ─────────────────────────────────────────┐
│  Apply simple rules to all 500 candidates:                     │
│  • Title keywords match?                                      │
│  • Location matches target city or is Remote?                 │
│  • Experience >= minimum? (null = keep, don't exclude)        │
│  • Industry bonus (soft signal, not a hard filter)            │
│                                                                │
│  Result: 500 candidates → ~50-150 shortlist                    │
│                                                                │
│  Why rules first?                                              │
│  Scoring 500 candidates with an LLM would be slow. Rules      │
│  quickly eliminate obviously wrong matches for free.          │
└────────────────────────────────────────────────────────────────┘
     │
     ▼
┌── Step 3: Score ──────────────────────────────────────────────┐
│  Send shortlisted candidates to LLM in batches of 5            │
│  LLM returns {score: 0-100, reason: "..."} for each           │
│                                                                │
│  Why LLM here?                                                 │
│  Nuanced judgment: "A Content Marketing Specialist might     │
│  have transferable customer-facing skills for a CSM role."    │
│  Rules alone would miss this.                                 │
└────────────────────────────────────────────────────────────────┘
     │
     ▼
┌── Step 4: Rank & Return ──────────────────────────────────────┐
│  Sort by score descending, return top 20                       │
│  Each result includes: name, title, score, reason             │
│                                                                │
│  Bonus: If < 20 candidates score > 50/100, auto-broaden       │
│  (relax constraints, re-score, merge results)                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Web framework — modern, fast, auto-generated docs |
| **Uvicorn** | ASGI server to run the API |
| **OpenAI Python SDK** | Communicate with OpenAI-compatible APIs (LM Studio) |
| **Pydantic** | Data validation — powers FastAPI's request/response models |
| **Python 3.10+** | Runtime |
| **pytest** | Unit testing |

---

## 🔧 Setup Instructions

### Prerequisites

- Python 3.10 or higher
- [LM Studio](https://lmstudio.ai/) installed and running with a model loaded
- LM Studio's API server running (default: `http://localhost:1234`)

### Steps

```bash
# 1. Navigate to the project
cd candidate_finder

# 2. Create a virtual environment (keep dependencies isolated)
python3 -m venv venv

# 3. Activate the virtual environment
# On macOS / Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment variables
cp .env.example .env
# Edit .env if needed (defaults work with standard LM Studio setup)

# 6. Make sure LM Studio is running with API server enabled
#    (Settings → Local Inference Server → Start)
#    Default URL: http://localhost:1234

# 7. Run the API!
uvicorn main:app --reload
```

The API will be available at **http://localhost:8000**.
Open **http://localhost:8000/docs** for the interactive Swagger UI.

---

## ⚙️ Configuration

All configuration is done via environment variables (or `.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_BASE_URL` | `http://localhost:1234/v1` | Your LLM API endpoint (LM Studio, Ollama, OpenAI) |
| `LLM_API_KEY` | `not-needed` | API key (LM Studio doesn't require one) |
| `LLM_MODEL` | `local-model` | Model name to use |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |

---

## 📡 API Usage

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/search` | Search candidates |
| `GET` | `/docs` | Swagger UI (interactive docs) |

### Search Example

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "requirement": "Customer Success Manager, 3+ years, fintech / financial services background, in Bangalore or Delhi NCR."
  }'
```

### Response

```json
{
  "query": "Customer Success Manager, 3+ years, fintech / financial services background, in Bangalore or Delhi NCR.",
  "total_results": 20,
  "broaden_used": false,
  "results": [
    {
      "rank": 1,
      "name": "Priya Sharma",
      "title": "Customer Success Manager",
      "location": "Bangalore",
      "experience": 5,
      "score": 92,
      "reason": "CSM title matches, 5 years exp (>3 required), financial services industry, Bangalore location"
    }
  ]
}
```

### Auto-broaden (Bonus Feature)

Pass `"broaden": true` in the request to enable auto-broaden:

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "requirement": "Senior Customer Success Manager, 8+ years, insurance, Pune",
    "broaden": true
  }'
```

If fewer than 20 candidates score above 50/100, the system will:
1. Relax the industry filter first (since 25% of data is missing industry anyway)
2. Then relax location if still needed
3. Re-score new candidates from the expanded pool
4. Merge and re-rank
5. Stop after one broaden attempt (no infinite loops)

---

## 🧠 How It Works (Deep Dive)

### Step 1: Parse the Requirement

**What happens:** The plain-text requirement is sent to the LLM with a structured prompt asking it to extract specific fields.

**Example:** *"Customer Success Manager, 3+ years, fintech / financial services background, in Bangalore or Delhi NCR."*

The LLM returns:
```json
{
  "title_keywords": ["customer", "success", "manager"],
  "min_experience": 3,
  "industries": ["financial services", "fintech"],
  "locations": ["Bangalore", "Delhi NCR"],
  "required_skills": []
}
```

**Why the LLM?** A rule-based parser would struggle with:
- "fintech background" → should map to "financial services" industry
- "Bangalore or Delhi NCR" → two locations, different formats
- "3+ years" → should extract as integer 3
- Misspellings or varied phrasing

### Step 2: Pre-filter with Rules

**What happens:** Each of the 500 candidates gets a quick rule-based score (0-100) based on:

| Criteria | Weight | Logic |
|----------|--------|-------|
| Title match | 40 pts | Does the candidate's title contain the required keywords? |
| Location match | 30 pts | Is the candidate in a target city or Remote? |
| Experience | 20 pts | Does the candidate have >= minimum years? |
| Industry | 10 pts | Soft signal — industry relevance |

**Why rules?** Rules are fast and free. They narrow 500 candidates to ~50-150 before we make any LLM calls, saving significant time and compute.

### Step 3: Score with LLM

**What happens:** Candidates are sent to the LLM in batches of 5. The LLM evaluates each one and returns a score (0-100) and a short reason.

**The scoring prompt asks the LLM to consider:**
1. **Title match** — Is the job title related? (e.g., "Customer Success Associate" → related to "Customer Success Manager")
2. **Experience** — Does experience meet or exceed requirements?
3. **Industry** — Is the industry relevant?
4. **Location** — Is location in the target area?
5. **Skills** — Does the candidate have relevant skills?

**Why the LLM?** Nuanced understanding:
- "Account Manager" ↔ "Customer Success Manager" (similar skills)
- 3 years in telecom → transferable to fintech
- Missing data doesn't mean bad candidate

### Step 4: Rank & Return

Simple sort by score, take top 20, assign ranks. Each result includes the reason so the recruiter understands *why*.

### Bonus: Auto-broaden

If fewer than 20 candidates score above 50/100, the system:
1. Drops the industry filter (25% of data is missing industry — too strict)
2. Finds new candidates that weren't in the first pass
3. Scores them with the relaxed requirement
4. Merges with original results, re-ranks, returns top 20

---

## 🛡️ Handling Missing Data

The dataset has ~500 records with realistic data quality issues. Here's how each field is handled:

| Field | Missing % | Strategy |
|-------|-----------|----------|
| **industry** | ~25% | `None` in model → "Not specified" in prompt → LLM scores neutrally (not 0). Never excluded by pre-filter — gets partial credit. |
| **years_experience** | ~13% | `None` in model → "Not specified" in prompt → LLM treats as unknown (scores lower than matching, higher than insufficient). Not excluded by pre-filter. |
| **skills** | ~10% empty | Empty list → "None listed" in prompt → LLM scores lower but doesn't penalize to 0. |
| **company** | ~10% | `None` → "Not specified" in prompt. Minimal impact — company is a weak signal for matching. |

**Key principle:** *Never crash on missing data. Never exclude someone just because one field is blank. Let the LLM make a holistic judgment.*

### How This Plays Out in Code

```python
# In models.py — Optional fields handle None gracefully
class Candidate(BaseModel):
    industry: Optional[str] = None
    years_experience: Optional[int] = None

# In data_loader.py — Missing fields use None, not sentinel values
candidate = Candidate(
    industry=item.get("industry"),  # None if missing
    years_experience=item.get("years_experience"),  # None if missing
)

# In matcher.py — Null experience gets partial credit, not exclusion
if candidate.years_experience is None:
    return (8, 20)  # Partial credit instead of excluding

# In scorer.py — Prompt says "Not specified" and LLM handles it
"Industry: Not specified" → LLM scores neutrally
```

---

## 📊 Sample Run

Full sample output is in [`SAMPLE_OUTPUT.md`](SAMPLE_OUTPUT.md).

### Quick Preview

**Query:** *"Customer Success Manager, 3+ years, fintech / financial services background, in Bangalore or Delhi NCR."*

```
Rank | Name               | Title                         | Score | Reason
─────┼────────────────────┼───────────────────────────────┼───────┼──────────────────────────────────────
  1  | Suresh Nair        | Customer Success Manager      |  92   | CSM in fintech, 4yr, Delhi NCR
  2  | Priya Sharma       | Customer Success Manager      |  90   | CSM in fintech, 5yr, Bangalore
  3  | Amit Kumar         | Customer Success Manager      |  85   | CSM, 6yr, Remote (flexible)
  ...
```

---

## 🧪 Running Tests

```bash
# Make sure you're in the project root and venv is activated
cd candidate_finder
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_matcher.py -v

# Run with coverage (if installed)
# pip install pytest-cov
# pytest --cov=app tests/
```

---

## 💡 What I'd Improve With More Time

1. **Parallel scoring** — Currently score candidates sequentially in batches. With async + concurrent LLM calls, we could score all candidates much faster.

2. **Vector embeddings** — Instead of rule-based pre-filtering, use semantic embeddings (e.g., sentence-transformers) to find similar candidates. This would capture semantic similarity better than keyword matching.

3. **Caching** — Cache parsed requirements and search results for frequent queries. Many recruiters search for similar roles.

4. **Ensemble scoring** — Make multiple LLM scoring calls per candidate and average the scores. This would reduce variance from the LLM and give more consistent rankings.

5. **Error recovery** — If the LLM fails mid-scoring, retry with exponential backoff instead of falling back immediately.

6. **Docker** — Containerize the application with Docker for easy deployment: `docker compose up`

7. **Database** — Replace the JSON file with SQLite or PostgreSQL for better scalability and querying.

8. **Web UI** — A simple React/Vue frontend where recruiters can type requirements and see results visually.

---

## 📁 Project Structure

```
candidate_finder/
├── main.py                  # FastAPI app, routes, startup, orchestrator
├── requirements.txt         # Python dependencies
├── .env.example             # Configuration template
├── .gitignore
├── README.md                # This file
├── SAMPLE_OUTPUT.md         # Pre-computed sample run
│
├── app/
│   ├── __init__.py
│   ├── config.py            # Environment variable configuration
│   ├── models.py            # Pydantic models (Candidate, Request, Response)
│   ├── data_loader.py       # Load and parse candidates.json
│   ├── llm_client.py        # OpenAI-compatible LLM client (LM Studio)
│   ├── requirement_parser.py# LLM-based requirement parsing
│   ├── matcher.py           # Rule-based pre-filtering
│   └── scorer.py            # LLM-based batch scoring
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures
│   ├── test_data_loader.py  # Data loading tests
│   └── test_matcher.py      # Pre-filtering tests
│
├── candidates.json           # Dataset (500 records)
│
└── output/
    └── .gitkeep             # Search results export
```
