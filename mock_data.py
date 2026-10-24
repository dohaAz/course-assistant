"""Shared fake examples for parallel development; NOT real retrieval/LLM results."""
MOCK_CHUNKS = [
    {"chunk_id":"c0001", "text":"Self-attention lets tokens incorporate context from other tokens.", "source":"sample_course.pdf", "page":12},
    {"chunk_id":"c0002", "text":"Positional encoding provides information about token order.", "source":"sample_course.pdf", "page":15},
]
MOCK_RETRIEVED = [{**MOCK_CHUNKS[0], "score":0.94}]
MOCK_ANSWER = {
    "answer":"Self-attention combines information from other tokens [c0001].",
    "sources":[{"chunk_id":"c0001", "source":"sample_course.pdf", "page":12}],
}
