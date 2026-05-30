# ADR-0002: Local-First Architecture

## Status

Accepted

## Context

The purpose of the project is to build a personal AI knowledge base that remains under the user's control.

## Decision

The system will operate using a local-first architecture.

### Content Storage

Full source content will be stored locally.

### Embeddings

Embeddings will be generated locally whenever practical.

### Vector Database

The vector database will run locally.

### Language Models

Local models are the default.

Cloud models may be used as optional enhancements but should not be required for core system functionality.

## Consequences

### Benefits

- Data ownership
- Privacy
- Reduced recurring costs
- Offline operation
- Technology flexibility

### Tradeoffs

- Greater responsibility for infrastructure
- Local hardware constraints
- More storage requirements

## Non-Goals

- Dependence on cloud-hosted vector databases
- Dependence on cloud-hosted document storage
- Vendor lock-in