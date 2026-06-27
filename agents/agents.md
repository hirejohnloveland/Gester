# AI Agent Instructions

## Purpose

This repository contains a local-first AI knowledge base focused on
acquiring, storing, retrieving, and summarizing AI-related content.

The system should remain understandable, maintainable, and largely
deterministic. See ADR-0003 for when runtime agents are appropriate
versus conventional application logic.

These instructions are guardrails for **AI coding assistants** (Cursor,
Copilot, etc.). They are separate from **runtime agents** built inside
Gester during Phase 8 of the roadmap.

---

## Before Starting Work

Review authoritative documents before making significant changes:

1. `docs/roadmap_v2.md` — current phase, milestones, and project goals
2. `docs/adr/` — architectural decisions (especially ADR-0001, ADR-0002,
   ADR-0003, ADR-0006, ADR-0009, ADR-0010)
3. `docs/coding-standards.md` — Python conventions and file organization
4. This file — scope limits and project structure

If a task touches architecture, new dependencies, or project layout,
read the relevant ADRs first. If you introduce a significant decision,
create or update an ADR.

When project structure changes, update this file and the affected ADRs
in the same change set (see ADR-0004).

---

## Authoritative Documents

| Document | Role |
|----------|------|
| `docs/roadmap_v2.md` | What to build and in what order |
| `docs/adr/` | Why architectural choices were made |
| `docs/coding-standards.md` | How to write code in this repo |
| `agents/agents.md` | Guardrails for AI coding assistants |

Do not duplicate ADR or coding-standard content here. Reference the
authoritative source instead.

---

## Project Structure

Gester is a local web application with a Python server and a future
React client (see ADR-0005). The server follows Presentation (API) /
Application / Domain / Infrastructure layering (see ADR-0001 and
ADR-0005).

```
Gester/
├── agents/              # AI coding assistant instructions (this file)
├── config/              # Application configuration
├── data/                # Local runtime data (SQLite, Qdrant)
├── docs/
│   ├── adr/             # Architecture Decision Records
│   ├── coding-standards.md
│   └── roadmap_v2.md    # Current roadmap
├── server/src/gester/
│   ├── app.py           # Composition root: creates app, includes routers, startup
│   ├── api/routers/     # FastAPI APIRouter modules (content, ingestion, retrieval)
│   ├── domain/models/   # Business concepts (SourceItem, SourceItemChunk, …)
│   ├── application/     # Use cases and orchestration
│   │   ├── content/     # Read/query services for stored items and chunks
│   │   ├── ingestion/   # RSS ingestion, chunking, embedding
│   │   ├── retrieval/   # Search and RAG answer services
│   │   └── responses/   # API response models
│   └── infrastructure/  # External integrations
│       ├── embeddings/
│       ├── extraction/
│       ├── feeds/
│       ├── llm/
│       └── storage/     # SQLite and Qdrant
├── run.py               # Server startup script
└── requirements.txt
```

### api (presentation)

FastAPI `APIRouter` modules grouped by concern. Route handlers are thin:
they call application services and map to response models. No business
logic or direct infrastructure access. `app.py` is the composition root
that includes the routers and runs startup.

Current routers: `content_router`, `ingestion_router`, `retrieval_router`.

### domain

Business concepts and models. No infrastructure dependencies.

Current examples: `SourceItem`, `SourceItemChunk`, `RssItem`, `TextChunk`.

### application

Use-case orchestration. Coordinates domain models and infrastructure.

Current examples: `RssIngestionService`, `SourceItemChunkingService`,
`ChunkEmbeddingService`, `SearchService`, `AnswerService`,
`SourceItemQueryService`, `SourceItemChunkQueryService`.

### infrastructure

Implementation details and external integrations.

Current examples: `RssReader`, `ArticleExtractor`, `EmbeddingService`,
`QdrantVectorStore`, `OllamaClient`, SQLite repositories and mappers.

### config

Configuration files for models, sources, and runtime settings.

### data

Locally stored runtime data. Not committed to source control.

### docs

Project documentation, ADRs, coding standards, and roadmap.

### agents

Instructions and guardrails for AI coding assistants.

---

## Terminology

| Term | Meaning |
|------|---------|
| **Coding assistant** | AI tool helping write code (governed by this file) |
| **Deterministic pipeline** | Fixed step-by-step workflow in application code |
| **Runtime agent** | Autonomous in-app system that decides its own steps (Phase 8) |

Using an LLM inside a pipeline (e.g. RAG answer generation) is not a
runtime agent. The code defines the steps; the model executes one of
them. See ADR-0003.

---

## Decision Making

When proposing changes:

1. Prefer the simplest solution that satisfies the requirement.
2. Prefer deterministic pipelines over runtime agents (ADR-0003).
3. Prefer local solutions over cloud solutions (ADR-0002).
4. Prefer explicit code over framework magic.
5. Prefer small focused files over large multi-purpose files.
6. Stay within the current roadmap phase unless the user directs otherwise.

If a significant architectural decision is required, create or update an
ADR before implementing.

---

## Expectations for AI Assistants

Do not:

- Introduce new frameworks without discussion.
- Introduce cloud dependencies without discussion.
- Introduce new architectural layers without discussion.
- Perform broad refactors when a targeted change is sufficient.
- Create catch-all modules or dumping grounds for unrelated code.
- Expand the scope of a requested change without discussion.
- Make unrelated or unnecessary changes.
- Assume project structure from memory — verify against this file and ADR-0001.

Do:

- Read the roadmap and relevant ADRs before significant work.
- If a larger change appears necessary, explain the rationale and obtain agreement before proceeding.
- Suggest improvements, missing considerations, architectural concerns, or extensibility issues when relevant.
- Update documentation when project structure or architecture changes.
- Clearly distinguish between:
  - The requested change.
  - Recommended enhancements.
  - Optional future improvements.

---

## Scope of Changes

Implement the requested change and only the requested change.

If additional changes are recommended:

- Explain the recommendation.
- Explain the benefit.
- Ask before proceeding.

---

## Documentation Maintenance

When you change project structure, add a new subsystem, or make an
architectural decision:

1. Update `agents/agents.md` if the directory layout or conventions change.
2. Create or update the relevant ADR in `docs/adr/`.
3. Update `docs/coding-standards.md` if new conventions are established.
4. Update `docs/roadmap_v2.md` only when milestones are completed or scope changes.

See ADR-0004 for the full documentation and guardrail policy.
