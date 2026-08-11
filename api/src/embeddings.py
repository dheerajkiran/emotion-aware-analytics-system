from functools import lru_cache

from sentence_transformers import SentenceTransformer

from . import config


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    return SentenceTransformer(config.EMBEDDING_MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Batch-embed texts as unit-normalized vectors, so cosine similarity is a dot product."""
    if not texts:
        return []
    vectors = _model().encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    return vectors.tolist()


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
