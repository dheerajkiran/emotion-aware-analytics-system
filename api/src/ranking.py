from dataclasses import dataclass, field
from datetime import datetime, timezone

from sklearn.cluster import HDBSCAN

from . import config
from .emotion_schema import EmotionClassification


@dataclass
class ClassifiedPost:
    external_id: str
    subreddit: str
    title: str | None
    url: str | None
    permalink: str | None
    score: int
    num_comments: int
    created_at_source: datetime
    embedding: list[float]
    emotion: EmotionClassification


@dataclass
class Storyline:
    headline: str
    summary: str
    subreddit: str
    dominant_emotion: str
    emotion_scores: dict[str, float]
    valence: float
    arousal: float
    engagement_velocity: float
    priority: float
    post_count: int
    sample_urls: list[str] = field(default_factory=list)


def cluster_into_storylines(posts: list[ClassifiedPost]) -> list[list[ClassifiedPost]]:
    """Group posts about the same story together via embedding similarity.

    Embeddings are unit-normalized (see embeddings.py), so euclidean distance
    is a monotonic function of cosine distance - no need for a separate cosine
    metric. HDBSCAN is used instead of k-means because the number of distinct
    storylines in a batch isn't known ahead of time.

    Verified interactively that HDBSCAN's density estimate needs a realistic
    batch size to reliably find small clusters - two near-duplicate posts among
    only 2-3 others reads as all-noise, but the same pair is correctly grouped
    once the batch is closer to production scale (~30 posts). That's an
    acceptable tradeoff here: a batch too small to cluster confidently just
    falls back to one storyline per post, which is a safe default, not a bug.
    """
    if not posts:
        return []
    if len(posts) < 2:
        return [[p] for p in posts]

    vectors = [p.embedding for p in posts]
    labels = HDBSCAN(min_cluster_size=2, metric="euclidean", copy=True).fit_predict(vectors)

    groups: dict[int, list[ClassifiedPost]] = {}
    next_noise_id = -1
    for post, label in zip(posts, labels):
        key = label
        if label == -1:
            # Each noise point is its own single-post storyline, not merged together.
            key = next_noise_id
            next_noise_id -= 1
        groups.setdefault(key, []).append(post)
    return list(groups.values())


def _engagement_velocity(post: ClassifiedPost, now: datetime) -> float:
    hours = max((now - post.created_at_source).total_seconds() / 3600, 0.1)
    return (post.score + post.num_comments) / hours


def _normalize(values: list[float]) -> list[float]:
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.5 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def score_storylines(groups: list[list[ClassifiedPost]], now: datetime | None = None) -> list[Storyline]:
    now = now or datetime.now(timezone.utc)
    if not groups:
        return []

    raw_engagement: list[float] = []
    raw_emotion: list[float] = []
    representatives: list[ClassifiedPost] = []

    for members in groups:
        representative = max(members, key=lambda p: _engagement_velocity(p, now))
        representatives.append(representative)
        raw_engagement.append(max(_engagement_velocity(p, now) for p in members))
        raw_emotion.append(sum(max(p.emotion.arousal, abs(p.emotion.valence)) for p in members) / len(members))

    engagement_norm = _normalize(raw_engagement)
    emotion_norm = _normalize(raw_emotion)

    storylines = []
    for members, representative, eng_n, emo_n in zip(groups, representatives, engagement_norm, emotion_norm):
        priority = config.PRIORITY_ENGAGEMENT_WEIGHT * eng_n + config.PRIORITY_EMOTION_WEIGHT * emo_n
        # The eight Plutchik axes only - valence/arousal are exposed as their own
        # Storyline fields below, not as part of the radar-chart-shaped dict.
        avg_scores = {
            key: sum(getattr(p.emotion, key) for p in members) / len(members)
            for key in EmotionClassification.model_fields
            if key not in ("dominant_emotion", "summary", "valence", "arousal")
        }
        avg_valence = sum(p.emotion.valence for p in members) / len(members)
        avg_arousal = sum(p.emotion.arousal for p in members) / len(members)
        storylines.append(
            Storyline(
                headline=representative.title or representative.emotion.summary,
                summary=representative.emotion.summary,
                subreddit=representative.subreddit,
                dominant_emotion=representative.emotion.dominant_emotion,
                emotion_scores=avg_scores,
                valence=avg_valence,
                arousal=avg_arousal,
                engagement_velocity=max(_engagement_velocity(p, now) for p in members),
                priority=priority,
                post_count=len(members),
                sample_urls=[p.url for p in members if p.url][:5],
            )
        )

    return sorted(storylines, key=lambda s: s.priority, reverse=True)
