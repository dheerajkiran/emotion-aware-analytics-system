import hashlib
from datetime import datetime, timezone

import praw

from . import config
from .schema import ContentEvent

# Not a security boundary - just keeps raw usernames out of the database. A fixed,
# hardcoded salt is fine for that purpose (pseudonymization, not authentication).
_AUTHOR_HASH_SALT = "emotion-aware-analytics-system"


def get_client() -> praw.Reddit:
    return praw.Reddit(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        user_agent=config.REDDIT_USER_AGENT,
    )


def _hash_author(name: str | None) -> str | None:
    if not name:
        return None
    return hashlib.sha256(f"{_AUTHOR_HASH_SALT}:{name}".encode()).hexdigest()[:16]


def normalize_submission(submission) -> ContentEvent:
    author_name = getattr(submission.author, "name", None)
    return ContentEvent(
        external_id=submission.id,
        subreddit=str(submission.subreddit),
        external_type="post",
        title=submission.title,
        body=submission.selftext or "",
        url=submission.url,
        permalink=f"https://reddit.com{submission.permalink}",
        score=submission.score,
        num_comments=submission.num_comments,
        created_at_source=datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
        author_hash=_hash_author(author_name),
    )


def fetch_posts(subreddit_name: str, limit: int = 25, listing: str = "hot") -> list[ContentEvent]:
    """Fetch and normalize posts from one subreddit. `listing` is 'hot', 'rising', 'new', or 'top'."""
    reddit = get_client()
    subreddit = reddit.subreddit(subreddit_name)
    fetcher = getattr(subreddit, listing)

    events = []
    for submission in fetcher(limit=limit):
        if submission.stickied:
            continue  # pinned mod posts, not organic discussion
        events.append(normalize_submission(submission))
    return events


def fetch_all(subreddit_names: list[str], limit_per_subreddit: int = 25, listing: str = "hot") -> list[ContentEvent]:
    events = []
    for name in subreddit_names:
        events.extend(fetch_posts(name, limit=limit_per_subreddit, listing=listing))
    return events
