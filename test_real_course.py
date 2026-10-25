
from pathlib import Path
from document_loader import load_pdf
from chunking import chunk_documents
import json

pdf_path = Path("data/Gen-AI3.pdf")

# Extract first 10 pages
pages = load_pdf(
    pdf_path.read_bytes(),
    pdf_path.name,
    max_pages=10
)

chunks = chunk_documents(pages)

print("Pages extracted:", len(pages))
print("Chunks created:", len(chunks))

for chunk in chunks[:10]:
    print("\n---------------------")
    print("Chunk ID:", chunk["chunk_id"])
    print("Source:", chunk["source"])
    print("Page:", chunk["page"])
    print("Text:", chunk["text"][:500])

# Save chunks to JSON
with open("data/chunks_test.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print("\nSaved to data/chunks_test.json")
