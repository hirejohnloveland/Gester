# ADR-0007: Local Model Stack

## Status

Accepted

## Context

Gester requires locally hosted models for embedding generation and text
generation. ADR-0002 establishes local-first operation but does not
specify integration mechanisms.

The codebase must integrate with concrete local tooling without locking
in interim development defaults as permanent architecture.

## Decision

Gester uses two local model integration points.

### Embeddings

Embedding generation is handled by **Sentence Transformers** running
locally via the `sentence-transformers` library.

Embedding infrastructure lives in `infrastructure/embeddings/`.

### Text generation

Text generation is handled by **Ollama** accessed over its local HTTP
API.

LLM infrastructure lives in `infrastructure/llm/`.

### Coupling rule

The vector store vector dimension must match the active embedding model
output dimension. Changing embedding models requires updating the vector
index accordingly.

Application and domain layers depend on application services and
infrastructure abstractions — not on specific model names or library
call sites outside infrastructure.

## Consequences

### Benefits

- Both integrations run locally on consumer hardware
- Clear infrastructure boundaries for swapping models
- Aligns with ADR-0002 and the publishable learning goals

### Tradeoffs

- Sentence Transformers and Ollama are separate runtimes to manage
- Embedding model changes require re-embedding or rebuild
- Ollama model availability depends on local installation

## Non-Goals

- Cloud LLM or embedding APIs as required dependencies
- A single unified model serving both embedding and generation

## Deferred (see roadmap)

The following are **not** decided by this ADR and remain open work:

- Specific embedding and generation model selection (configurable per
  roadmap Phase 0.2 and Phase 2.3)
- Externalized configuration for model names, URLs, and parameters
- Prompt design, grounding rules, and citation policy (Phase 3)
- Larger-model selection for overnight synthesis work (Phase 5)

Do not treat current hardcoded development defaults as architectural
decisions. Externalize them when Milestone 0.2 is complete.
