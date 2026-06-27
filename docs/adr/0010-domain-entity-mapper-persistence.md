# ADR-0010: Domain, Entity, and Mapper Persistence

## Status

Accepted

## Context

ADR-0001 separates domain models from infrastructure, but does not
define how persisted data moves between Python domain objects and the
database.

SQLAlchemy entities carry ORM concerns (columns, relationships, session
lifecycle). Domain models should remain free of persistence framework
dependencies so application logic stays testable and readable.

Domain models in this project are implemented as Pydantic `BaseModel`
classes. They are used for validation and serialization, but carry no
ORM mappings or database session awareness.

## Decision

SQLite persistence follows a three-part pattern.

### Domain models (`domain/models/`)

Pydantic `BaseModel` classes representing business concepts, free of
persistence-framework concerns.

- No SQLAlchemy imports
- No database session awareness
- Pydantic is used only for validation and serialization, not ORM mapping
- Used by application services and returned to callers

Examples: `SourceItem`, `SourceItemChunk`, `RssItem`, `TextChunk`.

### Entities (`infrastructure/storage/sqlite/entities/`)

SQLAlchemy ORM mappings for database tables.

- Define columns, constraints, and table structure
- Not passed into application service logic directly

Examples: `SourceItemEntity`, `SourceItemChunkEntity`.

### Mappers (`infrastructure/storage/sqlite/mappers/`)

Functions that translate between domain models and entities.

- `to_domain(entity)` — entity to domain model
- `to_entity(model)` — domain model to entity

Repositories call mappers at the infrastructure boundary. Application
code works exclusively with domain models.

### Repositories (`infrastructure/storage/sqlite/`)

Repositories encapsulate all database access.

- Open sessions, execute queries, commit transactions
- Return domain models via mappers
- Application layer depends on repositories, not on SQLAlchemy APIs

## Consequences

### Benefits

- Domain and application layers stay persistence-agnostic
- Database schema changes are localized to entities and mappers
- Consistent pattern across all stored types
- Easier unit testing of application services with domain models

### Tradeoffs

- Boilerplate for mappers on each persisted type
- Must maintain parallel domain model and entity definitions

## Non-Goals

- SQLAlchemy models in `domain/`
- Application services importing `SessionLocal` or entities directly
- Generic catch-all mapper frameworks

## Guiding Rule

If code in `domain/` or `application/` imports from
`infrastructure/storage/sqlite/entities/`, the boundary has been
violated.
