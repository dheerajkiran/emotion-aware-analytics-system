from dataclasses import dataclass
from datetime import datetime


@dataclass
class ContentEvent:
    """A normalized piece of source content, before classification.

    Deliberately source-agnostic - reddit_source.py knows how to produce these
    from PRAW submissions, but nothing downstream (classification, embedding,
    ranking) needs to know the content came from Reddit specifically. Adding a
    second source later means writing another `*_source.py` that produces the
    same shape, not touching anything else.
    """

    external_id: str
    subreddit: str
    external_type: str  # 'post' | 'comment'
    title: str | None
    body: str
    url: str | None
    permalink: str | None
    score: int
    num_comments: int
    created_at_source: datetime
    author_hash: str | None = None
    source: str = "reddit"

    @property
    def text_for_classification(self) -> str:
        if self.title:
            return f"{self.title}\n\n{self.body}".strip()
        return self.body.strip()


def filter_by_engagement(events: list[ContentEvent], min_score: int) -> list[ContentEvent]:
    return [e for e in events if e.score >= min_score]
