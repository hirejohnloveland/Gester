# ADR-0009: Staged Ingestion Pipeline

## Status

Accepted

## Context

Content moves through several transformations between acquisition and
semantic search: raw source items, text chunks, and vector embeddings.
Each step has different failure modes, cost, and re-run requirements.

ADR-0003 requires deterministic pipelines. The ingestion path must be
understandable, idempotent, and debuggable stage by stage.

## Decision

Ingestion is a **multi-stage pipeline** where each stage is a separate
application service with a single responsibility.

### Stages

1. **Acquisition** — retrieve source content and persist source items
   (`RssIngestionService`, future email and other source types)
2. **Chunking** — split source item text into chunks linked to the parent
   item (`SourceItemChunkingService`)
3. **Embedding** — generate vectors for chunks and index them in Qdrant
   (`ChunkEmbeddingService`)

Each stage reads from SQLite and writes its own outputs. Chunking and
embedding do not re-fetch external source content.

### Idempotent processing

Stages skip work already completed:

- Acquisition skips items with duplicate URLs
- Chunking skips source items that already have chunks
- Embedding skips chunks already marked embedded (unless explicitly
  rebuilding)

This allows stages to be re-run safely after partial failures or code
changes.

### Independent invocation

Stages may be invoked independently. A later stage does not implicitly
run earlier stages.

Orchestration (when to run each stage) is separate from stage logic.

## Consequences

### Benefits

- Each stage can be tested, debugged, and rerun in isolation
- Failures are localized to a single transformation
- Re-embedding does not require re-fetching source articles
- Aligns with ADR-0003 deterministic pipeline philosophy

### Tradeoffs

- Something must coordinate stage execution (not defined here)
- Running only later stages on empty earlier data produces no useful
  output
- More explicit operator awareness than a single "ingest everything"
  button

## Non-Goals

- A monolithic ingest function that hides all stages
- Runtime agents coordinating ingestion (ADR-0003)
- Defining the permanent scheduling or trigger mechanism

## Deferred (see roadmap)

The following are **not** decided by this ADR:

- Scheduled or overnight automatic orchestration (Phase 1 completion
  criteria, Phase 5.4)
- Configuration-driven source lists and enable/disable flags (Phase 1.3)
- HTTP routes, CLI commands, or background jobs as the permanent trigger
  mechanism — these are current development adapters, not architecture
- Email and non-RSS source acquisition (Phase 1.4)

When orchestration is implemented, it should call the same application
services defined here rather than duplicating stage logic.
