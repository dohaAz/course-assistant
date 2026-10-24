"""Student 4: glue modules together without changing shared contracts."""
from document_loader import load_pdf
from chunking import chunk_documents
from retriever import build_index, retrieve
from rag_generator import generate_answer


def prepare_document(file_bytes: bytes, filename: str):
    documents = load_pdf(file_bytes, filename)
    chunks = chunk_documents(documents)
    if not chunks:
        raise ValueError("No extractable PDF text. Try a text-selectable PDF; OCR is not included.")
    index = build_index(chunks)
    return index, chunks


def answer_question(question: str, index, chunks: list[dict]) -> dict:
    passages = retrieve(question, index, chunks, k=3)
    return generate_answer(question, passages)
