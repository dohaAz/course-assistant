"""Student 4: glue modules together without changing shared contracts."""
import os
import re
from dotenv import load_dotenv
from document_loader import load_pdf
from chunking import chunk_documents
from retriever import build_index, retrieve
from rag_generator import generate_answer

DEFAULT_K = 3
NO_ANSWER = "I cannot find enough information in the uploaded course material."
_THINK = re.compile(r"<think>.*?(</think>|$)", re.DOTALL | re.IGNORECASE)  # Qwen3 reasoning


def prepare_document(file_bytes: bytes, filename: str):
    if not file_bytes:
        raise ValueError("The uploaded file is empty.")
    documents = load_pdf(file_bytes, filename)
    chunks = chunk_documents(documents)
    if not chunks:
        raise ValueError("No extractable PDF text. Try a text-selectable PDF; OCR is not included.")
    index = build_index(chunks)
    if index is None:
        raise ValueError("Could not build the search index for this document.")
    return index, chunks


def answer_question(question: str, index, chunks: list[dict], k: int = DEFAULT_K) -> dict:
    """Return {'answer', 'sources'} per CONTRACTS.md, plus 'passages' (retrieved chunks) for display."""
    passages = retrieve(question, index, chunks, k=k)
    result = generate_answer(question, passages)
    answer = _THINK.sub("", result["answer"] or "").strip() or NO_ANSWER
    # Keep only sources still cited after removing <think> text.
    cited = set(re.findall(r"\[([A-Za-z0-9_-]+)\]", answer))
    sources = [s for s in result["sources"] if s["chunk_id"] in cited]
    return {"answer": answer, "sources": sources, "passages": passages}


def llm_settings() -> dict:
    """LLM config from .env, shown in the sidebar."""
    load_dotenv()
    return {"model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
            "base_url": os.getenv("LLM_BASE_URL") or "OpenAI API"}
