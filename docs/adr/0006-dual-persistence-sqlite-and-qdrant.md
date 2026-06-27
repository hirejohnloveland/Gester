# ADR-0006: Dual Persistence (SQLite and Qdrant)

## Status

Accepted

## Context

Gester stores source documents, chunk text, and metadata alongside vector
embeddings for semantic search. These concerns have different access
patterns and tooling requirements.

Relational data benefits from structured queries, transactions, and
deduplication. Vector similarity search benefits from a dedicated index.

ADR-0002 commits to local-first storage but does not define how
responsibilities are split across stores.

## Decision

Gester uses two local persistence layers with distinct roles.

### SQLite (canonical content store)

SQLite is the source of truth for:

- Source items (title, URL, raw content, metadata)
- Chunk text and chunk metadata (offsets, index, embedding status)
- Deduplication and relational queries

Location: `data/gester.db`

Access: SQLAlchemy repositories in `infrastructure/storage/sqlite/`.

### Qdrant (vector index)

Qdrant stores vectors and minimal lookup payload only:

- Point ID equals the SQLite chunk ID
- Payload includes `chunk_id` and `source_item_id`
- No chunk text or article metadata in Qdrant

Location: embedded local mode at `data/qdrant/` (no separate server
required for development).

Access: `QdrantVectorStore` in `infrastructure/storage/vector/`.

### Join at query time

Search queries Qdrant for similar vectors, then hydrates full results
from SQLite (chunk text, title, URL). Vector hits alone are not
returned to callers.

### Identity alignment

Chunk IDs are assigned by SQLite and reused as Qdrant point IDs. This
keeps the two stores linked without duplicating content in the vector
index.

## Consequences

### Benefits

- Clear separation: relational data vs similarity search
- Chunk text remains in one canonical place
- Vector index can be rebuilt from SQLite without losing source content
- Both stores run locally (ADR-0002)

### Tradeoffs

- Two systems to maintain and keep in sync
- Rebuild operations must clear and repopulate Qdrant when re-embedding
- Search requires a round trip to SQLite after vector lookup

## Non-Goals

- Storing full document text in Qdrant
- Using Qdrant as the primary content database
- Cloud-hosted vector storage

## Deferred (see roadmap)

- Hybrid keyword + vector retrieval (Phase 4)
- Metadata filtering strategy beyond current payload fields (Phase 2.4 /
  Phase 4)
