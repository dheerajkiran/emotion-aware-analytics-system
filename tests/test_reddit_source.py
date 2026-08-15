from datetime import datetime, timezone

from api.src.reddit_source import _hash_author, normalize_submission
from api.src.schema import filter_by_engagement


class FakeAuthor:
    def __init__(self, name):
        self.name = name


class FakeSubmission:
    def __init__(
        self,
        id="abc123",
        subreddit="technology",
        title="Some title",
        selftext="",
        url="https://example.com/article",
        permalink="/r/technology/comments/abc123/some_title/",
        score=100,
        num_comments=20,
        created_utc=1_700_000_000,
        author="some_user",
        stickied=False,
    ):
        self.id = id
        self.subreddit = subreddit
        self.title = title
        self.selftext = selftext
        self.url = url
        self.permalink = permalink
        self.score = score
        self.num_comments = num_comments
        self.created_utc = created_utc
        self.author = FakeAuthor(author) if author else None
        self.stickied = stickied

    def __str__(self):
        return self.subreddit


def test_normalize_submission_maps_fields_correctly():
    submission = FakeSubmission(
        id="xyz789", subreddit="news", title="Big news happened", selftext="Details here.",
        permalink="/r/news/comments/xyz789/big_news_happened/", score=5000, num_comments=1200,
    )
    event = normalize_submission(submission)

    assert event.external_id == "xyz789"
    assert event.subreddit == "news"
    assert event.external_type == "post"
    assert event.title == "Big news happened"
    assert event.body == "Details here."
    assert event.score == 5000
    assert event.num_comments == 1200
    assert event.permalink == "https://reddit.com/r/news/comments/xyz789/big_news_happened/"
    assert event.source == "reddit"


def test_normalize_submission_handles_link_post_with_no_selftext():
    submission = FakeSubmission(selftext="")
    event = normalize_submission(submission)
    assert event.body == ""
    assert event.title  # link posts still carry emotional content in the title alone


def test_normalize_submission_created_at_is_utc_datetime():
    submission = FakeSubmission(created_utc=1_700_000_000)
    event = normalize_submission(submission)
    assert event.created_at_source == datetime.fromtimestamp(1_700_000_000, tz=timezone.utc)
    assert event.created_at_source.tzinfo is not None


def test_normalize_submission_hashes_author_not_raw_username():
    submission = FakeSubmission(author="real_username")
    event = normalize_submission(submission)
    assert event.author_hash is not None
    assert event.author_hash != "real_username"
    assert "real_username" not in event.author_hash


def test_normalize_submission_handles_deleted_author():
    submission = FakeSubmission(author=None)
    event = normalize_submission(submission)
    assert event.author_hash is None


def test_hash_author_is_deterministic_and_distinct():
    a1 = _hash_author("alice")
    a2 = _hash_author("alice")
    b = _hash_author("bob")
    assert a1 == a2
    assert a1 != b


def test_filter_by_engagement_drops_low_score_posts():
    events = [normalize_submission(FakeSubmission(id=str(i), score=score)) for i, score in enumerate([5, 50, 500])]
    filtered = filter_by_engagement(events, min_score=20)
    assert [e.score for e in filtered] == [50, 500]
