from dataclasses import asdict
from datetime import datetime, timezone

from fastapi import APIRouter, Query

from .. import config, db
from ..ranking import cluster_into_storylines, score_storylines
from ..schemas import LandscapeResponse, StorylineOut

router = APIRouter()


@router.get("/landscape", response_model=LandscapeResponse)
async def get_landscape(
    subreddits: str | None = Query(default=None, description="Comma-separated; defaults to REDDIT_SUBREDDITS"),
    limit: int = Query(default=20, ge=1, le=100),
    window_hours: float = Query(default=72, gt=0, le=24 * 14),
) -> LandscapeResponse:
    subs = [s.strip() for s in subreddits.split(",") if s.strip()] if subreddits else config.REDDIT_SUBREDDITS

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
