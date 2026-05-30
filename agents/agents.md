# AI Agent Instructions

## Purpose

This repository contains a local-first AI knowledge base focused on acquiring, storing, retrieving, and summarizing AI-related content.

The system should remain understandable, maintainable, and largely deterministic. Agent-based solutions should only be introduced when they provide clear value over conventional application logic.

---

## Architecture Decisions

Architectural decisions are documented in:

- docs/adr/
- docs/coding-standards.md


Review relevant ADRs before making significant architectural changes.

If a significant architectural decision is introduced, create or update an ADR.

---

## Project Structure

The repository follows a Domain / Application / Infrastructure architecture.

### domain

Contains business concepts and models.

### application

Contains orchestration and use-case logic.

### infrastructure

Contains implementation details and external integrations.

### config

Configuration files.

### data

Locally stored runtime data.

### docs

Project documentation and Architecture Decision Records.

### agents

Instructions and guidance for AI coding assistants.

For additional details, see ADR-0001.

---

## Decision Making

When proposing changes:

1. Prefer the simplest solution that satisfies the requirement.
2. Prefer deterministic pipelines over agents.
3. Prefer local solutions over cloud solutions.
4. Prefer explicit code over framework magic.
5. Prefer small focused files over large multi-purpose files.

If a significant architectural decision is required, create or update an ADR.

---

## Expectations for AI Assistants

Do not:

- Introduce new frameworks without discussion.
- Introduce cloud dependencies without discussion.
- Introduce new architectural layers without discussion.
- Perform broad refactors when a targeted change is sufficient.
- Create catch-all modules or dumping grounds for unrelated code.
- Expand the scope of a requested change without discussion.
- Make unrelated or unnecessary changes.

Do:

- If a larger change appears necessary, explain the rationale and obtain agreement before proceeding.
- Suggest improvements, missing considerations, architectural concerns, or extensibility issues when relevant.
- Clearly distinguish between:
  - The requested change.
  - Recommended enhancements.
  - Optional future improvements.

---

## Scope of Changes

Implement the requested change and only the requested change.

If additional changes are recommended:

- Explain the recommendation.
- Explain the benefit.
- Ask before proceeding.