# UniCourse AI — University Course Assistant

**ENSIAS | Generative AI | Python RAG**

A small Retrieval-Augmented Generation application: upload a text-based university PDF, ask a question, and receive an LLM-generated answer with page citations.

## Team ownership

| Student | Owns | Inputs → Outputs |
|---|---|---|
| 1 | `document_loader.py`, `chunking.py` | PDF bytes → page records → chunk dictionaries |
| 2 | `embeddings.py`, `retriever.py` | chunks → FAISS index; question + index → relevant chunks |
| 3 | `prompts.py`, `rag_generator.py` | question + retrieved chunks → answer + sources |
| 4 | `app.py`, `pipeline.py`, integration | uploaded PDF + question → chat UI + citations |

**IMPORTANT:** `CONTRACTS.md` is the source of truth. Do not change function signatures or dictionary keys without agreement from the team.

## Setup

Requirements: Python 3.11+ and internet on first run to download the embedding model.

```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and configure an **OpenAI-compatible** model API:

```text
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-4o-mini
# LLM_BASE_URL=       # Optional: provider's OpenAI-compatible endpoint
```

For local Ollama with its OpenAI-compatible API (if already installed):

```text
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=your-installed-model-name
```

Never commit your actual `.env` or API keys.

Launch:

```bash
streamlit run app.py
```

Steps in app: upload a **text-selectable PDF**, click **Process PDF**, type a question, and inspect sources.

> Many course slides are image-based. Ordinary PyMuPDF extraction cannot read text inside images. OCR is **not** implemented in this starter; use a searchable PDF for the first demo. Missing text should be reported, never silently invented.

## Fast tests

```bash
python smoke_test.py      # no external packages required
python -m unittest discover -s tests
python -m compileall -q .
```

The smoke test exercises the **contracts with mock data**. It is not a real RAG benchmark. Live FAISS/LLM operation requires dependencies and an API or local model.

## Live architecture

`PDF → page extraction → chunking → SentenceTransformer embeddings → FAISS → Top-K → LLM prompt → answer + checked citation IDs → Streamlit`

## Parallel Git workflow

1. The team lead **clones the existing GitHub repository**, copies these starter files into it, pushes to `main`, then creates `develop`.
2. Each member branches from `develop` using `feature/documents`, `feature/retrieval`, `feature/generation`, or `feature/ui`.
3. Work on your own assigned files; use `mock_data.py` for missing upstream outputs.
4. Open PRs into `develop`; run smoke tests and integration tests before merge.
5. After the full flow works, merge `develop` into `main` and prepare the required ZIP.

See `TEAM_WORKFLOW.md` for step-by-step commands.

## Submission checklist

- Source `.py` files and executed `.ipynb` notebooks
- `requirements.txt`, sample/test data information, README with execution steps
- Presentation PDF/PPTX (10 minutes; separate file or included)
- ZIP named exactly as specified by the teacher: `GenAI_Groupe[N]_Nom1_Nom2.zip`
- No credentials, virtual environments, model caches, or private/course-restricted PDFs inside ZIP

## Limitations

Basic extractive PDF parsing; no OCR for image slides; results depend on retrieval and API/model quality; cited chunk IDs exist in retrieved contexts but their substantive factual support still requires review.
