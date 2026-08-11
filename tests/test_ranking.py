import random
from datetime import datetime, timedelta, timezone

import pytest

from api.src import config
from api.src.emotion_schema import EmotionClassification
from api.src.ranking import ClassifiedPost, cluster_into_storylines, score_storylines

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _emotion(valence: float, arousal: float, dominant: str = "neutral") -> EmotionClassification:
    return EmotionClassification(
        joy=0, trust=0, fear=0, surprise=0, sadness=0, disgust=0, anger=0, anticipation=0,
        valence=valence, arousal=arousal, dominant_emotion=dominant, summary="a post",
    )


def _post(external_id: str, embedding: list[float], score=10, num_comments=5, hours_ago=1.0, **emotion_kwargs):
    return ClassifiedPost(
        external_id=external_id,
        subreddit="test",
        title=f"post {external_id}",
        url=f"https://example.com/{external_id}",
        permalink=None,
        score=score,
        num_comments=num_comments,
        created_at_source=NOW - timedelta(hours=hours_ago),
        embedding=embedding,
        emotion=_emotion(**emotion_kwargs) if emotion_kwargs else _emotion(0.0, 0.1),
    )


def test_near_duplicate_posts_cluster_together():
    # HDBSCAN's density estimate needs a realistic-sized batch to be stable - a
    # 2-point "cluster" among only 2-3 other points reliably reads as all-noise
    # (verified interactively), which isn't representative of real batches
    # (~30-50 posts/request). Match that scale here: two near-duplicates among
    # many scattered, mutually-distant singletons.
    rng = random.Random(0)
    a = _post("a", [1.0, 0.0, 0.0, 0.0])
    b = _post("b", [0.97, 0.03, 0.0, 0.0])
    scattered = [
        _post(f"s{i}", [rng.uniform(-1, 1) for _ in range(4)])
        for i in range(28)
    ]

    groups = cluster_into_storylines([a, b, *scattered])
    group_ids = [sorted(p.external_id for p in g) for g in groups]

    assert ["a", "b"] in group_ids, f"expected a and b to cluster together, got {group_ids}"


def test_single_and_empty_batches_dont_crash():
    assert cluster_into_storylines([]) == []
    solo = _post("solo", [1.0, 0.0])
    assert [[p.external_id for p in g] for g in cluster_into_storylines([solo])] == [["solo"]]


def test_high_engagement_and_high_emotion_storylines_both_surface():
    """A big-but-flat storyline and a small-but-intense one shouldn't let either dominate outright."""
    high_engagement = _post("popular", [1.0, 0.0], score=5000, num_comments=2000, valence=0.05, arousal=0.1)
    high_emotion = _post("intense", [0.0, 1.0], score=10, num_comments=2, valence=0.9, arousal=0.95)

    storylines = score_storylines([[high_engagement], [high_emotion]], now=NOW)
    priorities = {s.headline: s.priority for s in storylines}

    assert abs(priorities["post popular"] - priorities["post intense"]) < 0.01, (
        f"expected roughly equal priority with default 0.5/0.5 weights, got {priorities}"
    )


def test_priority_weights_actually_control_ranking(monkeypatch):
    high_engagement = _post("popular", [1.0, 0.0], score=5000, num_comments=2000, valence=0.05, arousal=0.1)
    high_emotion = _post("intense", [0.0, 1.0], score=10, num_comments=2, valence=0.9, arousal=0.95)

    monkeypatch.setattr(config, "PRIORITY_ENGAGEMENT_WEIGHT", 1.0)
    monkeypatch.setattr(config, "PRIORITY_EMOTION_WEIGHT", 0.0)
    engagement_only = score_storylines([[high_engagement], [high_emotion]], now=NOW)
    assert engagement_only[0].headline == "post popular"

    monkeypatch.setattr(config, "PRIORITY_ENGAGEMENT_WEIGHT", 0.0)
    monkeypatch.setattr(config, "PRIORITY_EMOTION_WEIGHT", 1.0)
    emotion_only = score_storylines([[high_engagement], [high_emotion]], now=NOW)
    assert emotion_only[0].headline == "post intense"


def test_storyline_headline_prefers_most_engaged_member_and_averages_emotion():
    quiet = _post("quiet", [1.0, 0.0], score=1, num_comments=0, valence=0.2, arousal=0.2)
    loud = _post("loud", [0.99, 0.01], score=900, num_comments=400, valence=0.8, arousal=0.8)

    storylines = score_storylines([[quiet, loud]], now=NOW)
    assert len(storylines) == 1
    story = storylines[0]

    assert story.headline == "post loud"
    assert story.post_count == 2
    assert story.valence == pytest.approx((0.2 + 0.8) / 2)
    assert story.arousal == pytest.approx((0.2 + 0.8) / 2)
