-- Apply once emotion_events has real data — an HNSW index on an empty
-- or near-empty table has nothing to index and just adds write overhead.
create index on emotion_events using hnsw (embedding vector_cosine_ops);
