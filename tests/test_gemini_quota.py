import pytest

from app.core.llm import (
    is_daily_quota_exceeded,
    get_retry_delay,
    GeminiQuotaExceeded,
)


def test_daily_quota_detection():
    error = (
        "429 RESOURCE_EXHAUSTED "
        "Quota exceeded for metric: "
        "generate_content_free_tier_requests"
    )

    assert is_daily_quota_exceeded(error) is True


def test_temporary_rate_limit():
    error = "429 Too many requests per minute"

    assert is_daily_quota_exceeded(error) is False


def test_retry_delay():
    error = "{'retryDelay': '57343s'}"

    assert get_retry_delay(error) == 57343


def test_no_retry_delay():
    assert get_retry_delay("HTTP 503") is None


def test_quota_exception():
    with pytest.raises(GeminiQuotaExceeded):
        raise GeminiQuotaExceeded("Daily quota exhausted")