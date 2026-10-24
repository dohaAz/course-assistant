"""Student 1: chunk per-page text; no chunk spans PDF page boundaries."""
from __future__ import annotations
import re


def chunk_documents(documents: list[dict], chunk_size: int = 900, overlap: int = 150) -> list[dict]:
    """Split pages by character window while preserving `source` and `page`.

    Character chunking is an MVP simplification; try token-aware chunking later.
    """
    if chunk_size <= 0 or not (0 <= overlap < chunk_size):
        raise ValueError("Need chunk_size > 0 and 0 <= overlap < chunk_size")
    chunks = []
    step = chunk_size - overlap
    for page in documents:
        clean = re.sub(r"\s+", " ", page["text"]).strip()
        for start in range(0, len(clean), step):
            text = clean[start : start + chunk_size].strip()
            if text:
                chunks.append({
                    "chunk_id": f"c{len(chunks)+1:04d}",
                    "text": text,
                    "source": page["source"],
                    "page": page["page"],
                })
            if start + chunk_size >= len(clean):
                break
    return chunks
