# Emotion-Aware Analytics System

An on-demand pipeline that fetches live Reddit discussion, classifies it against a structured 8-emotion taxonomy using Claude, clusters near-duplicate posts into distinct storylines, and ranks them by a blend of engagement and emotional intensity — so you can see what's actually driving reaction online right now without reading a subreddit yourself.

> Status: in active development. See [ARCHITECTURE.md](ARCHITECTURE.md) for the full system design.

## What it does

- **Fetches** current hot/rising posts from configured subreddits, on demand — triggered by opening the dashboard or hitting refresh, not a background poller.
- **Classifies** each post against Plutchik's eight primary emotions (joy, trust, fear, surprise, sadness, disgust, anger, anticipation) plus overall valence/arousal, and writes a short neutral summary of what it's about — both from a single validated, structured Claude call.
- **Clusters** near-duplicate posts about the same story into one entry, via embedding similarity — so the feed shows distinct storylines, not fifteen copies of the same event.
- **Ranks** storylines by a blend of engagement velocity and emotional intensity — surfacing what's both spreading fast *and* provoking strong reaction, not just what Reddit's own sort already shows.
- **Caches** every classification so re-opening the app doesn't re-pay for posts already seen, and opportunistically builds a history over real usage.

## Why this is useful

Reddit's own "hot" sort already tells you what's popular. This adds the signal that sort doesn't: is this provoking real reaction, or just mild interest? Opening the dashboard replaces manually scanning several subreddits and mentally merging the ten posts that are all about the same event — instead, one ranked, deduplicated list, in about as long as it takes to read a few headlines.

Worth being precise about what it isn't: it's not a verified news source (an emotion score describes the intensity of Reddit's reaction, not the real-world importance or accuracy of the underlying event), and it's Reddit-only, so it reflects Reddit's communities, not "public sentiment" broadly. It's a triage tool — it tells you what's worth a closer look, not a substitute for reading the thread once something ranks high.

## Architecture at a glance

```
Next.js (Vercel) --GET /landscape--> FastAPI (Cloud Run, scale-to-zero)
    fetch Reddit → classify (Claude) → embed → cluster into storylines → rank → return
                                    ↕
                        Neon Postgres + pgvector (cache/history)
```

Nothing runs continuously — the whole pipeline executes inside a single request. Full rationale for each choice, including the cost research behind it, is in [ARCHITECTURE.md](ARCHITECTURE.md).

## Stack

FastAPI · Pydantic AI · Claude API (Anthropic) · sentence-transformers · scikit-learn (HDBSCAN) · Neon (Postgres + pgvector) · Next.js / TypeScript · Google Cloud Run · Vercel

## Cost

Every piece of infrastructure runs on a genuine free tier (Cloud Run, Neon, Vercel) and nothing runs when the app isn't in use. The only real recurring cost is the Claude API itself, bounded by a Haiku-default model, an engagement filter before classification, and a spend cap set in the Anthropic Console.

## Getting started

Local dev instructions land here once `api/` and `web/` are built out.

## License

MIT — see [LICENSE](LICENSE).
