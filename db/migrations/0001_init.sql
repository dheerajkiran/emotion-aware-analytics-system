create extension if not exists vector;
create extension if not exists pgcrypto;

create table emotion_events (
  id uuid primary key default gen_random_uuid(),
  source text not null default 'reddit',
  subreddit text not null,
  external_id text not null,
  external_type text not null check (external_type in ('post', 'comment')),
  author_hash text,
  url text,
  permalink text,
  title text,
  body text not null,
  score int,
  num_comments int,
  created_at_source timestamptz not null,
  classified_at timestamptz not null default now(),

  -- Plutchik's eight primary emotions, independently scored 0..1
  joy real,
  trust real,
  fear real,
  surprise real,
  sadness real,
  disgust real,
  anger real,
  anticipation real,

  valence real,
  arousal real,
  dominant_emotion text,
  summary text,
  claude_model text,

  embedding vector(384),

  unique (source, external_id)
);

create index on emotion_events (subreddit, created_at_source desc);
create index on emotion_events (external_id);
