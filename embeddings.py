# embeddings.py
import os
from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")


@lru_cache(maxsize=1)
def get_model():
    """Charge le modèle une seule fois (le chargement est lent)."""
    return SentenceTransformer(MODEL_NAME)


def _prefix(kind: str) -> str:
    # Les modèles E5 exigent ces préfixes ; bge-m3 n'en a pas besoin.
    if "e5" in MODEL_NAME.lower():
        return "query: " if kind == "query" else "passage: "
    return ""


def embed_texts(texts: list[str], kind: str = "passage", batch_size: int = 32) -> np.ndarray:
    """Retourne un tableau float32 (n, dim), vecteurs normalisés (norme 1)."""
    model = get_model()
    if not texts:
        return np.zeros((0, model.get_sentence_embedding_dimension()), dtype="float32")
    p = _prefix(kind)
    vecs = model.encode(
        [p + t for t in texts],
        batch_size=batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=len(texts) > 200,
    )
    return vecs.astype("float32")