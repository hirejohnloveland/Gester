# Gester

Local-first AI knowledge base for acquiring, storing, retrieving, and summarizing technical AI content.

Built as a production-style RAG learning project: ingest curated feeds, chunk and embed into a local vector store, then search and summarize with local models.

## Stack

- Python / FastAPI server
- SQLite + Qdrant for storage and retrieval
- Sentence Transformers embeddings
- ADRs and roadmap under `docs/`

## Quick start

```bash
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python run.py
```

See `docs/roadmap_v2.md` and `agents/agents.md` for project goals, structure, and contribution guardrails.