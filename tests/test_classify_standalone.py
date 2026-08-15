import json
import os
from pathlib import Path

import pytest

from api.src import config  # noqa: F401 - importing loads .env before the skip-check below reads it

pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set - classification tests make real (cheap, Haiku) API calls",
)

FIXTURES = json.loads((Path(__file__).parent / "fixtures" / "sample_texts.json").read_text())

# Unambiguous enough to hard-assert the dominant emotion; the rest just get schema/range checks.
UNAMBIGUOUS_IDS = {"joy-1", "fear-1", "anger-1", "sadness-1"}


@pytest.mark.parametrize("fixture", FIXTURES, ids=[f["id"] for f in FIXTURES])
async def test_classify_returns_valid_scores(fixture):
    from api.src.classify import classify_text

    result = await classify_text(fixture["text"])

    for field in ("joy", "trust", "fear", "surprise", "sadness", "disgust", "anger", "anticipation"):
        score = getattr(result, field)
        assert 0 <= score <= 1, f"{field}={score} out of [0,1]"
    assert -1 <= result.valence <= 1
    assert 0 <= result.arousal <= 1
    assert result.summary.strip()

    if fixture["id"] in UNAMBIGUOUS_IDS:
        assert result.dominant_emotion == fixture["expected_dominant"], (
            f"{fixture['id']}: expected {fixture['expected_dominant']}, got {result.dominant_emotion} "
            f"(scores={result.scores()})"
        )


async def test_neutral_text_has_low_intensity():
    from api.src.classify import classify_text

    neutral = next(f for f in FIXTURES if f["id"] == "neutral-1")
    result = await classify_text(neutral["text"])

    assert abs(result.valence) < 0.4, f"expected near-neutral valence, got {result.valence}"
    assert result.arousal < 0.5, f"expected low arousal, got {result.arousal}"
