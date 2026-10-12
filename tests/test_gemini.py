import os
import pytest

from app.core.llm import generate_response


@pytest.mark.live_api
def test_gemini_connection():

    if os.getenv("RUN_LIVE_GEMINI_TESTS", "false").lower() != "true":
        pytest.skip(
            "Live Gemini test disabled to save API quota."
        )

    prompt = (
        "Explain what an AI agent is "
        "in three simple sentences."
    )

    result = generate_response(prompt)

    assert isinstance(result, str)
    assert len(result.strip()) > 0