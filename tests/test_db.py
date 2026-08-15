import os
from datetime import datetime, timedelta, timezone

import pytest

from api.src import config

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="DATABASE_URL not set - these tests run real queries against a Postgres+pgvector database",
)

TEST_SOURCE = "test-db-py"


def _record(external_id: str, **overrides):
    from api.src.db import EventRecord
    from api.src.emotion_schema import EmotionClassification

    defaults = dict(
        external_id=external_id,
        subreddit="testsub",
        external_type="post",
        title=f"title {external_id}",
        body="body text",
        url=f"https://example.com/{external_id}",
        permalink=None,
        score=10,
        num_comments=2,
        created_at_source=datetime.now(timezone.utc) - timedelta(hours=1),
        embedding=[0.1] * 384,
        emotion=EmotionClassification(
            joy=0.1, trust=0.1, fear=0.1, surprise=0.1, sadness=0.1, disgust=0.1,
            anger=0.1, anticipation=0.1, valence=0.0, arousal=0.2,
            dominant_emotion="neutral", summary="a test post",
        ),
        claude_model="test-model",
        source=TEST_SOURCE,
    )
    defaults.update(overrides)
    return EventRecord(**defaults)


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    from api.src.db import _connect

    with _connect() as conn:
        conn.execute("delete from emotion_events where source = %s", (TEST_SOURCE,))


def test_migrations_apply_and_are_idempotent():
    from api.src.db import run_migrations

    first = run_migrations()
    second = run_migrations()

    assert second == [], f"expected no migrations re-applied on second run, got {second}"
    # First run may be [] too if a prior test run already applied them - both are fine,
    # what matters is the second run never re-applies anything.


def test_upsert_then_get_cached_round_trip():
    from api.src.db import get_cached, upsert_events

    record = _record("rt-1")
    upsert_events([record])

    cached = get_cached(["rt-1"], freshness_hours=config.CLASSIFICATION_FRESHNESS_HOURS)

    assert "rt-1" in cached
    fetched = cached["rt-1"]
    assert fetched.subreddit == "testsub"
    assert fetched.emotion.dominant_emotion == "neutral"
    assert len(fetched.embedding) == 384
    assert fetched.embedding[0] == pytest.approx(0.1, abs=1e-3)


def test_upsert_same_external_id_updates_not_duplicates():
    from api.src.db import get_cached, upsert_events

    upsert_events([_record("dup-1", score=10)])
    upsert_events([_record("dup-1", score=999)])

    cached = get_cached(["dup-1"], freshness_hours=config.CLASSIFICATION_FRESHNESS_HOURS)
    assert cached["dup-1"].score == 999, "expected get_cached to reflect the second upsert's score"

    # get_cached alone wouldn't catch a broken upsert that inserted a second row instead of
    # updating in place - it dedupes by dict key. Check the row count directly too.
    from api.src.db import _connect
    with _connect() as conn:
        rows = conn.execute(
            "select count(*), max(score) from emotion_events where source = %s and external_id = %s",
            (TEST_SOURCE, "dup-1"),
        ).fetchone()
    assert rows[0] == 1, "expected exactly one row after two upserts with the same external_id"
    assert rows[1] == 999, "expected the second upsert's score to win"


def test_freshness_window_is_based_on_classified_at_not_created_at_source():
    """upsert_events always stamps classified_at = now(), regardless of the post's own age -
    freshness is about how recently *we classified it*, not how old the Reddit post is."""
    from api.src.db import get_cached, upsert_events

    old_post = _record("stale-1", created_at_source=datetime.now(timezone.utc) - timedelta(hours=48))
    upsert_events([old_post])

    # A real post's age doesn't make the cache entry stale...
    cached = get_cached(["stale-1"], freshness_hours=6)
    assert "stale-1" in cached, "expected a just-classified row to be cached regardless of the post's own age"

    # ...only how long ago classified_at itself was does. classified_at was set to now() a
    # moment ago, so a zero-width freshness window should already exclude it.
    cached = get_cached(["stale-1"], freshness_hours=0)
    assert "stale-1" not in cached, "expected a 0-hour freshness window to exclude anything already classified"
