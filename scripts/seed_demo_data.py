"""Classify and embed the demo fixture set, writing results straight to Neon.

Bypasses Reddit and the /landscape route entirely - this exists so the
dashboard has real, ranked data to render before live fetching is wired up.
Safe to re-run: upsert_events() is idempotent per external_id.

Usage: python scripts/seed_demo_data.py
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.src import config, db  # noqa: E402
from api.src.classify import classify_text  # noqa: E402
from api.src.embeddings import embed_texts  # noqa: E402

FIXTURES_PATH = Path(__file__).parent / "fixtures" / "demo_seed_texts.json"
CONCURRENCY = 8


async def _classify_one(semaphore: asyncio.Semaphore, entry: dict):
    text = f"{entry['title']}\n\n{entry['body']}"
    async with semaphore:
        try:
            emotion = await classify_text(text)
            return entry, emotion, None
        except Exception as exc:  # noqa: BLE001 - report and continue seeding the rest
            return entry, None, exc


async def main() -> None:
    entries = json.loads(FIXTURES_PATH.read_text())
    print(f"Loaded {len(entries)} fixture posts from {FIXTURES_PATH.name}")

    print("Applying migrations...")
    applied = db.run_migrations()
    print(f"  {len(applied) or 'no new'} migration(s) applied")

    print(f"Classifying {len(entries)} posts (concurrency={CONCURRENCY})...")
    semaphore = asyncio.Semaphore(CONCURRENCY)
    results = await asyncio.gather(*(_classify_one(semaphore, e) for e in entries))

    ok = [(entry, emotion) for entry, emotion, err in results if err is None]
    failed = [(entry, err) for entry, _, err in results if err is not None]
    for entry, err in failed:
        print(f"  FAILED {entry['external_id']}: {err}")
    print(f"  {len(ok)} classified, {len(failed)} failed")

    if not ok:
        print("Nothing to embed or write - exiting.")
        return

    print("Embedding...")
    texts = [f"{entry['title']}\n\n{entry['body']}" for entry, _ in ok]
    vectors = embed_texts(texts)

    now = datetime.now(timezone.utc)
    records = []
    for (entry, emotion), vector in zip(ok, vectors):
        created_at = now - timedelta(hours=entry["hours_ago"])
        records.append(
            db.EventRecord(
                external_id=entry["external_id"],
                subreddit=entry["subreddit"],
                external_type="post",
                title=entry["title"],
                body=entry["body"],
                url=entry["url"],
                permalink=None,
                score=entry["score"],
                num_comments=entry["num_comments"],
                created_at_source=created_at,
                embedding=vector,
                emotion=emotion,
                claude_model=config.CLAUDE_MODEL,
            )
        )

    print(f"Writing {len(records)} records to Neon...")
    db.upsert_events(records)
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
