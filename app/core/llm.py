import random
import re
import time

from google import genai
from google.genai import errors, types

from app.core.config import settings


client = genai.Client(
    api_key=settings.GOOGLE_API_KEY
)


class GeminiQuotaExceeded(RuntimeError):
    """Raised when Gemini's daily request quota is exhausted."""


def is_daily_quota_exceeded(error):
    """
    Detect Gemini daily free-tier request quota errors.
    """
    message = str(error).lower()

    return (
        "generaterequestsperday" in message
        or "generate_content_free_tier_requests" in message
        or "requestsperdayperprojectpermodel" in message
    )


def get_retry_delay(error):
    """
    Extract Google's suggested retry delay in seconds.
    """
    message = str(error)

    match = re.search(
        r"['\"]retryDelay['\"]:\s*['\"](\d+)s['\"]",
        message,
    )

    if match:
        return int(match.group(1))

    return None


def generate_response(prompt: str) -> str:
    max_attempts = 5
    base_delay = 2
    max_delay = 30

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=settings.GEMINI_TEMPERATURE
                )
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return response.text

        except errors.APIError as exc:
            status = getattr(exc, "code", None)

            # Stop immediately on daily quota exhaustion.
            if status == 429 and is_daily_quota_exceeded(exc):
                retry_delay = get_retry_delay(exc)

                print("\n[GEMINI DAILY QUOTA EXHAUSTED]")
                print(f"Model: {settings.GEMINI_MODEL}")

                if retry_delay is not None:
                    print(
                        "Suggested retry delay: "
                        f"{retry_delay / 3600:.2f} hours"
                    )

                print(
                    "Stopping retries to avoid "
                    "unnecessary API requests."
                )

                raise GeminiQuotaExceeded(
                    "Gemini daily free-tier quota exhausted. "
                    "Wait until Google resets the quota."
                ) from exc

            # Retry temporary errors, including short-term
            # rate limits, but not daily quota exhaustion.
            retryable = status in (
                429, 500, 502, 503, 504
            )

            if not retryable:
                raise

            if attempt == max_attempts:
                raise RuntimeError(
                    f"Gemini API unavailable after "
                    f"{max_attempts} attempts. "
                    f"Last error: {exc}"
                ) from exc

            delay = min(
                base_delay * (2 ** (attempt - 1)),
                max_delay
            ) + random.uniform(0, 1)

            print(
                f"[GEMINI RETRY] Attempt "
                f"{attempt}/{max_attempts} failed "
                f"(HTTP {status}). "
                f"Retrying in {delay:.1f} seconds..."
            )

            time.sleep(delay)