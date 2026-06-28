# ADR-0011: Configuration Management

## Status

Accepted

## Context

The codebase hard-coded operational values inside business and
infrastructure logic: the RSS feed URL, embedding model name, Ollama
base URL / model / temperature / timeout, chunk size and overlap, the
Qdrant path / collection / vector size / distance, the SQLite path, and
retrieval defaults. This violates the configuration guidance in
`docs/coding-standards.md` and makes the system hard to retarget between
machines or environments.

Services and repositories also self-instantiated their collaborators and
imported module-level database globals (`engine`, `SessionLocal`),
hiding their dependencies and coupling them to a single fixed
configuration.

Roadmap milestone 0.2 calls for a validated configuration layer before
further feature work.

## Decision

Gester loads configuration once at startup and passes it into services
via explicit constructor injection.

### Source of values

- **Committed YAML** (`config/settings.yaml`) holds non-secret defaults:
  `paths`, `feeds[]` (`name` / `url` / `enabled`), `chunking`,
  `embedding`, `vector_store`, `llm`, and `retrieval`.
- **Environment variables** override deploy-specific values. A small,
  explicit set is supported: `GESTER_CONFIG_PATH` (settings file
  location), `GESTER_DATA_DIR` (runtime data directory), and
  `GESTER_OLLAMA_BASE_URL` (LLM endpoint).

### Validation

Settings are validated into Pydantic models in the `configuration`
package (`AppSettings` and nested section models, plus
`FeedSourceSettings`). `settings_loader.load_settings()` resolves the
project root, reads the YAML, applies the env overrides, and validates.
`AppSettings` holds resolved absolute `project_root` and `data_dir` and
derives `database_path` and `qdrant_path` from `data_dir`.

### Constructor injection

Infrastructure constructors take explicit parameters
(`EmbeddingService(model_name)`,
`QdrantVectorStore(path, collection_name, vector_size, distance)`,
`OllamaClient(base_url, model, temperature, timeout)`;
`TextChunkingService` was already parameterized). Application services
receive their collaborators through their constructors rather than
self-instantiating them.

### Session-factory injection

`sqlite_db` no longer exposes import-time globals. It provides
`create_db_engine(database_path)`, `create_session_factory(engine)`, and
`initialize_database(engine)`. Repositories receive a `session_factory`
in `__init__` instead of importing a module-global `SessionLocal`.

### Composition root and providers

`app.py` is the composition root: on startup it calls `load_settings()`,
builds the engine and session factory, stores `settings` and
`session_factory` on `app.state`, and calls `initialize_database(engine)`.
`api/dependencies.py` provides FastAPI `Depends` functions
(`get_settings`, repository/infrastructure providers, and service
providers) that assemble the dependency graph from settings. Routers
stay thin: `/ingest/rss` iterates the enabled feeds from settings, and
`/search` and `/ask` fall back to `settings.retrieval` defaults when
query parameters are omitted.

## Consequences

### Benefits

- No operational values hard-coded in business logic
- Single, validated source of truth loaded once at startup
- Dependencies are explicit and testable; no hidden global state
- Feeds are config-driven and individually enable/disable-able
- Environment overrides keep secrets and deploy specifics out of git

### Tradeoffs

- More wiring in the composition root and dependency providers
- Adds Pydantic settings models and a YAML file to maintain

## Non-Goals

- Logging configuration (milestone 0.1)
- Full multi-source-type extensibility (milestone 1.3)
- Secret management beyond simple environment-variable overrides
- A generic plugin/registry configuration framework

## Note on Numbering

ADR numbers are sequential. There is no ADR-0008 in the record set; this
gap is intentional and ADR numbers are not reused.

## Guiding Rule

If code in `application/` or `infrastructure/` reads a path, URL, model
name, or service setting directly instead of receiving it through its
constructor, the configuration boundary has been violated.
