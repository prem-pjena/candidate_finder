"""
Configuration for the Candidate Finder API.

I'm using environment variables (with a .env file) so that anyone running
this project can change settings without editing the code. This is a good
practice I learned — never hardcode configuration!

The dotenv library loads variables from .env into os.environ, so os.getenv
can find them. If a variable isn't set, I provide sensible defaults that
work with a standard LM Studio setup on localhost.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Find the .env file in the project root (one level up from app/)
# I use Path(__file__).resolve() to get the absolute path, which avoids
# issues when the script is run from different directories.
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Settings:
    """
    Holds all configuration values for the application.

    Using a class instead of global variables makes it easier to:
    1. See all config in one place
    2. Pass settings around as a single object
    3. Mock settings in tests if needed (though I haven't done that yet)
    """

    # ── LLM Configuration ──────────────────────────────────────────────
    # LM Studio runs a local API server that's compatible with OpenAI's API format.
    # The default URL is http://localhost:1234/v1 (this is what LM Studio uses).
    # If someone wants to use OpenAI or Ollama instead, they just change this URL.
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
    
    # LM Studio doesn't require an API key, but the OpenAI SDK expects one.
    # 'not-needed' is a placeholder that satisfies the SDK.
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "not-needed")
    
    # The model name as it appears in LM Studio (e.g., "llama-3.2-3b-instruct")
    # This gets passed to the API in every request.
    LLM_MODEL: str = os.getenv("LLM_MODEL", "local-model")

    # ── Server Configuration ───────────────────────────────────────────
    # 0.0.0.0 means "listen on all network interfaces" — useful for
    # testing from other devices on the same network.
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # ── Data Paths ─────────────────────────────────────────────────────
    # The candidates.json file. By default it's in the project root.
    # I had to use Path(__file__).resolve() to get the right path because
    # when uvicorn runs main.py, the "current working directory" might be
    # different from where you expect.
    CANDIDATES_PATH: str = os.getenv(
        "CANDIDATES_PATH",
        str(Path(__file__).resolve().parent.parent / "candidates.json"),
    )

    # ── Scoring Settings ───────────────────────────────────────────────
    # SCORE_THRESHOLD: Candidates scoring below 50/100 are not considered
    #   "good matches". I picked 50 as the threshold after thinking about
    #   it — it's the midpoint, so anything above is at least somewhat relevant.
    SCORE_THRESHOLD: int = 50
    
    # TOP_K: The assignment asks for top 20, so this is 20.
    TOP_K: int = 20
    
    # BATCH_SIZE: We send 5 candidates per LLM call. I tested different
    # batch sizes and found that 5 is a good balance — small enough that
    # the LLM doesn't get confused, but large enough to reduce API calls.
    BATCH_SIZE: int = 5


# Create a single global instance so all modules share the same settings.
# This is imported like: from app.config import settings
settings = Settings()
