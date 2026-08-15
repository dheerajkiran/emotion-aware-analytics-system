from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import psycopg
from pgvector.psycopg import register_vector

from . import config
from .emotion_schema import EmotionClassification
from .ranking import ClassifiedPost

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent.parent / "db" / "migrations"


@dataclass
class EventRecord:
    external_id: str
    subreddit: str
    external_type: str
    title: str | None
    body: str
    url: str | None
    permalink: str | None
    score: int
    num_comments: int
    created_at_source: datetime
    embedding: list[float]
    emotion: EmotionClassification
    claude_model: str
    author_hash: str | None = None
    source: str = "reddit"


def to_classified_post(record: EventRecord) -> ClassifiedPost:
    return ClassifiedPost(
        external_id=record.external_id,
        subreddit=record.subreddit,
        title=record.title,
        url=record.url,
        permalink=record.permalink,
        score=record.score,
        num_comments=record.num_comments,
        created_at_source=record.created_at_source,
        embedding=record.embedding,
        emotion=record.emotion,
    )


@contextmanager
def _connect():
    with psycopg.connect(config.DATABASE_URL, autocommit=True) as conn:
        try:
            register_vector(conn)
        except psycopg.ProgrammingError:
            # The vector extension doesn't exist yet - true only before migration 0001
            # has run. Skip registering the adapter; nothing on this connection needs
            # it until the extension (and the embedding column) actually exist.
            pass
        yield conn


def run_migrations() -> list[str]:
    """Apply any db/migrations/*.sql files not yet recorded as applied. Returns filenames applied."""
    applied = []
    with _connect() as conn:
        conn.execute(
            "create table if not exists schema_migrations "
            "(filename text primary key, applied_at timestamptz not null default now())"
        )
        already = {row[0] for row in conn.execute("select filename from schema_migrations").fetchall()}

        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if path.name in already:
                continue
            conn.execute(path.read_text())
            conn.execute("insert into schema_migrations (filename) values (%s)", (path.name,))
            applied.append(path.name)
    return applied


def get_cached(external_ids: list[str], freshness_hours: float) -> dict[str, EventRecord]:
    """Rows classified within freshness_hours, keyed by external_id - callers skip re-classifying these."""
    if not external_ids:
        return {}
    with _connect() as conn:
        rows = conn.execute(
            """
            select external_id, subreddit, external_type, title, body, url, permalink,
                   score, num_comments, created_at_source, embedding,
                   joy, trust, fear, surprise, sadness, disgust, anger, anticipation,
                   valence, arousal, dominant_emotion, summary, claude_model, author_hash, source
            from emotion_events
            where external_id = any(%s)
              and classified_at > now() - (%s || ' hours')::interval
            """,
            (external_ids, freshness_hours),
        ).fetchall()

    return {row[0]: _row_to_record(row) for row in rows}


def get_recent(subreddits: list[str] | None = None, window_hours: float = 72) -> list[EventRecord]:
    """Recently-posted, already-classified rows for ranking - the read side of the /landscape route."""
    query = """
        select external_id, subreddit, external_type, title, body, url, permalink,
               score, num_comments, created_at_source, embedding,
               joy, trust, fear, surprise, sadness, disgust, anger, anticipation,
               valence, arousal, dominant_emotion, summary, claude_model, author_hash, source
        from emotion_events
        where created_at_source > now() - (%s || ' hours')::interval
    """
    params: list = [window_hours]
    if subreddits:
        query += " and subreddit = any(%s)"
        params.append(subreddits)

    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_row_to_record(row) for row in rows]


def _row_to_record(row) -> EventRecord:
    (
        external_id, subreddit, external_type, title, body, url, permalink,
        score, num_comments, created_at_source, embedding,
        joy, trust, fear, surprise, sadness, disgust, anger, anticipation,
        valence, arousal, dominant_emotion, summary, claude_model, author_hash, source,
    ) = row
    emotion = EmotionClassification(
        joy=joy, trust=trust, fear=fear, surprise=surprise, sadness=sadness,
        disgust=disgust, anger=anger, anticipation=anticipation,
        valence=valence, arousal=arousal, dominant_emotion=dominant_emotion, summary=summary,
    )
    return EventRecord(
        external_id=external_id, subreddit=subreddit, external_type=external_type,
        title=title, body=body, url=url, permalink=permalink,
        score=score, num_comments=num_comments, created_at_source=created_at_source,
        embedding=embedding.to_list(), emotion=emotion, claude_model=claude_model,
        author_hash=author_hash, source=source,
    )


def upsert_events(records: list[EventRecord]) -> None:
    if not records:
        return
    with _connect() as conn:
        for r in records:
            conn.execute(
                """
                insert into emotion_events (
                    source, subreddit, external_id, external_type, author_hash,
                    url, permalink, title, body, score, num_comments, created_at_source,
                    classified_at, joy, trust, fear, surprise, sadness, disgust, anger,
                    anticipation, valence, arousal, dominant_emotion, summary, claude_model, embedding
                ) values (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    now(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                on conflict (source, external_id) do update set
                    score = excluded.score,
                    num_comments = excluded.num_comments,
                    classified_at = excluded.classified_at,
                    joy = excluded.joy, trust = excluded.trust, fear = excluded.fear,
                    surprise = excluded.surprise, sadness = excluded.sadness,
                    disgust = excluded.disgust, anger = excluded.anger,
                    anticipation = excluded.anticipation, valence = excluded.valence,
                    arousal = excluded.arousal, dominant_emotion = excluded.dominant_emotion,
                    summary = excluded.summary, claude_model = excluded.claude_model,
                    embedding = excluded.embedding
                """,
                (
                    r.source, r.subreddit, r.external_id, r.external_type, r.author_hash,
                    r.url, r.permalink, r.title, r.body, r.score, r.num_comments, r.created_at_source,
                    r.emotion.joy, r.emotion.trust, r.emotion.fear, r.emotion.surprise, r.emotion.sadness,
                    r.emotion.disgust, r.emotion.anger, r.emotion.anticipation, r.emotion.valence,
                    r.emotion.arousal, r.emotion.dominant_emotion, r.emotion.summary, r.claude_model,
                    r.embedding,
                ),
            )
