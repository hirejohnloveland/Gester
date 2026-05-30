# ADR-0001: Project Structure

## Status

Accepted

## Context

The project requires a maintainable structure that supports long-term growth while avoiding large files, mixed responsibilities, and catch-all modules.

## Decision

The codebase will be organized into:

- domain
- application
- infrastructure

### Domain

Contains business concepts and models.

Examples:

- FeedSource
- FeedItem
- ArticleDocument
- ArticleChunk

### Application

Contains use cases and orchestration logic.

Examples:

- IngestionPipeline
- RetrievalPipeline

### Infrastructure

Contains implementation details.

Examples:

- RSS readers
- HTML extraction
- File storage
- SQLite repositories
- Qdrant integration
- Embedding providers

## Consequences

### Benefits

- Clear separation of concerns
- Small focused files
- Easier testing
- Easier replacement of infrastructure components

### Tradeoffs

- More folders
- Slightly higher initial complexity