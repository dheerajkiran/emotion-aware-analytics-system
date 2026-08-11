import math

from api.src.embeddings import embed_text, embed_texts


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def test_embed_text_shape_and_normalization():
    vec = embed_text("The stock market dropped sharply this morning.")
    assert len(vec) == 384
    norm = math.sqrt(sum(x * x for x in vec))
    assert math.isclose(norm, 1.0, abs_tol=1e-4)


def test_embed_texts_batch_matches_count():
    texts = ["first post", "second post", "third post"]
    vectors = embed_texts(texts)
    assert len(vectors) == len(texts)
    assert all(len(v) == 384 for v in vectors)


def test_embed_texts_empty_list():
    assert embed_texts([]) == []


def test_similar_texts_are_closer_than_unrelated_ones():
    a, b, c = embed_texts([
        "The central bank raised interest rates by half a point today.",
        "Federal Reserve announces a surprise 0.5% rate hike.",
        "My cat knocked a plant off the balcony this morning.",
    ])
    similar_score = _dot(a, b)
    unrelated_score = _dot(a, c)
    assert similar_score > unrelated_score, (
        f"expected the two rate-hike posts to be closer than the cat post "
        f"(similar={similar_score:.3f}, unrelated={unrelated_score:.3f})"
    )
