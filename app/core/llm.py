import random
import re
import time

from google import genai
from google.genai import errors, types

from app.core.config import settings


client = genai.Client(api_key=settings.GOOGLE_API_KEY)


class GeminiQuotaExceeded(RuntimeError):
    """Raised when Gemini quota is exhausted."""


class GeminiUnavailable(RuntimeError):
    """Raised when Gemini remains unavailable after retries."""


def is_daily_quota_exceeded(error):
    message = str(error).lower()

    daily_markers = (
        "generaterequestsperday",
        "generate_content_free_tier_requests",
        "requestsperdayperprojectpermodel",
        "per_day",
        "per day",
        "daily quota",
    )

    return any(marker in message for marker in daily_markers)


def get_retry_delay(error):
    """Extract suggested retry delay from Gemini error text."""
    message = str(error)

    patterns = (
        r"retryDelay['\"]?\s*:\s*['\"]?(\d+(?:\.\d+)?)s",
        r"retry in (\d+(?:\.\d+)?)s",
        r"retry after (\d+(?:\.\d+)?) seconds",
    )

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)

        if match:
            return float(match.group(1))

    return None


def generate_response(prompt: str) -> str:
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    max_attempts = 4
    base_delay = 2
    max_delay = 30

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=settings.GEMINI_TEMPERATURE
                ),
            )

            answer = response.text

            if not answer or not answer.strip():
                raise GeminiUnavailable(
                    "Gemini returned an empty response."
                )

            return answer.strip()

        except errors.APIError as exc:
            status = getattr(exc, "code", None)

            if status == 429 and is_daily_quota_exceeded(exc):
                print("[GEMINI] Daily quota exhausted.")

                raise GeminiQuotaExceeded(
                    "Gemini daily quota exhausted. "
                    "Check Google AI Studio usage and retry "
                    "when your quota becomes available."
                ) from exc

            retryable = status in (429, 500, 502, 503, 504)

            if not retryable:
                raise GeminiUnavailable(
                    f"Gemini request failed (HTTP {status})."
                ) from exc

            if attempt == max_attempts:
                raise GeminiUnavailable(
                    "Gemini quota/rate limit reached or service "
                    "temporarily unavailable. "
                    "Please try again later."
                ) from exc

            suggested_delay = get_retry_delay(exc)

            exponential_delay = min(
                base_delay * (2 ** (attempt - 1)),
                max_delay,
            )

            delay = (
                suggested_delay
                if suggested_delay is not None
                else exponential_delay + random.uniform(0, 1)
            )

            # Avoid waiting indefinitely in a Streamlit request.
            if delay > 60:
                raise GeminiUnavailable(
                    f"Gemini requested a retry after {delay:.0f} "
                    "seconds. Please try again later."
                ) from exc

            print(
                f"[GEMINI RETRY] Attempt {attempt}/{max_attempts}, "
                f"HTTP {status}. Retrying in {delay:.1f}s..."
            )

            time.sleep(delay)

    raise GeminiUnavailable("Gemini request failed.")