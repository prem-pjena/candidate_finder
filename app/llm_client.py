"""
LLM client — talks to OpenAI-compatible APIs (LM Studio, Ollama, OpenAI, etc.).

I'm using the OpenAI Python SDK, but pointing it at a custom base_url.
This works because LM Studio (and Ollama, and others) implement the same
API format as OpenAI. So changing LLM_BASE_URL in .env is all we need to
switch between providers.

I learned about this trick from the LM Studio docs — they advertise
themselves as "OpenAI API compatible" which means any code written for
OpenAI just works with a URL change.
"""

import json
import logging
from typing import Optional

from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Wraps the OpenAI SDK to work with any OpenAI-compatible endpoint.

    Usage:
        client = LLMClient()
        response = client.call("What is the capital of France?")
        
    There's also call_json() for when you want the response parsed as JSON.
    I use this for requirement parsing and candidate scoring.

    I made temperature default to 0.1 (low) because for structured tasks
    like parsing and scoring, we want consistent, deterministic output.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Set up the client with configurable endpoint details.

        Each parameter defaults to the value from settings (which comes from .env).
        This lets us override them per-instance if needed (useful for testing).
        """
        self.base_url = base_url or settings.LLM_BASE_URL
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL

        # Initialize the OpenAI client with our custom base URL
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        logger.info(
            "LLMClient initialized with base_url=%s, model=%s",
            self.base_url,
            self.model,
        )

    def call(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ) -> str:
        """
        Send a prompt to the LLM and get the text response back.

        Args:
            prompt: The main question/instruction for the LLM.
            system_prompt: Optional system-level instruction (sets context/behavior).
            temperature: How "creative" the response should be (0 = deterministic, 1 = wild).
            max_tokens: Maximum length of the response.

        Returns:
            The LLM's text response, stripped of whitespace.

        Raises:
            ConnectionError: If the API endpoint is unreachable (e.g., LM Studio not running).
            RuntimeError: If the LLM returns an error or empty response.
        """
        # Build the message list in the format the OpenAI API expects
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Extract the text from the response object
            # The OpenAI SDK returns a complex object, not plain text
            content = response.choices[0].message.content
            if content is None:
                raise RuntimeError("LLM returned empty response (content was None)")

            return content.strip()

        except ConnectionError as e:
            # This happens when LM Studio isn't running or the URL is wrong
            logger.error("Failed to connect to LLM at %s: %s", self.base_url, e)
            raise ConnectionError(
                f"Cannot connect to LLM at {self.base_url}. "
                "Make sure LM Studio (or your provider) is running."
            ) from e
        except Exception as e:
            # Catch anything else (timeout, auth error, etc.)
            logger.error("LLM call failed: %s", e)
            raise RuntimeError(f"LLM call failed: {e}") from e

    def call_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ) -> dict:
        """
        Like call(), but expects the LLM to return JSON and parses it.

        I use this for requirement parsing and candidate scoring, where
        I need structured data back instead of free text.

        Args:
            Same as call().

        Returns:
            Parsed JSON dictionary.

        Raises:
            ValueError: If the LLM response isn't valid JSON.
        """
        # Append JSON instructions to the system prompt
        # I do this instead of putting it in the user prompt so the LLM
        # gets the instruction as a system-level constraint (more reliable)
        json_system = (
            system_prompt or ""
        ) + "\n\nYou MUST respond with valid JSON only. No markdown, no explanations."

        response_text = self.call(
            prompt=prompt,
            system_prompt=json_system,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # The response might have ```json ... ``` markers, so we clean it first
        return self._parse_json_response(response_text)

    @staticmethod
    def _parse_json_response(text: str) -> dict:
        """
        Try to extract and parse JSON from an LLM response.

        LLMs sometimes wrap JSON in ```json ... ``` code blocks even when
        told not to. This method strips those markers before parsing.

        I also handle the case where the response has trailing text after
        the JSON object. This is a common issue with local models.
        """
        text = text.strip()
        
        # Check if the response is wrapped in markdown code blocks
        if text.startswith("```"):
            # Find where the actual JSON starts (after ```json or ```)
            start = text.find("{")
            if start == -1:
                start = text.find("[")
            if start != -1:
                text = text[start:]
            
            # Find where the code block ends (the closing ```)
            end = text.rfind("```")
            if end != -1:
                text = text[:end].strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM JSON response: %s", e)
            logger.debug("Raw response (first 200 chars): %s", text[:200])
            raise ValueError(
                f"LLM returned invalid JSON. Response was: {text[:200]}..."
            ) from e
