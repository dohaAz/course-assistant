"""Lightweight integration CONTRACT check using mock data (not a live RAG test)."""
from mock_data import MOCK_CHUNKS, MOCK_RETRIEVED, MOCK_ANSWER
from chunking import chunk_documents

chunk = chunk_documents([{"text":"Hello world from a PDF page", "source":"test.pdf", "page":2}])[0]
assert set(chunk) == {"chunk_id", "text", "source", "page"}
assert chunk["page"] == 2
assert all(set(ch) == {"chunk_id", "text", "source", "page"} for ch in MOCK_CHUNKS)
assert all(set(ch) == {"chunk_id", "text", "source", "page", "score"} for ch in MOCK_RETRIEVED)
assert set(MOCK_ANSWER) == {"answer", "sources"}
print("PASS: shared contracts work with mock data (not a live LLM test).")
