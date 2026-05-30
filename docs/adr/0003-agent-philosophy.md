# ADR-0003: Agent Philosophy

## Status

Accepted

## Context

The project is intended to become an AI-powered knowledge base and content curation system.

Many modern AI systems introduce agents early in development. While agents can provide flexibility, they also introduce complexity, non-deterministic behavior, increased debugging effort, and additional maintenance costs.

The project owner prefers explicit, understandable code and deterministic pipelines whenever possible.

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