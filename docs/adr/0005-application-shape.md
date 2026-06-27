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

### Presentation layer (`api/`)

The server exposes a FastAPI HTTP API. HTTP route handlers live in
FastAPI `APIRouter` modules under `server/src/gester/api/routers/`,
grouped by concern:

- `content_router` — browse stored items and chunks
- `ingestion_router` — ingest, chunk, reset chunks, embed
- `retrieval_router` — search and RAG answers

Route handlers are thin: they call application services and map results
to response models (`application/responses/`). They do not contain
business logic or access infrastructure directly.

### Composition root (`app.py`)

`app.py` is the composition root. It creates the FastAPI app, includes
the routers, and performs startup bootstrap (e.g. database
initialization). As the composition root, it is the one place permitted
to wire infrastructure into the running application.

The CLI (`run.py`) is a development convenience for starting the server.
It is not the primary user interface.

### Application services

Core application behavior lives in application services under
`server/src/gester/application/`. Services must be callable from:

- HTTP routers (`api/routers/`)
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
- Business logic inside route handlers
- A single module containing all HTTP routes
