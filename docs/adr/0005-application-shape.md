# ADR-0005: Application Shape

## Status

Accepted

## Context

Gester needs a clear definition of how users and developers interact
with the system. Without this, implementation effort may drift toward
CLI-only tooling or ad-hoc scripts that do not serve the long-term
product goals (weekly intelligence page, article browsing, search).

## Decision

Gester is a local web application with a React client and a Python
server.

The server exposes a FastAPI HTTP API. Current routes include ingestion,
chunking, embedding, search, and RAG answer endpoints.

The CLI (`run.py`) is a development convenience for starting the server.
It is not the primary user interface.

Core application behavior lives in application services under
`server/src/gester/application/`. Services must be callable from:

- Web routes (`app.py`)
- Background jobs (scheduled ingestion, overnight reports)
- Tests
- Temporary CLI adapters when needed for development

The React client will be introduced in Phase 6 (User Experience) to
deliver the dashboard, article reader, search experience, and weekly
intelligence page.

## Consequences

### Benefits

- Application logic is reusable across HTTP, jobs, and tests
- Clear separation between server API and future UI
- Aligns with the weekly intelligence page and personalization goals

### Tradeoffs

- React client is deferred until the backend pipeline is mature
- API design must remain stable enough for the future UI

## Non-Goals

- CLI as the primary user interface
- Tight coupling between route handlers and infrastructure details
