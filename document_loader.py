"""Student 1: load PDFs into page records with source metadata."""
from __future__ import annotations


def load_pdf(file_bytes: bytes, filename: str) -> list[dict]:
    """Extract text from each PDF page (1-based page numbers).

    Input: file bytes + original name.
    Output: [{'text': str, 'source': str, 'page': int}, ...]
    NOTE: image-only pages need OCR, which is outside the MVP.
    """
    if not file_bytes:
        return []
    import fitz  # PyMuPDF; import here so contract smoke tests need no installation
    records = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page_idx, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if text:
                records.append({"text": text, "source": filename, "page": page_idx})
    return records
