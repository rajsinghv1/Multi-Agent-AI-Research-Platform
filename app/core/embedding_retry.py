import random
import re
import time
from google.genai import errors

RETRYABLE_CODES = {429, 500, 502, 503, 504}


def get_retry_seconds(error):
    message = str(error)
    patterns = (
        r"['\"]retryDelay['\"]\s*:\s*['\"](\d+(?:\.\d+)?)s",
        r"Please retry in\s+(\d+(?:\.\d+)?)s",
        r"retry after\s+(\d+(?:\.\d+)?)\s*seconds",
    )
    for pattern in patterns:
        match = re.search(pattern, message, flags=re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def embed_with_retry(embed_function, *args, max_attempts=5, **kwargs):
    for attempt in range(1, max_attempts + 1):
        try:
            return embed_function(*args, **kwargs)
        except errors.APIError as exc:
            status = getattr(exc, "code", None)
            if status not in RETRYABLE_CODES or attempt == max_attempts:
                raise
            recommended = get_retry_seconds(exc)
            delay = (recommended + 2.0) if recommended is not None else min(2 ** attempt, 60) + random.uniform(0, 1)
            print(f"[EMBEDDING RETRY] HTTP {status}; attempt {attempt}/{max_attempts}; wait {delay:.1f}s", flush=True)
            time.sleep(delay)
