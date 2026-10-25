"""Small reproducible smoke test for Student 1 upgraded module."""
import sys
from pathlib import Path
from document_loader import load_document, load_pdf
from chunking import chunk_documents


def validate(records, chunks):
    assert records
    for row in records:
        assert set(row) == {"text", "source", "page"}
        assert isinstance(row["page"], int) and row["page"] >= 1
    for chunk in chunks:
        assert set(chunk) == {"chunk_id", "text", "source", "page"}
        assert chunk["text"]


def main():
    import fitz
    # Local reproducible selectable-text PDF.
    test_doc = fitz.open()
    p = test_doc.new_page()
    p.insert_text((45, 90), "Attention connects tokens through learned weights.", fontsize=16)
    pdf_bytes = test_doc.tobytes()
    png_bytes = p.get_pixmap(dpi=220, alpha=False).tobytes("png")
    test_doc.close()

    pages = load_pdf(pdf_bytes, "example.pdf")
    chunks = chunk_documents(pages)
    validate(pages, chunks)
    assert "Attention connects tokens" in pages[0]["text"]
    print("OK - searchable PDF: pages", len(pages), "/ chunks", len(chunks))

    try:
        image_pages = load_document(png_bytes, "example.png")
        image_chunks = chunk_documents(image_pages)
        validate(image_pages, image_chunks)
        assert image_pages[0]["page"] == 1
        print("OK - PNG OCR:", image_pages[0]["text"][:120])
    except ValueError as exc:
        print("PNG OCR unavailable - Tesseract setup needed:", exc)

    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        print("Testing user file:", path)
        document_pages = load_document(path.read_bytes(), path.name, max_pages=2)
        final_chunks = chunk_documents(document_pages)
        validate(document_pages, final_chunks)
        print("Pages with content:", len(document_pages), "Chunks:", len(final_chunks))
        for row in document_pages:
            print("Page", row["page"], "Text preview:", row["text"][:220].replace("\n", " "))


if __name__ == "__main__":
    main()
