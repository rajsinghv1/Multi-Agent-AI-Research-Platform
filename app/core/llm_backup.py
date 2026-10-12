import random
import time

from google import genai
from google.genai import errors, types

from app.core.config import settings


client = genai.Client(
    api_key=settings.GOOGLE_API_KEY
)


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

            # Retry only temporary API errors.
            retryable = status in (429, 500, 502, 503, 504)

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