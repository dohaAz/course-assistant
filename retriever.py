# retriever.py
import faiss
from embeddings import embed_texts


def build_index(chunks: list[dict]):
    """Construit l'index FAISS. L'ordre de `chunks` définit les identifiants internes."""
    if not chunks:
        return None
    vecs = embed_texts([c["text"] for c in chunks], kind="passage")
    index = faiss.IndexFlatIP(vecs.shape[1])   # recherche exacte, produit scalaire
    index.add(vecs)
    return index


def retrieve(question: str, index, chunks: list[dict], k: int = 3) -> list[dict]:
    """Top-k chunks les plus proches de la question, avec score."""
    if index is None or not chunks or not question or not question.strip():
        return []
    k = min(k, index.ntotal, len(chunks))
    if k <= 0:
        return []

    q = embed_texts([question.strip()], kind="query")
    scores, ids = index.search(q, k)

    results = []
    for score, i in zip(scores[0], ids[0]):
        if i < 0:                       # FAISS renvoie -1 s'il manque des résultats
            continue
        c = chunks[int(i)]
        results.append({
            "chunk_id": c["chunk_id"],
            "text": c["text"],
            "source": c["source"],
            "page": c["page"],
            "score": float(score),      # float Python, pas numpy.float32 (sérialisation JSON)
        })
    return results