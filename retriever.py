"""Student 2: index chunks with FAISS and retrieve Top-K relevant passages."""
from __future__ import annotations
from embeddings import encode_texts


def build_index(chunks: list[dict]):
    """Return a FAISS cosine-equivalent inner product index.

    Chunk order must be kept identical to FAISS insertion order.
    """
    if not chunks:
        raise ValueError("No chunks to index")
    import faiss
    vectors = encode_texts([item["text"] for item in chunks])
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return index


def retrieve(question: str, index, chunks: list[dict], k: int = 3) -> list[dict]:
    """Return [{'chunk_id','text','source','page','score'}, ...]."""
    if not question.strip() or not chunks:
        return []
    import numpy as np
    vec = encode_texts([question])
    scores, positions = index.search(vec, min(max(k, 1), len(chunks)))
    results = []
    for score, position in zip(scores[0], positions[0]):
        if position < 0:
            continue
        result = dict(chunks[int(position)])
        result["score"] = float(score)
        results.append(result)
    return results
