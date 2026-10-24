# SHARED CONTRACTS — Read before coding

**Do not rename the fields below.** Use `dict` / `list[dict]` values for simplest Python integration. All page numbers are **1-based integers**. Empty input may return `[]`.

### Student 1: `document_loader.py` and `chunking.py`

`load_pdf(file_bytes: bytes, filename: str) -> list[dict]`

One PDF page dictionary: `{"text": "...", "source": "course.pdf", "page": 12}`.

`chunk_documents(documents: list[dict]) -> list[dict]`

One chunk dictionary:

```json
{"chunk_id":"c0001","text":"Self-attention ...","source":"course.pdf","page":12}
```

Every chunk retains the page on which its text originated; chunks never cross page boundaries in the starter.

### Student 2: `embeddings.py` and `retriever.py`

`build_index(chunks: list[dict]) -> index` (FAISS index object)

`retrieve(question: str, index, chunks: list[dict], k: int=3) -> list[dict]`

Each result MUST copy `chunk_id`, `text`, `source`, and `page`, plus add a float `score`:

```json
{"chunk_id":"c0001","text":"Self-attention ...","source":"course.pdf","page":12,"score":0.94}
```

Score is an example, not a measured output. The starter uses normalized embeddings and cosine-equivalent inner products.

### Student 3: `rag_generator.py` / `prompts.py`

`generate_answer(question: str, retrieved_chunks: list[dict]) -> dict`

```json
{
  "answer": "Self-attention allows ... [c0001]",
  "sources": [{"chunk_id":"c0001","source":"course.pdf","page":12}]
}
```

`source` and `page` MUST come from the retrieved chunk metadata, not invented by the LLM. Only cite chunk IDs included in `retrieved_chunks`. If no context is available, return an abstention answer with `sources: []`. Checking IDs is not the same as verifying every factual claim.

### Student 4: `app.py` and `pipeline.py`

`prepare_document(file_bytes: bytes, filename: str) -> (index, chunks)`

`answer_question(question: str, index, chunks: list[dict]) -> dict`

Streamlit displays `result["answer"]` and loops over `result["sources"]`.

### Mock development

Use `mock_data.py` for fake inputs and outputs **only while building**. Real demo requires the actual PDF→retrieval→LLM path. Do not present mocked answers as AI output.
