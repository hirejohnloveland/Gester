# ADR-0003: Agent Philosophy

## Status

Accepted

## Context

The project is intended to become an AI-powered knowledge base and content curation system.

Many modern AI systems introduce agents early in development. While agents can provide flexibility, they also introduce complexity, non-deterministic behavior, increased debugging effort, and additional maintenance costs.

The project owner prefers explicit, understandable code and deterministic pipelines whenever possible.

### Terminology

This ADR governs **runtime agents** — autonomous in-app systems that decide their own steps (search again, fetch more content, change strategy, loop until done).

It does **not** govern **AI coding assistants** (Cursor, Copilot, etc.). Those are constrained by `agents/agents.md` and ADR-0004.

Using an LLM inside a fixed workflow is not a runtime agent. For example, a RAG answer service that always executes search → build prompt → generate → return is a deterministic pipeline with an LLM step, not a runtime agent.

## Decision

The system will follow a "Deterministic First" philosophy.

Deterministic pipelines should be the default solution.

Agent-based solutions should only be introduced when deterministic solutions become insufficient.

Examples of appropriate deterministic pipelines:

- RSS ingestion
- Content extraction
- Document chunking
- Embedding generation
- Vector indexing
- Retrieval
- Report generation

Examples where agents may eventually be justified:

- Content discovery
- Multi-step research workflows
- Autonomous topic exploration
- Personalized content curation
- Complex summarization workflows

## Consequences

Benefits:

- Easier debugging
- More predictable behavior
- Simpler testing
- Lower operational complexity
- Reduced implementation risk

Tradeoffs:

- Less flexibility during early phases
- Some future capabilities may require architectural changes

## Guiding Principle

A pipeline should only become an agent when a pipeline is no longer sufficient.