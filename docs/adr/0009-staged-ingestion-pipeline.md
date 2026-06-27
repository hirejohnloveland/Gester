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

Chunking and embedding read from SQLite and do not re-fetch external
source content.

### Acquisition chunks inline as a convenience

For the full-ingest path, `RssIngestionService` also chunks each article
inline immediately after persisting it, so a single ingest call produces
chunk-ready content without a second request.

This is a deliberate convenience, not a violation of stage separation:
the chunking logic is shared (`TextChunkingService`), and
`SourceItemChunkingService` remains the authority for chunking existing
content independently of acquisition.

### Standalone chunking stage

`SourceItemChunkingService` exists so that stored content can be
(re)chunked **without re-fetching source articles**. Its primary value
during retrieval development is iterating on chunk settings against
already-acquired raw content.

- `chunk_missing_source_items()` chunks any source item that has no chunks
- `reset_chunks()` burns down all chunks and clears the derived vector
  collection, then chunking can be re-run to regenerate chunks

### Idempotent processing

Stages skip work already completed:

- Acquisition skips items with duplicate URLs
- Standalone chunking skips source items that already have chunks
- Embedding skips chunks already marked embedded (unless explicitly
  rebuilding)

This allows stages to be re-run safely after partial failures or code
changes.

### Resetting chunks invalidates embeddings

Vector points in Qdrant are keyed by chunk ID (ADR-0006). Deleting chunks
without clearing their vectors would leave orphaned points. Therefore
`reset_chunks()` deletes chunk rows in SQLite **and** clears the Qdrant
collection in the same operation.

The rechunk-and-re-embed loop during retrieval development is:

```
reset chunks (clears chunks + vectors) → rechunk → re-embed
```

Source items are never touched by this loop, so articles are not
re-downloaded.

### Independent invocation

Chunking, reset, and embedding may be invoked independently. They do not
implicitly run one another.

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

- Runtime agents coordinating ingestion (ADR-0003)
- Defining the permanent scheduling or trigger mechanism
- Deleting source items as part of resetting chunks

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
