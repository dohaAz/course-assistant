"""Student 1 - Split page records into citation-ready chunks."""
from __future__ import annotations

import re


def chunk_documents(
    documents: list[dict],
    chunk_size: int = 900,
    overlap: int = 150,
) -> list[dict]:
    """Return chunks with the exact keys: chunk_id, text, source, page.

    chunk_size / overlap are character counts (not token counts).
    All chunks stay within their original PDF page for truthful citations.
    """
    if chunk_size <= 0 or not 0 <= overlap < chunk_size:
        raise ValueError('Require chunk_size > 0 and 0 <= overlap < chunk_size')

    results = []
    step = chunk_size - overlap
    for page in documents:
        # Contract validation makes bugs obvious during parallel integration.
        for field in ('text', 'source', 'page'):
            if field not in page:
                raise ValueError(f'Missing page field: {field}')
        text = re.sub(r'\s+', ' ', page['text']).strip()
        if not text:
            continue
        for start in range(0, len(text), step):
            # Character chunking keeps the MVP independent of tokenizers.
            part = text[start : start + chunk_size].strip()
            if part:
                results.append({
                    'chunk_id': f'c{len(results) + 1:04d}',
                    'text': part,
                    'source': page['source'],
                    'page': page['page'],
                })
            if start + chunk_size >= len(text):
                break
    return results
