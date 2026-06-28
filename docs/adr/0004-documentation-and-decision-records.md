# ADR-0004: Documentation and Agent Guardrails

## Status

Accepted

## Context

Gester is developed with significant help from AI coding assistants.
Prior experience showed that work goes off the rails quickly without
explicit guardrails — including failures to remember the current project
structure, architectural constraints, and scope of a requested change.

The project also serves as a publishable learning reference. Decisions,
structure, and conventions must remain documented and current.

Roadmap milestone 0.3 establishes a documentation system that keeps AI
assistants aligned with project structure, decisions, and constraints.

## Decision

Gester maintains a layered documentation system with clear roles for
each document type.

### Roadmap

`docs/roadmap_v2.md` is the authoritative plan for what to build and in
what order. AI assistants should consult it before starting significant
new work.

### Architecture Decision Records

Significant architectural decisions are recorded in `docs/adr/` using the
standard ADR format (status, context, decision, consequences).

Current ADRs:

| ADR | Topic |
|-----|-------|
| ADR-0001 | Project structure (domain / application / infrastructure) |
| ADR-0002 | Local-first architecture |
| ADR-0003 | Agent philosophy (deterministic pipelines first) |
| ADR-0004 | Documentation and agent guardrails (this record) |
| ADR-0005 | Application shape (Python server, React client) |
| ADR-0006 | Dual persistence (SQLite and Qdrant) |
| ADR-0007 | Local model stack (Ollama, Sentence Transformers) |
| ADR-0009 | Staged ingestion pipeline |
| ADR-0010 | Domain, entity, and mapper persistence |
| ADR-0011 | Configuration management |

New ADRs are numbered sequentially. Do not rewrite accepted ADRs to
reverse a decision; supersede them with a new ADR instead.

Do not record ADRs for incomplete roadmap work or interim development
shortcuts. Document decisions that are intentional and stable; defer
prompt design, grounding policy, configuration, and orchestration until
those milestones are complete.

### Coding Standards

`docs/coding-standards.md` defines Python conventions, file organization,
and code quality expectations. It is maintained separately from AI
assistant instructions.

### AI Assistant Instructions

`agents/agents.md` provides guardrails for AI coding assistants. It
references authoritative documents rather than duplicating them.

`agents/agents.md` must describe:

- Current project structure and directory layout
- Expectations and scope limits for AI assistants
- Which documents to read before starting work
- When and how to update documentation after changes

### Separation of Concerns

| Document | Answers |
|----------|---------|
| Roadmap | What to build and when |
| ADRs | Why architectural choices were made |
| Coding standards | How to write code |
| agents/agents.md | How AI assistants should behave |

Avoid duplicating content across these documents. Cross-reference
instead.

### Maintenance Triggers

Documentation must be updated in the same change set when:

- Directory structure or layer boundaries change
- A new subsystem or integration is added
- An architectural decision is made or reversed
- Coding conventions change

At minimum, update `agents/agents.md` and the relevant ADR. Update the
roadmap when a milestone is completed or scope changes.

## Consequences

### Benefits

- AI assistants stay aligned with project structure and decisions
- Architectural rationale is preserved for future work and publication
- Reduced scope creep and off-rails refactors
- Clear onboarding path for human contributors

### Tradeoffs

- Documentation must be maintained alongside code changes
- Slight overhead on each structural change

## Guiding Principle

If the code changed in a way that would confuse a future AI assistant
about where things belong or why they exist, the documentation must be
updated before the work is considered complete.
