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

- SourceItem
- SourceItemChunk
- RssItem
- TextChunk

### Application

Contains use cases and orchestration logic.

Examples:

- RssIngestionService
- SourceItemChunkingService
- ChunkEmbeddingService
- SearchService
- AnswerService

### Infrastructure

Contains implementation details.

Examples:

- RssReader
- ArticleExtractor
- EmbeddingService
- QdrantVectorStore
- OllamaClient
- SQLite repositories and mappers

## Consequences

### Benefits

- Clear separation of concerns
- Small focused files
- Easier testing
- Easier replacement of infrastructure components

### Tradeoffs

- More folders
- Slightly higher initial complexity