"""Student 2: Sentence Transformer embeddings. Use same model for docs and queries."""
from functools import lru_cache

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # English-first MVP


@lru_cache(maxsize=1)
def get_embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


def encode_texts(texts: list[str]):
    """Return L2-normalized float32 NumPy array, shape=(n, embedding_dim)."""
    return get_embedding_model().encode(
        texts, convert_to_numpy=True, normalize_embeddings=True
    ).astype("float32")
