import asyncio
from dataclasses import asdict
from datetime import datetime, timezone

from fastapi import APIRouter, Query

from .. import config, db, reddit_source
from ..classify import classify_text
from ..embeddings import embed_texts
from ..ranking import cluster_into_storylines, score_storylines
from ..schema import ContentEvent, filter_by_engagement
from ..schemas import LandscapeResponse, StorylineOut

router = APIRouter()

CLASSIFY_CONCURRENCY = 8


async def _classify_one(semaphore: asyncio.Semaphore, event: ContentEvent):
    async with semaphore:
        try:
            return event, await classify_text(event.text_for_classification), None
        except Exception as exc:  # noqa: BLE001 - one bad post shouldn't fail the whole request
            return event, None, exc


async def ensure_classified(events: list[ContentEvent]) -> int:
    """Classify+embed+write anything not already cached within the freshness window.

    Returns how many were newly classified (0 if everything was already fresh).
    """
    if not events:
        return 0

    cached = db.get_cached([e.external_id for e in events], config.CLASSIFICATION_FRESHNESS_HOURS)
    to_classify = [e for e in events if e.external_id not in cached]
    if not to_classify:
        return 0

    semaphore = asyncio.Semaphore(CLASSIFY_CONCURRENCY)
    results = await asyncio.gather(*(_classify_one(semaphore, e) for e in to_classify))
    ok = [(event, emotion) for event, emotion, err in results if err is None]
    if not ok:
        return 0

    vectors = embed_texts([event.text_for_classification for event, _ in ok])
    records = [
        db.EventRecord(
            external_id=event.external_id, subreddit=event.subreddit, external_type=event.external_type,
            title=event.title, body=event.body, url=event.url, permalink=event.permalink,
            score=event.score, num_comments=event.num_comments, created_at_source=event.created_at_source,
            embedding=vector, emotion=emotion, claude_model=config.CLAUDE_MODEL,
            author_hash=event.author_hash, source=event.source,
        )
        for (event, emotion), vector in zip(ok, vectors)
    ]
    db.upsert_events(records)
    return len(records)


@router.get("/landscape", response_model=LandscapeResponse)
async def get_landscape(
    subreddits: str | None = Query(default=None, description="Comma-separated; defaults to REDDIT_SUBREDDITS"),
    limit: int = Query(default=20, ge=1, le=100),
    window_hours: float = Query(default=72, gt=0, le=24 * 14),
    refresh: bool = Query(default=True, description="Fetch fresh Reddit posts before ranking"),
    posts_per_subreddit: int = Query(default=25, ge=5, le=100),
) -> LandscapeResponse:
    subs = [s.strip() for s in subreddits.split(",") if s.strip()] if subreddits else config.REDDIT_SUBREDDITS

    if refresh:
        events = reddit_source.fetch_all(subs, limit_per_subreddit=posts_per_subreddit)
        events = filter_by_engagement(events, config.MIN_ENGAGEMENT_SCORE)
        await ensure_classified(events)

    records = db.get_recent(subs, window_hours=window_hours)
    posts = [db.to_classified_post(r) for r in records]

    groups = cluster_into_storylines(posts)
    storylines = score_storylines(groups)[:limit]

    return LandscapeResponse(
        generated_at=datetime.now(timezone.utc).isoformat(),
        subreddits=subs,
        post_count=len(posts),
        storyline_count=len(storylines),
        storylines=[StorylineOut(**asdict(s)) for s in storylines],
    )
