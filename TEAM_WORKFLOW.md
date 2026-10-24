# GitHub — steps for an EXISTING repository

The repository already exists on GitHub and contains `README.md` and `.gitignore`. **Do not run `git init` or add a new remote inside the existing clone.**

## Team lead: clone repository and copy starter files

1. Copy the HTTPS URL from GitHub > green **Code** button.
2. In VS Code terminal, run:

```bash
git clone YOUR_REPOSITORY_URL
cd course-assistant
```

Replace `course-assistant` with the name of your actual repository folder if necessary.

3. Extract the provided ZIP. Copy the **contents** of its `University-Course-Assistant/` directory into your cloned repository directory (not the enclosing directory itself). Overwrite `README.md` and `.gitignore` if prompted.
4. From the cloned repository terminal:

```bash
git add .
git commit -m "Add RAG starter modules and contracts"
git push origin main
git switch -c develop
git push -u origin develop
```

5. GitHub > repository **Settings** > **Collaborators** > invite the other 3 students.

## Each teammate: clone and create assigned branch

```bash
git clone YOUR_REPOSITORY_URL
cd course-assistant
git fetch origin
git switch -c feature/documents origin/develop
```

Use the branch assigned to your own role instead:

- Student 1: `feature/documents` (`document_loader.py`, `chunking.py`)
- Student 2: `feature/retrieval` (`embeddings.py`, `retriever.py`)
- Student 3: `feature/generation` (`prompts.py`, `rag_generator.py`)
- Student 4: `feature/ui` (`app.py`, `pipeline.py`)

## Save work

```bash
git add .
git commit -m "Implement assigned module"
git push -u origin HEAD
```

On GitHub, make a Pull Request from your feature branch **into `develop`**, not into `main`. Review and merge. Keep `CONTRACTS.md` keys/function signatures unchanged unless everyone agrees. Never commit `.env` secrets.

## Local environment (one time)

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
python smoke_test.py
```

Copy `.env.example` to `.env` and set a valid LLM key or local OpenAI-compatible endpoint, then run `streamlit run app.py`.

**Limit:** scanned/image-only course slides need OCR and may not work with this starter's PyMuPDF extraction.
