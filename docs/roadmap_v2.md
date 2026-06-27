# Gester Roadmap

## Project Goal

Gester is a local-first AI knowledge platform focused on acquiring,
organizing, searching, and summarizing information about local AI,
applied AI, and other curated technical sources. The project is
primarily a learning exercise in building a high-quality, production-grade
local Retrieval-Augmented Generation (RAG) system — and a publishable
reference for others who want to do the same.

### Primary Objectives

1. **Knowledge ingestion** — Build a pipeline that synthesizes content
   from curated sources such as XDA Developers, the Anthropic blog, the
   OpenAI blog, email topics, and other configurable feeds.
2. **Production-grade RAG** — Chunk, embed, and summarize that content
   into a high-quality retrieval pipeline with measurable quality.
3. **Weekly intelligence experience** — On a weekly overnight schedule,
   review accumulated content and produce an interactive React page (or
   similar) where content can be browsed, searched, and explored. Use a
   larger local model for synthesis work (target hardware: 64 GB DDR4,
   medium-sized model at acceptable speed). Surface trend summaries
   across weekly, monthly, quarterly, and yearly horizons. Support
   reading individual articles. Over time, interactions should
   personalize recommendations so engaged content is prioritized.
4. **Local agent education** — Teach how to build, design, develop, and
   deploy local agents as a documented, hands-on part of the project.
5. **Agent guardrails** — Use the `docs/` folder (ADRs, coding
   standards, project structure) and `agents/` instructions to provide
   oversight and guardrails for AI coding assistants. Prior experience
   showed that work goes off the rails quickly without explicit
   constraints — including basics like remembering the current project
   structure.

Guiding principles:

-   Local-first (LLMs, embeddings, vector database)
-   Write most of the code manually
-   Favor understanding over speed
-   Build complete, working subsystems before moving on
-   Deterministic pipelines first; agents only when pipelines are
    insufficient (see ADR-0003)
-   Keep `docs/` and `agents/` current as the project evolves

------------------------------------------------------------------------

## Status Legend

Status reflects implementation verified against the codebase as of
2026-06-27, mapping each milestone's "Done When" criteria to working
code.

-   **Complete** — all material "Done When" criteria are met in code
-   **In progress** — partially implemented; remaining gaps noted inline
-   **Not started** — no implementing code yet

Note: configuration is not yet externalized (see Milestone 0.2), so
"configurable via config file" sub-criteria are deferred and tracked
under 0.2 rather than blocking otherwise-complete milestones.

Current position: the last fully complete milestone is **3.2 RAG
Responses**. Phases 5–8 are entirely not started.

------------------------------------------------------------------------

# Phase 0 -- Foundation — In progress

**Purpose**

Establish the project structure, configuration, development environment,
and documentation guardrails required for reliable agent-assisted work.

**Learning Objectives**

-   Project organization
-   Configuration management
-   Dependency management
-   Documentation-driven development

**Completion Criteria**

The application starts successfully, configuration is externalized, the
project structure is ready for future work, and agent guardrails are in
place.

## Milestone 0.1 -- Project Skeleton — In Progress

_Note: app starts via `run.py` / `gester.app:app`; logging currently
relies on uvicorn defaults rather than an explicit logging setup._

Purpose: Create the repository, entry point, and basic application
structure.

Done When:

-   Repository created
-   Virtual environment configured
-   Application starts
-   Basic logging works

## Milestone 0.2 -- Configuration — In progress

_Remaining: no `config/` layer exists; feed URL, embedding model, LLM
model, and chunk size/overlap are hardcoded. No `.env` /
secrets separation in the repo._

Purpose: Externalize application configuration.

Done When:

-   Configuration files load successfully
-   Models and sources are configurable
-   Secrets are separated from source control

## Milestone 0.3 -- Documentation & Agent Guardrails — Complete

Purpose: Establish the documentation system that keeps AI assistants
aligned with project structure, decisions, and constraints.

Done When:

-   `agents/agents.md` describes project structure, expectations, and
    scope limits for AI assistants
-   ADRs document significant architectural decisions (`docs/adr/`)
-   Coding standards are documented (`docs/coding-standards.md`)
-   Project structure changes trigger corresponding documentation
    updates
-   Roadmap and ADRs are referenced before significant new work

------------------------------------------------------------------------

# Phase 1 -- Content Acquisition — In progress

**Purpose**

Acquire content from configured sources and persist the original
documents locally. Target sources include RSS feeds (XDA Developers,
Anthropic blog, OpenAI blog, and similar), email topics, and other
extensible source types.

**Learning Objectives**

-   RSS parsing
-   HTML extraction
-   Background processing
-   Multi-source ingestion design

**Completion Criteria**

Content is acquired repeatedly without manual intervention from all
configured sources.

## Milestone 1.1 -- RSS Ingestion — Complete

Purpose: Retrieve article metadata from configured RSS feeds.

Done When:

-   Feed items are retrieved successfully
-   Duplicate entries are prevented
-   Article metadata is stored locally

## Milestone 1.2 -- Article Retrieval — Complete

Purpose: Retrieve and store the full text of articles.

Done When:

-   Full article text is stored locally
-   Metadata and source URLs are preserved
-   Previously processed articles are skipped

## Milestone 1.3 -- Source Management — In progress

_Done: `source_type` carried on the domain model/entity; design is
extensible. Remaining: feed URL is hardcoded in the router (not
config-driven), and there is no enable/disable mechanism._

Purpose: Support multiple configurable source types.

Done When:

-   Sources are configuration-driven
-   New sources can be added without code changes
-   Sources can be enabled or disabled through configuration
-   RSS is supported today; design is extensible for email and other
    source types

## Milestone 1.4 -- Email Ingestion — Not started

Purpose: Ingest content from email topics and newsletters.

Done When:

-   Email sources are configurable
-   Message content is extracted and stored as source items
-   Duplicate messages are prevented
-   Email metadata (subject, sender, date) is preserved

------------------------------------------------------------------------

# Phase 2 -- Knowledge Storage — In progress

**Purpose**

Convert acquired documents into a searchable, production-grade knowledge
base through chunking, embedding, and vector storage.

**Learning Objectives**

-   Chunking strategies
-   Local embeddings
-   Vector databases

**Completion Criteria**

Articles are chunked, embedded locally, and searchable with preserved
source traceability.

## Milestone 2.1 -- Metadata Storage — Complete

Purpose: Store articles in a structured local repository.

Done When:

-   Articles are stored in SQLite
-   Duplicate content is detected
-   Source metadata is preserved

## Milestone 2.2 -- Chunking — In Progresss

_Note: size/overlap are constructor parameters (defaults 1000/200); not
yet wired to external config (tracked under 0.2)._

Purpose: Split documents into retrieval-friendly chunks.

Done When:

-   Articles are automatically chunked
-   Chunk size and overlap are configurable
-   Chunks remain linked to source articles
-   Chunk metadata is stored

## Milestone 2.3 -- Local Embeddings — I Pgoress

_Note: embeddings run locally (`BAAI/bge-small-en-v1.5`) with no cloud
dependency and are tracked via `embedded_at`; model name is hardcoded
(externalization tracked under 0.2)._

Purpose: Generate embeddings using locally hosted models.

Done When:

-   Embeddings are generated locally
-   No cloud AI services are required
-   Embedding models are configurable
-   Embeddings are stored successfully

## Milestone 2.4 -- Vector Storage — In progress

_Done: vectors indexed in local Qdrant, cosine similarity search works,
results carry source metadata. Remaining: metadata filtering on search
is not implemented (payload is only `chunk_id` / `source_item_id`)._

Purpose: Store embeddings for semantic retrieval.

Done When:

-   Vectors are indexed
-   Semantic similarity search functions correctly
-   Results include source metadata
-   Metadata filtering is supported

------------------------------------------------------------------------

# Phase 3 -- Retrieval Pipeline — In progress

**Purpose**

Build a solid retrieval pipeline before focusing on generation.

**Learning Objectives**

-   Retrieval architecture
-   Search APIs
-   Grounded prompting

**Completion Criteria**

Natural-language questions retrieve relevant grounded context with
traceable sources.

## Milestone 3.1 -- Retrieval Service — Complete

Purpose: Retrieve relevant content using vector similarity.

Done When:

-   Search API is available
-   Search returns meaningful, relevant results
-   Configurable result limits and minimum score thresholds
-   Retrieved content preserves source information

## Milestone 3.2 -- RAG Responses — Complete

Purpose: Generate answers using retrieved content.

Done When:

-   Prompt construction is grounded in retrieved chunks
-   Questions are answered using stored knowledge
-   Responses include supporting evidence and source citations
-   Responses remain grounded in retrieved content

## Milestone 3.3 -- Retrieval Diagnostics — In progress

_Done: chunks can be inspected via `GET /items/{id}/chunks` and search
params are tunable per request. Remaining: no side-by-side comparison of
retrieval settings and no structured retrieval-debugging tooling._

Purpose: Inspect and improve retrieval quality during development.

Done When:

-   Retrieved chunks can be inspected
-   Retrieval quality can be debugged
-   Retrieval settings can be compared side by side

## Milestone 3.4 -- Source Attribution — In progress

_Done: every `/search` and `/ask` response carries title, URL, score,
and chunk/source IDs, and the prompt enforces inline citations.
Remaining: no user-facing UI to make citations visible or open original
articles (depends on Phase 6)._

Purpose: Provide traceability back to original sources.

Done When:

-   Every response references source material
-   Original articles can be opened directly
-   Citations are visible to users

------------------------------------------------------------------------

# Phase 4 -- Retrieval Quality — In progress

**Purpose**

Improve retrieval accuracy rather than simply making it functional.
Move from a working RAG pipeline toward production-grade quality.

**Learning Objectives**

-   Hybrid retrieval
-   BM25
-   Reranking
-   Retrieval evaluation

**Completion Criteria**

Retrieval quality has been measured and demonstrably improved.

## Milestone 4.1 -- Search Tuning — In progress

_Done: per-article dedup (over-fetches `limit * 4`), configurable chunk
limit and `min_score`. Remaining: thresholds are not systematically
calibrated (no evaluation harness yet — see 4.3)._

Purpose: Tune retrieval parameters for better precision and recall.

Done When:

-   Chunk limits are tuned
-   Article deduplication in results works correctly
-   Score thresholds are calibrated

## Milestone 4.2 -- Hybrid Retrieval — Not started

Purpose: Combine keyword and vector search for better coverage.

Done When:

-   Keyword (BM25) and vector search are combined
-   Metadata filtering improves result relevance

## Milestone 4.3 -- Evaluation — Not started

_Note: no test files or query/benchmark sets exist in the repo._

Purpose: Measure and benchmark retrieval quality objectively.

Done When:

-   Test query sets are defined
-   Relevance can be evaluated systematically
-   Retrieval benchmarks track improvement over time

------------------------------------------------------------------------

# Phase 5 -- Knowledge Refinement — Not started

**Purpose**

Transform retrieved knowledge into higher-level intelligence using
locally hosted models. Heavier synthesis work (weekly reports, trend
analysis) uses a larger local model suited to 64 GB DDR4 hardware.

**Learning Objectives**

-   Summarization
-   Topic extraction
-   Trend identification
-   Scheduled overnight batch jobs

**Completion Criteria**

The system automatically produces meaningful synthesized knowledge on
daily and weekly schedules.

## Milestone 5.1 -- Article Summaries — Not started

Purpose: Generate concise summaries for newly acquired content.

Done When:

-   Summaries are generated automatically
-   Summaries include structured topics and practical takeaways
-   Summaries are stored locally
-   Summaries are displayed in the UI

## Milestone 5.2 -- Daily Digest — Not started

Purpose: Produce a daily intelligence briefing.

Done When:

-   Daily reports are generated automatically
-   Reports summarize recent activity
-   Reports are viewable through the UI

## Milestone 5.3 -- Theme & Trend Summaries — Not started

Purpose: Identify how topics evolve over time.

Done When:

-   Related articles are grouped by theme
-   Topic summaries are produced for each theme
-   Trend summaries cover weekly, monthly, quarterly, and yearly
    horizons
-   Significant changes in topic momentum are highlighted

## Milestone 5.4 -- Weekly Intelligence Report — Not started

Purpose: Generate a curated weekly intelligence report as an overnight
batch job using a larger local model.

Done When:

-   Weekly reports are generated automatically on an overnight schedule
-   Major themes and significant developments are identified
-   Reports include source links
-   Report output feeds the interactive weekly experience (Phase 6)

------------------------------------------------------------------------

# Phase 6 -- User Experience — Not started

_Note: no React client, `client/`, or `package.json` exists yet; the
project is API-only._

**Purpose**

Provide a useful React-based interface for consuming, searching, and
interacting with synthesized intelligence — especially the weekly
intelligence page.

**Learning Objectives**

-   UI design
-   Search UX
-   React application development

**Completion Criteria**

Users can browse articles, search content, view trend summaries across
time horizons, and read generated responses through a web interface.

## Milestone 6.1 -- Dashboard — Not started

Purpose: Provide an overview of recently acquired content.

Done When:

-   Recent articles are visible
-   Basic navigation exists
-   Content can be filtered
-   Personalized recommendations surface prioritized content

## Milestone 6.2 -- Article Reader — Not started

Purpose: Allow users to read stored content.

Done When:

-   Full article text is viewable
-   Metadata is displayed
-   Source links are available
-   Article summaries and topics are visible alongside content

## Milestone 6.3 -- Search Experience — Not started

Purpose: Expose retrieval functionality through the web interface.

Done When:

-   Users can submit natural language queries
-   Results include supporting sources and citations
-   Original articles can be opened from search results
-   Related content is displayed

## Milestone 6.4 -- Weekly Intelligence Page — Not started

Purpose: Deliver the primary weekly intelligence experience as an
interactive React page.

Done When:

-   Weekly report content is rendered as an interactive page
-   Trend summaries (weekly, monthly, quarterly, yearly) are browsable
-   Theme groupings and significant developments are navigable
-   Source links connect back to individual articles
-   Page updates automatically after each overnight report run

------------------------------------------------------------------------

# Phase 7 -- Personalization — Not started

**Purpose**

Learn what content is valuable to the user and prioritize it across
search, dashboards, and weekly reports.

**Learning Objectives**

-   Ranking
-   Feedback systems
-   Personalization

**Completion Criteria**

Recommendations and rankings improve based on user behavior over time.

## Milestone 7.1 -- Engagement Tracking — Not started

Purpose: Record user interactions with content.

Done When:

-   Article reads are tracked
-   Searches are tracked
-   Saved content is tracked

## Milestone 7.2 -- Interest Model — Not started

Purpose: Develop a model of user interests from engagement data.

Done When:

-   Interest categories are identified
-   Interests evolve over time
-   Profile data is stored locally

## Milestone 7.3 -- Personalized Ranking — Not started

Purpose: Improve retrieval and recommendations using engagement data.

Done When:

-   Search and browse results incorporate user interests
-   Weekly reports reflect engagement history
-   Ranking quality improves measurably over time

------------------------------------------------------------------------

# Phase 8 -- Agent Workflows — Not started

_Note: only documentation groundwork exists (ADR-0003 agent philosophy,
`agents/agents.md` coding-assistant guardrails); no runtime agents._

**Purpose**

Introduce agents only after the retrieval and knowledge pipeline is
mature. Document the full lifecycle — design, development, and local
deployment — as publishable educational content.

**Learning Objectives**

-   Agent orchestration
-   Long-running workflows
-   Autonomous research
-   Local agent design and deployment

**Completion Criteria**

Agents perform useful work on top of a trustworthy knowledge base, and
the project documents how to build and deploy them locally.

## Milestone 8.1 -- Research Agent — Not started

Purpose: Perform focused investigations on a specific topic.

Done When:

-   Agent retrieves relevant information from the knowledge base
-   Agent generates topic summaries
-   Agent cites supporting sources
-   Design and implementation are documented for publication

## Milestone 8.2 -- Trend Analysis Agent — Not started

Purpose: Identify emerging patterns across acquired content.

Done When:

-   Trends are detected automatically
-   Significant changes are highlighted
-   Trend reports are generated
-   Agent workflow is documented as a reusable pattern

## Milestone 8.3 -- Curator Agent — Not started

Purpose: Produce highly curated intelligence reports tailored to user
interests.

Done When:

-   Reports incorporate engagement history
-   Reports include trend analysis
-   Reports prioritize relevant content
-   Local deployment and operation are documented

## Milestone 8.4 -- Agent Development Guide — Not started

Purpose: Publish a practical guide for building, designing, developing,
and deploying local agents using patterns established in this project.

Done When:

-   Guide covers when to use agents vs. deterministic pipelines
-   Guide documents agent architecture used in Gester
-   Guide covers local deployment on consumer hardware
-   Guide references ADRs and guardrails that kept agent work on track

------------------------------------------------------------------------

# Version 1 Success Criteria

Gester is considered Version 1 complete when:

-   Scheduled ingestion runs multiple times per day from configured
    sources (RSS, email, and extensible source types)
-   Content is stored locally with deduplication and source metadata
-   Embeddings are generated locally with no cloud AI dependency
-   High-quality, measured retrieval pipeline (hybrid search, tuning,
    evaluation)
-   Grounded RAG responses with visible source citations
-   Daily digests and weekly intelligence reports generated automatically
-   Weekly intelligence experience delivered as an interactive React page
-   Trend summaries available across weekly, monthly, quarterly, and
    yearly horizons
-   User interactions personalize ranking and recommendations
-   Local agents are documented with a publishable development guide
-   `docs/` and `agents/` guardrails remain current and enforced
-   All AI workloads execute locally
