# Python Coding Standards

## Purpose

These standards keep the Gester codebase understandable, maintainable, and easy to extend.

The goal is not to create excessive rules. The goal is to avoid large files, unclear responsibilities, hidden coupling, and unnecessary complexity.

Authoritative project documentation:

- `docs/roadmap_v2.md` — build plan and milestones
- `docs/adr/` — architectural decisions
- `agents/agents.md` — guardrails for AI coding assistants

See ADR-0004 for how these documents relate to each other.

---

## General Principles

* Prefer simple, explicit code.
* Prefer deterministic logic over agentic behavior.
* Prefer small focused files over large multi-purpose files.
* Prefer clear names over clever abstractions.
* Avoid premature generalization.
* Avoid broad refactors unless explicitly approved.
* Prefer Clean Coding principles in all development work. Code should be:
- Clean
- Readable
- Maintainable
- Extensable
- Loosely coupled
- Highly cohesive
- Adhere to SOLID Principles
---

## File Organization

Each file should have one clear responsibility.  Files should be grouped into meaningful folders based
on similar abstraction types. 

Avoid catch-all files such as:

* `utils.py`
* `helpers.py`
* `common.py`
* `models.py`

Prefer focused files such as:

* `feed_source.py`
* `feed_item.py`
* `rss_feed_reader.py`
* `article_fetcher.py`
* `readable_text_extractor.py`
* `ingestion_pipeline.py`

So, by way of example, instead of a single models file, prefer a models folder with contents like
- rss_feed.py
- html_article.py
- rss_feed_item.py

---

## File Length

Keep files short enough to understand quickly.

General guidance:

* Under 150 lines is preferred.
* 150-250 lines is acceptable when the file has one clear responsibility.
* Over 250 lines should trigger a review.
* Over 400 lines should usually be split.

Do not split files mechanically. Split when responsibilities are becoming unclear.

---

## Naming

Use standard Python naming conventions:

* Files and modules: `snake_case.py`
* Functions: `snake_case`
* Variables: `snake_case`
* Classes: `PascalCase`
* Constants: `UPPER_SNAKE_CASE`

Names should describe purpose.

Prefer:

```python
rss_feed_reader.py
article_document.py
extract_readable_text()
```

Avoid vague names:

```python
processor.py
manager.py
handler.py
data.py
```

Use names like `manager`, `processor`, or `handler` only when the responsibility is genuinely specific and clear.

File names should generally be postfixed with the service type for donwstream readability concerns.
For example, a service class called rss_feed is ambiguous. It could be a model, it could be a service. 
Instead, differentiate with postfix class types such as rss_feed_dto, rss_feed_ingestion_service.

---

## Functions

Functions should do one thing.

Prefer functions that are:

* Easy to name
* Easy to test
* Easy to read without scrolling
* Free of unrelated side effects

General guidance:

* Under 40 lines is preferred.
* If a function grows beyond 20-30 lines, contains multiple responsibilities, or repeats logic found elsewhere, consider extracting a private helper.
* Over 75 lines should trigger a review.

A function that fetches data should not also parse, store, embed, and index it.


---

## Classes

Classes should represent one clear concept or implementation.

Good examples:

* `FeedSource`
* `FeedItem`
* `RssFeedReader`
* `ReadableTextExtractor`
* `QdrantVectorStore`

Avoid classes that become dumping grounds for unrelated behavior.  A class should have one reason to change.

---

## Type Hints

Use type hints for public functions, methods, and data models.

Prefer:

```python
def read_feed(feed_source: FeedSource) -> list[FeedItem]:
    ...
```

Avoid untyped public interfaces unless there is a clear reason.

---

## Data Models

Use dataclasses for simple domain models unless validation or parsing requirements justify another tool.

Prefer one model per file.

Example:

```text
domain/models/feed_source.py
domain/models/feed_item.py
```

---

## Dependencies

Keep dependencies flowing in the intended direction:

```text
application -> domain
infrastructure -> domain
```

Domain code should not depend on infrastructure code.

Application code should coordinate workflows.

Infrastructure code should contain external library usage and implementation details.

---

## Error Handling

Handle expected failures explicitly.

Examples:

* Failed RSS fetch
* Invalid article URL
* Failed HTML extraction
* Failed embedding generation
* Failed vector database write

Do not silently swallow errors.

When continuing after an error, record enough information to troubleshoot later.
Erros objects should use a defined and repeatable error shape, so that consumers always have the same error contract.

---

## Configuration

Do not hard-code paths, model names, URLs, or service settings inside business logic.

Use configuration files or environment variables for values such as:

* RSS feed URLs
* Data paths
* Qdrant URL
* Embedding model name
* Collection names

Settings live in `config/settings.yaml` and are loaded and validated by
the `configuration` package (`load_settings()` in
`server/src/gester/configuration/settings_loader.py`). Pass settings into
services via constructor injection rather than reading them inside
business logic. See ADR-0011.

---

## Logging

Use logging for pipeline activity and failures.

Avoid excessive logging in low-level code.

Useful logs include:

* Feed started
* Article fetched
* Article skipped
* Extraction failed
* Chunks created
* Embeddings generated
* Vectors indexed


---


## Testing Guidance

Prefer testing focused units of behavior.

Good test targets:

* RSS feed parsing
* URL deduplication
* Article extraction
* Chunking
* Local file storage paths
* Search result formatting

Avoid tests that require live external services unless clearly marked as integration tests.  Avoid testing 
that requires mocking database dependencies. Code should not have to be rewritten for testing.  The need to change code to make a test compile should be a warning that the developer needs to be informed of the issue and provide feedback.

---

## Scope Control

When changing code:

* Make the requested change.
* Avoid unrelated cleanup.
* Avoid opportunistic refactors.
* Avoid changing architecture without discussion.

If a broader change seems necessary, explain the reason before making it.

---

## Formatting

Use standard Python formatting tools.

Preferred tools:

* `black`
* `ruff`

Do not hand-format code in a way that fights the formatter.

---

## Guiding Rule

Code should be boring, obvious, and easy to change.
