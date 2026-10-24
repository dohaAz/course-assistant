"""Student 3: LLM generation, with cited IDs validated against retrieved chunks."""
from __future__ import annotations
import os
import re
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT, format_context


def generate_answer(question: str, retrieved_chunks: list[dict]) -> dict:
    """Return {'answer': str, 'sources': [{'chunk_id','source','page'}]}.

    NOTE: IDs are validated, but semantic citation fidelity still needs testing.
    """
    if not retrieved_chunks:
        return {"answer": "I cannot find enough information in the uploaded course material.", "sources": []}
    load_dotenv()
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    if not api_key and not base_url:
        raise RuntimeError("Configure LLM_API_KEY and LLM_MODEL in .env (or an OpenAI-compatible local LLM_BASE_URL).")

    from openai import OpenAI
    client = OpenAI(api_key=api_key or "local", base_url=base_url or None)
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Question:\n{question}\n\nSource passages:\n{format_context(retrieved_chunks)}"},
        ],
    )
    answer = (response.choices[0].message.content or "").strip()
    allowed = {ch["chunk_id"]: ch for ch in retrieved_chunks}
    mentioned = list(dict.fromkeys(re.findall(r"\[([A-Za-z0-9_-]+)\]", answer)))
    invalid = [chunk_id for chunk_id in mentioned if chunk_id not in allowed]
    if invalid:
        # Strip invalid citation tokens; never present a citation to an absent source.
        for bad in invalid:
            answer = answer.replace(f"[{bad}]", "")
    sources = [
        {"chunk_id": cid, "source": allowed[cid]["source"], "page": allowed[cid]["page"]}
        for cid in mentioned if cid in allowed
    ]
    return {"answer": answer or "I cannot find enough information in the uploaded course material.", "sources": sources}
