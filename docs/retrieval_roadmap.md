# Gester RAG Retrieval Roadmap

## Purpose

This roadmap defines the next phase of Gester’s retrieval work.

The goal is not merely to make search “work.” The goal is to learn RAG deeply by building, testing, and improving a serious local-first retrieval pipeline.

Gester should evolve from basic vector search into a measurable knowledge base and retrieval-augmented answer system that can:

* Retrieve relevant source material reliably
* Explain why results were returned
* Support sourced, grounded answers
* Improve through repeatable evaluation
* Compare retrieval strategies instead of relying on intuition
* Keep all AI processing local

## Guiding Principle

Do not tune RAG by vibes.

Every retrieval improvement should follow this loop:

```text
Create test questions
Run retrieval
Inspect results
Classify failures
Change one thing
Re-run the same tests
Compare results
Keep or revert the change
```

The purpose of this roadmap is to make retrieval quality observable, testable, and improvable.

---

## Status Legend

Status reflects implementation verified against the codebase as of
2026-06-30, mapping each milestone's "Done When" criteria to working
code.

-   **Complete** — all material "Done When" criteria are met in code
-   **In progress** — partially implemented; remaining gaps noted inline
-   **Not started** — no implementing code yet

Current position: vector search, article deduplication, metadata-enriched
embeddings (title + URL), and grounded `/ask` responses with citations
are working. Configurable fixed-size chunking and staged re-chunk/re-embed
endpoints exist. **Phase 1 retrieval evaluation** (frozen corpus, golden
questions, batch eval run) is complete — Phase 2 baseline inspection is
next.

---

# Phase 1 - Retrieval Evaluation Foundation — Complete

## Purpose

Before improving retrieval, Gester needs a way to measure whether retrieval is actually improving.

This phase creates a repeatable evaluation harness for testing search quality across known queries, expected articles, and expected chunks.

## Milestone 1.1 - Freeze an Evaluation Corpus — Complete

_Done: `POST /eval/corpora` snapshots current articles and chunks to
`data/eval/corpora/{version}.json` with chunking/embedding config,
ingestion/embedding timestamps, article metadata, and ID lists.
`GET /eval/corpora` lists snapshots; `GET /eval/corpora/{version}` loads
one. Default version name: `baseline_YYYY_MM_DD`._

### Purpose

Create a stable corpus snapshot so retrieval experiments can be compared fairly.

### Implementation

* Select the current set of articles and chunks as the first evaluation corpus.
* Assign a corpus version name, such as:

```text
baseline_2026_06_28
```

* Store enough metadata to reproduce or identify the corpus:

  * Article IDs
  * Chunk IDs
  * Source names
  * Article titles
  * URLs
  * Chunking strategy
  * Embedding model
  * Embedding date
  * Ingestion date

### Done When

* A fixed evaluation corpus can be selected.
* Retrieval tests can be run repeatedly against the same corpus.
* New ingestion does not silently change evaluation results.
* Corpus version is included in evaluation output.

### Evaluation

This milestone is not judged by retrieval quality yet.

It is judged by repeatability.

The same query against the same corpus and configuration should produce the same or explainably similar results.

---

## Milestone 1.2 - Create a Golden Question Set — Complete

_Done: `config/eval/golden_questions.yaml` holds 30 curated questions with
expected article IDs, categories (direct lookup, concept, proper noun,
near miss, negative), and optional terms/notes. `GET /eval/questions`
loads the set; `GET /eval/questions/validate?corpus_version=...` checks
IDs against a frozen corpus._

### Purpose

Create a manually curated set of questions where the expected source material is known.

### Implementation

Start with 25–50 test questions.

Include several types of questions:

#### Direct lookup questions

Questions that should retrieve one obvious article or chunk.

```text
What does the article say about running local LLMs on consumer hardware?
```

#### Concept questions

Questions that may require multiple chunks or articles.

```text
What are the arguments for using local models instead of cloud-hosted models?
```

#### Proper noun questions

Questions involving exact names, libraries, models, or products.

```text
What does the corpus say about Ollama?
```

#### Near-miss questions

Questions where semantically similar but wrong results are likely.

```text
What are the tradeoffs of local embedding models?
```

#### Negative questions

Questions where the correct result may be no strong match.

```text
What does the corpus say about Kubernetes autoscaling?
```

### Suggested Data Model

```python
class RetrievalEvalQuestion(BaseModel):
    id: str
    question: str
    expected_article_ids: list[int]
    expected_chunk_ids: list[int] = []
    expected_terms: list[str] = []
    notes: str | None = None
```

### Done When

* At least 25 golden questions exist.
* Each question has expected article IDs or expected chunk IDs.
* Questions cover multiple retrieval scenarios.
* Questions are stored in a durable format such as JSON, YAML, or SQLite.

### Evaluation

The golden question set should be reviewed manually.

A question is useful if a human can say:

```text
For this question, these are the sources I expected Gester to retrieve.
```

---

## Milestone 1.3 - Build the Retrieval Evaluation Command — Complete

### Purpose

Create a command that runs retrieval tests and saves results.

### Implementation

Run retrieval evaluation over HTTP:

```bash
POST /eval/retrieval/run?corpus_version=baseline_2026_06_28
```

Optional query params: `limit`, `min_score`, `dedupe_by_article`, `question_ids` (repeatable).

Eval defaults live in `config/settings.yaml` under `eval.retrieval` (`limit=10`,
`min_score=0`, `dedupe_by_article=false`, `recall_k_values: [3, 5, 10]`).

Saved runs:

```bash
GET /eval/retrieval/runs
GET /eval/retrieval/runs/{run_id}
```

Reports are written to `data/eval/runs/{run_id}.json`.

The workflow:

* Load the golden question set
* Run each question through the retrieval pipeline
* Save the top-k retrieved chunks
* Compare actual results against expected results
* Report metrics
* Save a detailed inspection file

### Retrieval Output Fields

For each retrieved result, save:

```text
question_id
query
rank
score
chunk_id
article_id
article_title
source_name
source_url
chunk_text_preview
full_chunk_text
retrieval_strategy
corpus_version
embedding_model
chunking_strategy
```

### Done When

_Done: `POST /eval/retrieval/run` runs all golden questions against a frozen
corpus using eval defaults from `config/settings.yaml`; reports Recall@3/5/10,
MRR, and expected-article/chunk flags per question; saves detailed JSON reports
to `data/eval/runs/`. `GET /eval/retrieval/runs` and `GET /eval/retrieval/runs/{run_id}`
load saved runs._

* The eval command runs all golden questions.
* Results are saved to disk.
* Each result includes rank, score, source, article, chunk, and text preview.
* The command reports summary metrics.

### Evaluation Metrics

Start with:

```text
Recall@3
Recall@5
Recall@10
MRR
Expected article found: yes/no
Expected chunk found: yes/no
```

Definitions:

```text
Recall@5:
Did one of the expected articles or chunks appear in the top 5?

MRR:
How high did the first correct result appear?
```

Example output:

```text
Question: What does the corpus say about Ollama?

Expected article IDs: [17]

Top 5:
1. article 17 | chunk 82 | score .78 | correct
2. article 22 | chunk 91 | score .71 | incorrect
3. article 17 | chunk 83 | score .69 | correct
4. article 40 | chunk 12 | score .64 | incorrect
5. article 61 | chunk 33 | score .59 | incorrect

Recall@5: pass
MRR: 1.0
```

---

# Phase 2 - Baseline Retrieval Inspection — In progress

## Purpose

Understand how the current retrieval system fails before adding new retrieval techniques.

This phase uses the evaluation harness to classify retrieval failures.

## Milestone 2.1 - Add Search Debug Output — In progress

_Done: `GET /search` returns score, chunk ID, source item ID, title, URL,
and full chunk text; `GET /items/{id}/chunks` lists stored chunks.
Remaining: no dedicated debug export (rank, published date, chunk length,
saved inspection file); no side-by-side retrieval-setting comparison._

### Purpose

Make every search result inspectable.

### Implementation

For every query, display or save:

```text
query
rank
score
article title
source
published date
chunk id
article id
chunk length
text preview
full chunk text
```

### Done When

* Search results can be inspected without using the database manually.
* The user can see why a chunk was returned.
* The output is readable enough for manual debugging.

### Evaluation

A search result is debuggable if a human can quickly answer:

```text
Was this the right article?
Was this the right chunk?
Was the score reasonable?
Did a duplicate crowd out better results?
Was the chunk missing useful context?
```

---

## Milestone 2.2 - Classify Retrieval Failures — Not started

### Purpose

Create a controlled vocabulary for describing why retrieval failed.

### Failure Categories

Use categories such as:

```text
wrong_topic_retrieved
right_article_wrong_chunk
right_chunk_ranked_too_low
duplicate_chunks_crowded_results
chunk_lacks_context
query_uses_different_language_than_source
chunk_too_small
chunk_too_large
source_text_noisy
embedding_model_weak
keyword_match_needed
multi_article_answer_needed
no_good_answer_in_corpus
```

### Implementation

For each failed golden question, manually assign one or more failure categories.

### Done When

* Failed queries can be labeled.
* The most common retrieval failure modes are visible.
* Future improvements can be tied to specific failure types.

### Evaluation

This milestone succeeds when Gester can answer:

```text
What kind of bad is our retrieval?
```

Not just:

```text
Is retrieval bad?
```

---

# Phase 3 - Source Text Quality — In progress

## Purpose

Improve the quality of stored source text before tuning retrieval algorithms.

Bad source text creates bad chunks, bad embeddings, bad search results, and bad answers.

## Milestone 3.1 - Inspect Cleaned Article Text — Not started

### Purpose

Verify that article text stored in Gester is actually useful.

### Things to Check

Inspect for:

```text
cookie banners
navigation text
newsletter blocks
related article sections
duplicated footer text
missing article body
broken formatting
HTML artifacts
advertising text
author bios mixed into article body
```

### Done When

* At least 20 stored articles are manually inspected.
* Common extraction issues are documented.
* Each article keeps source URL and metadata.

### Evaluation

For each inspected article, assign a quality label:

```text
clean
minor_noise
major_noise
failed_extraction
```

Track:

```text
percent_clean
percent_minor_noise
percent_major_noise
percent_failed_extraction
```

---

## Milestone 3.2 - Improve Article Cleaning — In progress

_Done: Trafilatura-based extraction in `ArticleExtractor`; RSS ingestion
falls back to feed summary when extraction fails. Remaining: no separate
`raw_html` / `cleaned_text` storage, no extractor version metadata, no
re-cleaning pipeline._

### Purpose

Improve retrieval by improving the text being indexed.

### Implementation

Store both:

```text
raw_html
cleaned_text
```

Add metadata:

```text
extractor_name
extractor_version
extracted_at
```

### Done When

* Article body extraction is more reliable.
* Cleaned text excludes obvious site chrome.
* Extraction version is stored.
* Re-cleaning articles is possible.

### Evaluation

Re-run the retrieval eval.

Compare before and after:

```text
Recall@5
Recall@10
failure category counts
number of noisy chunks retrieved
```

Expected improvement:

```text
Fewer retrieval results caused by source_text_noisy.
```

---

# Phase 4 - Chunking Experiments — In progress

## Purpose

Learn how chunk design affects retrieval quality.

Chunking is one of the most important parts of RAG because chunks are the atomic evidence units used by retrieval and answer generation.

## Milestone 4.1 - Baseline Current Chunking — In progress

_Done: `TextChunkingService` (1000 chars / 200 overlap from
`config/settings.yaml`); chunk stats derivable from stored chunks.
Remaining: baseline retrieval metrics and failure categories not recorded
(no eval harness yet)._

### Purpose

Measure the current chunking strategy before changing it.

### Implementation

Record:

```text
chunk size
chunk overlap
chunking method
average chunk length
min chunk length
max chunk length
number of chunks per article
```

### Done When

* Current chunking strategy is documented.
* Current retrieval metrics are recorded.
* Current failure categories are recorded.

### Evaluation

This is the baseline for future chunking experiments.

---

## Milestone 4.2 - Fixed-Size Chunking Experiment — In progress

_Done: chunk size and overlap configurable via settings; `POST
/process/chunks/reset` and `POST /process/chunks` support re-chunking;
`POST /process/embeddings?rebuild=true` re-embeds. Remaining: no eval
command to compare chunking configurations._

### Purpose

Test several fixed-size chunk configurations.

### Experiments

Try:

```text
400 tokens / 50 overlap
600 tokens / 100 overlap
800 tokens / 100 overlap
1000 tokens / 150 overlap
```

### Done When

* Multiple chunking configurations can be generated.
* Each configuration can be embedded and searched.
* Evaluation can compare one chunking strategy against another.

### Evaluation

For each strategy, record:

```text
Recall@3
Recall@5
Recall@10
MRR
average chunks per article
duplicate rate in top 10
right_article_wrong_chunk failures
chunk_lacks_context failures
```

Expected learning:

```text
Smaller chunks may improve precision but lose context.
Larger chunks may improve context but reduce focus.
Overlap may help continuity but increase duplicates.
```

---

## Milestone 4.3 - Structure-Aware Chunking Experiment — Not started

### Purpose

Test chunks based on article structure rather than raw token counts.

### Implementation

Try to preserve:

```text
headings
paragraphs
lists
code blocks
section boundaries
```

### Done When

* Chunking avoids splitting in the middle of obvious semantic units.
* Section headings are retained when available.
* Chunks remain linked to source articles.

### Evaluation

Compare against fixed-size chunking.

Track:

```text
Recall@5
MRR
manual readability
chunk_lacks_context failures
right_article_wrong_chunk failures
```

Expected improvement:

```text
Chunks should be easier to understand and more useful as evidence.
```

---

# Phase 5 - Metadata-Enriched Chunks — In progress

## Purpose

Add contextual headers to chunks so retrieval has more information than isolated body text.

Many chunks are ambiguous by themselves. Metadata-enriched chunks help the embedding model and keyword search understand what the chunk is about.

## Milestone 5.1 - Add Chunk Headers — In progress

_Done: `ChunkEmbeddingService` builds embedding text from title + URL +
chunk body without modifying stored chunk text; answers cite original
chunk content. Remaining: embedding text is not persisted as a separate
field; headers omit source name, published date, and section; no A/B eval
against raw-chunk embeddings._

### Purpose

Create an `embedding_text` field that includes metadata plus chunk body.

### Example

```text
Title: Local LLMs Are Getting Good Enough for Coding Agents
Source: XDA Developers
Published: 2026-06-21
Section: Running models locally

Chunk:
Open models have crossed the point where they are good enough for daily work with a coding agent...
```

### Implementation

Store separately:

```text
raw_chunk_text
embedding_text
prompt_context_text
metadata
```

Do not overwrite the original chunk text.

### Done When

* Each chunk has a generated embedding text field.
* The original chunk text remains unchanged.
* Embeddings are generated from the enriched text.
* Final answers can still cite the original source material.

### Evaluation

Compare:

```text
raw chunk embeddings
vs
metadata-enriched chunk embeddings
```

Track:

```text
Recall@5
MRR
chunk_lacks_context failures
wrong_topic_retrieved failures
```

Expected improvement:

```text
Queries involving article topic, source, or section should improve.
```

---

## Milestone 5.2 - Add Keywords and Entities — Not started

### Purpose

Extract useful terms from articles and chunks for search.

### Keywords

Examples:

```text
local LLM
Ollama
Qwen
Gemma
Cursor
LangGraph
BM25
SQLite FTS5
vector database
local embeddings
```

### Entities

Examples:

```text
OpenAI
Anthropic
Microsoft
NVIDIA
Cursor
Ollama
LangChain
LlamaIndex
```

### Implementation

Store:

```python
class ChunkMetadata(BaseModel):
    article_id: int
    source_name: str
    title: str
    section_heading: str | None
    published_at: datetime | None
    keywords: list[str]
    entities: list[str]
```

Use keywords in:

```text
embedding headers, lightly
BM25/full-text search, heavily
metadata display/debugging
```

### Done When

* Articles have generated keywords.
* Chunks have generated or inherited keywords.
* Keywords are stored as structured metadata.
* Keywords are included in search indexing.

### Evaluation

Compare retrieval performance on proper noun and technical term questions.

Track:

```text
Recall@5 for proper noun questions
BM25 hit rate after BM25 is added
wrong_near_match failures
```

Expected improvement:

```text
Queries involving exact tools, model names, libraries, and acronyms should improve.
```

---

# Phase 6 - Article Summaries and Hierarchical Retrieval — Not started

## Purpose

Use article summaries to help identify relevant articles before retrieving exact chunks.

Summaries should be used for discovery and routing, not as final evidence.

```text
Summary = helps find likely articles
Chunk = evidence for final answer
```

## Milestone 6.1 - Generate Article Summaries — Not started

### Purpose

Create a concise representation of each article.

### Summary Requirements

Each article summary should include:

```text
main topic
key claims
important tools/models/products
why the article matters
notable caveats
```

Suggested length:

```text
5–8 sentences
```

### Data Model

```python
class ArticleSummary(BaseModel):
    article_id: int
    summary_text: str
    keywords: list[str]
    entities: list[str]
    generated_by_model: str
    generated_at: datetime
    summary_version: str
```

### Done When

* Each article has a stored summary.
* Summaries are generated locally.
* Summaries preserve article ID and source link.
* Summaries can be regenerated when the summary prompt changes.

### Evaluation

Manually inspect a sample of summaries.

Rate each summary:

```text
accurate
mostly_accurate
missing_key_details
misleading
failed
```

Track:

```text
summary_accuracy_rate
missing_key_details_rate
misleading_summary_rate
```

---

## Milestone 6.2 - Create Article Summary Search — Not started

### Purpose

Create a separate retrieval path over article summaries.

### Implementation

Create an article summary vector index.

Search flow:

```text
query
↓
search article summaries
↓
identify likely articles
↓
retrieve chunks from those articles
```

### Done When

* Article summaries can be searched independently.
* Search results return article IDs.
* Summary search can be compared against direct chunk search.

### Evaluation

Create article-level metrics:

```text
Article Recall@3
Article Recall@5
Article Recall@10
Article MRR
```

Compare:

```text
direct chunk retrieval
vs
summary retrieval
```

Expected improvement:

```text
Broad conceptual questions should identify better source articles.
```

---

## Milestone 6.3 - Summary-Guided Chunk Retrieval — Not started

### Purpose

Use article summary hits to guide chunk retrieval.

### Retrieval Flow

```text
1. Search article summaries
2. Select top N likely articles
3. Search chunks within those articles
4. Merge with normal chunk search results
5. Rank final candidates
```

### Done When

* Summary-discovered articles influence final retrieval.
* Final answer context still uses original chunks.
* Summary text is not treated as primary evidence unless explicitly allowed.

### Evaluation

Track:

```text
Recall@5
Recall@10
Article Recall@5
multi_article_answer_needed failures
wrong_topic_retrieved failures
```

Expected improvement:

```text
Broad questions should retrieve better article sets.
```

---

# Phase 7 - BM25 / Keyword Search — Not started

## Purpose

Add lexical search to complement vector search.

Vector search finds semantic similarity.

BM25 finds exact term matches.

Both are useful.

## Milestone 7.1 - Add Local Full-Text Index — Not started

### Purpose

Create a local keyword search index.

### Local-First Options

Possible implementations:

```text
SQLite FTS5
Whoosh
Tantivy
Lucene-based local index
```

If Gester already uses SQLite, start with SQLite FTS5.

### Searchable Fields

Index:

```text
title
source_name
section_heading
keywords
entities
chunk_text
```

### Example

```sql
CREATE VIRTUAL TABLE chunk_fts USING fts5(
    title,
    source_name,
    section_heading,
    keywords,
    entities,
    chunk_text
);
```

### Done When

* Chunks are inserted into a full-text index.
* Keyword search can return ranked chunk results.
* Results include article and source metadata.

### Evaluation

Create a subset of proper noun queries.

Examples:

```text
Ollama
Qwen
Gemma
Cursor
LangGraph
BM25
SQLite FTS5
RTX 5090
```

Track:

```text
BM25 Recall@5
BM25 Recall@10
proper noun Recall@5
```

Expected improvement:

```text
Exact tool, model, and product queries should improve.
```

---

## Milestone 7.2 - Add Field Boosting — Not started

### Purpose

Make matches in important fields count more than matches in body text.

### Suggested Boosts

```text
title: 3.0
keywords: 2.0
entities: 2.0
section_heading: 1.5
chunk_text: 1.0
```

### Done When

* Title matches can rank higher than body-only matches.
* Keyword/entity matches influence ranking.
* Boost weights are configurable.

### Evaluation

Compare BM25 search:

```text
without field boosting
vs
with field boosting
```

Track:

```text
MRR
Recall@3
proper noun Recall@5
manual ranking quality
```

Expected improvement:

```text
Important title and keyword matches should move higher in results.
```

---

# Phase 8 - Hybrid Retrieval — In progress

## Purpose

Combine vector search, BM25 search, and summary-guided retrieval into a stronger candidate generation pipeline.

## Milestone 8.1 - Merge Vector and BM25 Results — Not started

### Purpose

Create a hybrid retriever.

### Retrieval Flow

```text
1. Run vector search
2. Run BM25 search
3. Normalize scores
4. Merge results
5. Deduplicate by chunk ID
6. Group by article
7. Return final top-k candidates
```

### Possible Scoring

```text
hybrid_score = vector_weight * vector_score + bm25_weight * bm25_score
```

Start with configurable weights:

```text
80 / 20
65 / 35
50 / 50
35 / 65
```

### Done When

* Vector and BM25 results can be combined.
* Hybrid weights are configurable.
* Results preserve source metadata.
* The retrieval eval can run against hybrid search.

### Evaluation

Compare:

```text
vector only
BM25 only
hybrid 80/20
hybrid 65/35
hybrid 50/50
hybrid 35/65
```

Track:

```text
Recall@3
Recall@5
Recall@10
MRR
proper noun Recall@5
concept question Recall@5
negative question false positive rate
```

Expected improvement:

```text
Hybrid retrieval should outperform vector-only retrieval across the full eval set.
```

---

## Milestone 8.2 - Add Article Grouping and Deduplication — Complete

_Done: `SearchService` over-fetches then deduplicates by source item ID
(`dedupe_by_article`, default true); configurable via settings and
`/search` query params._

### Purpose

Prevent search results from being dominated by many chunks from the same article.

### Implementation

Support configurable modes:

```text
raw_chunk_mode
article_diverse_mode
grouped_article_mode
```

Example grouped behavior:

```text
retrieve top 50 raw candidates
group by article
keep best 1–3 chunks per article
return top article groups
```

### Done When

* Duplicate-heavy results can be reduced.
* The number of chunks per article is configurable.
* The system can preserve multiple chunks from the same article when useful.

### Evaluation

Track:

```text
duplicate article rate in top 10
Recall@5
Article Recall@5
multi_article_answer completeness
manual result diversity
```

Expected improvement:

```text
Results should include more useful source diversity without losing important repeated evidence.
```

---

# Phase 9 - Parent-Child Retrieval — Not started

## Purpose

Search over small focused chunks while sending larger surrounding context to the answer model.

This helps balance precision and context.

## Milestone 9.1 - Add Parent-Child Chunk Structure — Not started

### Purpose

Link small retrieval chunks to larger parent sections or article spans.

### Model

```text
article
  parent section
    child chunk
    child chunk
    child chunk
```

Search uses child chunks.

Answer context can include:

```text
matched child chunk
neighboring chunks
parent section
```

### Done When

* Child chunks are searchable.
* Each child chunk links to a parent context.
* Retrieval can expand a hit into surrounding context.

### Evaluation

Compare:

```text
small chunks only
large chunks only
small chunk retrieval + parent context
```

Track:

```text
Recall@5
answer completeness
right_article_wrong_chunk failures
chunk_lacks_context failures
context token usage
```

Expected improvement:

```text
Search remains precise while answers get better supporting context.
```

---

# Phase 10 - Local Reranking — Not started

## Purpose

Add a second-stage ranking step that decides which retrieved candidates actually answer the query.

Candidate generation asks:

```text
What might be relevant?
```

Reranking asks:

```text
What actually answers this question?
```

## Milestone 10.1 - Add Local Reranker — Not started

### Purpose

Use a local reranking model to reorder top candidates.

### Retrieval Flow

```text
1. Hybrid search retrieves top 30–50 candidates
2. Candidates are deduped/grouped
3. Local reranker scores query + chunk pairs
4. Top 5–8 chunks are selected for answer context
```

### Done When

* A local reranker can score query/chunk pairs.
* Reranking can be turned on/off by configuration.
* Evaluation can compare retrieval with and without reranking.

### Evaluation

Compare:

```text
hybrid without reranker
hybrid with reranker
```

Track:

```text
MRR
Recall@3
Recall@5
manual ranking quality
answer context usefulness
```

Expected improvement:

```text
Correct chunks should move higher in the ranking.
```

---

# Phase 11 - Query Rewriting and Expansion — Not started

## Purpose

Improve retrieval when the user’s wording does not match source wording.

This should be added after baseline retrieval, BM25, hybrid retrieval, and reranking are measurable.

## Milestone 11.1 - Add Query Expansion — Not started

### Purpose

Generate alternate search terms for the same user question.

### Example

Original query:

```text
How do local models compare to hosted models?
```

Expanded query terms:

```text
local LLM
on-device inference
self-hosted model
cloud model
hosted AI service
private inference
```

### Done When

* The system can generate local query expansions.
* Expanded terms can be inspected.
* Retrieval can run with and without expansion.

### Evaluation

Track:

```text
Recall@5
Recall@10
wrong_topic_retrieved failures
query_uses_different_language_than_source failures
false positive rate
```

Expected improvement:

```text
Queries with vocabulary mismatch should improve.
```

---

## Milestone 11.2 - Add Multi-Query Retrieval — Not started

### Purpose

Generate multiple versions of the query and merge results.

### Retrieval Flow

```text
original query
↓
generate 3–5 alternate queries
↓
run retrieval for each query
↓
merge results
↓
dedupe/group
↓
rerank
```

### Done When

* Multi-query retrieval is available as a configurable strategy.
* Generated queries are logged.
* Results can be compared with single-query retrieval.

### Evaluation

Track:

```text
Recall@10
MRR
duplicate rate
false positive rate
manual result quality
```

Expected learning:

```text
Multi-query retrieval can improve recall but may introduce noise.
```

---

# Phase 12 - Context Assembly — In progress

## Purpose

Improve how retrieved chunks are turned into LLM context.

Good retrieval can still produce bad answers if context assembly is poor.

## Milestone 12.1 - Source Block Formatting — In progress

_Done: `AnswerService._build_context` formats `[Source N]` blocks with
title, URL, and chunk text; prompt instructs inline `[Source N]`
citations. Remaining: published date and chunk ID not included in context
blocks._

### Purpose

Send structured source blocks to the answer model.

### Example

```text
[Source 1]
Article: Local LLMs Are Getting Good Enough for Coding Agents
Source: XDA Developers
URL: https://example.com/article
Published: 2026-06-21
Chunk ID: 82

Text:
Open models have crossed the point where they are good enough for daily work with a coding agent...
```

### Done When

* Every context chunk has a source ID.
* Source metadata is included.
* Chunks are clearly separated.
* The answer model can cite source IDs.

### Evaluation

Track:

```text
citation correctness
answer grounding
answer completeness
hallucination rate
```

---

## Milestone 12.2 - Context Packing Strategy — In progress

_Done: top-k article-diverse chunks via deduplicated search results;
timing logged in `/ask` response. Remaining: context strategy not
configurable; no context token usage logging; no comparison of packing
strategies._

### Purpose

Control which retrieved chunks are sent to the LLM.

### Strategies to Compare

```text
top-k raw chunks
top-k article-diverse chunks
grouped article context
parent-child expanded context
reranked top-k context
```

### Done When

* Context strategy is configurable.
* Context token usage is logged.
* The same question can be answered using different context strategies.

### Evaluation

Track:

```text
answer completeness
groundedness
citation correctness
context token count
irrelevant context count
```

Expected learning:

```text
More context is not always better.
```

---

# Phase 13 - Grounded Answer Generation — In progress

## Purpose

Generate answers that are explicitly grounded in retrieved source material.

## Milestone 13.1 - Add Grounded Answer Prompt — Complete

_Done: `AnswerService` prompt requires sources-only answers, inline
`[Source N]` citations, explicit insufficient-evidence response, and no
outside knowledge; `/ask` returns source metadata mapped to chunk and
article IDs; direct-text-evidence gate reduces ungrounded generation._

### Purpose

Make the answer model use only retrieved evidence.

### Prompt Requirements

The prompt should instruct the model to:

```text
answer only from provided sources
cite source IDs
say when evidence is insufficient
avoid using outside knowledge
avoid inventing citations
separate supported claims from uncertainty
```

### Done When

* Answers cite retrieved sources.
* The model refuses or qualifies answers when evidence is weak.
* Source IDs map back to original articles/chunks.

### Evaluation

For each answer, judge:

```text
Did it answer the question?
Did it use the right source?
Did it invent unsupported claims?
Did it cite correctly?
Did it ignore important evidence?
Was it too vague?
Was it too long?
```

Suggested labels:

```text
grounded
mostly_grounded
partially_grounded
ungrounded
```

---

## Milestone 13.2 - Answer Evaluation Set — Not started

### Purpose

Evaluate generated answers separately from retrieval.

### Data Model

```python
class AnswerEvalResult(BaseModel):
    question_id: str
    answer: str
    cited_source_ids: list[str]
    retrieval_passed: bool
    grounded: bool
    complete: bool
    citation_correct: bool
    notes: str | None = None
```

### Done When

* Retrieval evaluation and answer evaluation are separate.
* An answer can fail even if retrieval passed.
* Retrieval can fail even if the answer sounds plausible.

### Evaluation Metrics

Track:

```text
grounded answer rate
citation correctness rate
complete answer rate
unsupported claim rate
insufficient evidence handling rate
```

---

# Phase 14 - Citation Validation — Not started

## Purpose

Ensure that cited sources actually support the answer.

## Milestone 14.1 - Validate Cited Source IDs — Not started

### Purpose

Make sure every citation maps to retrieved source material.

### Done When

* Every cited source ID exists in the context.
* Every citation maps back to article and chunk metadata.
* Invalid citations are detected.

### Evaluation

Track:

```text
invalid citation count
missing citation count
citation maps to retrieved context: yes/no
```

---

## Milestone 14.2 - Manual Citation Support Review — Not started

### Purpose

Check whether cited sources actually support answer claims.

### Evaluation Labels

For each cited claim:

```text
fully_supported
partially_supported
not_supported
source_misused
```

### Done When

* A sample of answers has citation support reviewed.
* Unsupported citation patterns are documented.
* Prompt/context changes can be tested against citation quality.

---

# Phase 15 - Regression Testing — Not started

## Purpose

Prevent future retrieval improvements from breaking previously working queries.

## Milestone 15.1 - Add Retrieval Regression Tests — Not started

### Purpose

Convert successful golden questions into regression tests.

### Example Regression Rule

```text
Query:
What does the corpus say about local LLMs for coding agents?

Expected:
- Article 17 appears in top 5
- At least one chunk from Article 17 appears in final context
- No more than 3 chunks from the same article appear before dedupe
```

### Done When

* Important queries have pass/fail rules.
* Retrieval changes can be tested before being accepted.
* Failures are visible.

### Evaluation

A retrieval change should not be accepted unless it:

```text
improves target metrics
or fixes known failures
without causing unacceptable regressions
```

---

# Phase 16 - Experiment Logging — Not started

## Purpose

Maintain a record of retrieval experiments and results.

## Milestone 16.1 - Create Retrieval Experiment Log — Not started

### Purpose

Document what changed, why it changed, and whether it helped.

### Suggested Format

```markdown
# Retrieval Experiment Log

## 2026-06-28 - Baseline Vector Retrieval

Corpus: baseline_2026_06_28
Embedding model: ...
Chunking strategy: ...
Top K: 10

Results:
- Recall@3:
- Recall@5:
- Recall@10:
- MRR:

Observations:
- Proper noun queries are weak.
- Duplicate chunks crowd out diverse results.
- Some chunks lack article context.

Decision:
Keep as baseline.
```

### Done When

* Every major retrieval experiment is documented.
* Metrics are recorded before and after.
* Decisions are explicit.

---

# Phase 17 - Personalization Signals — Not started

## Purpose

Eventually use user behavior to improve ranking without hiding baseline retrieval problems.

This should come after retrieval is already reasonably strong.

## Milestone 17.1 - Track User Engagement — Not started

### Purpose

Record interactions that may later influence ranking.

### Signals

```text
article opened
article saved
search submitted
result clicked
answer copied
source expanded
thumbs up/down
```

### Done When

* Engagement events are stored locally.
* Events include article/chunk IDs where relevant.
* Events do not affect ranking yet.

### Evaluation

This milestone is judged by data quality, not ranking improvement.

---

## Milestone 17.2 - Personalized Ranking Experiment — Not started

### Purpose

Test whether user behavior can improve result ordering.

### Possible Boosts

```text
preferred sources
frequently opened topics
saved articles
recently searched concepts
```

### Done When

* Personalization can be enabled or disabled.
* Personalized ranking is compared against non-personalized ranking.
* Ranking changes are explainable.

### Evaluation

Track:

```text
click-through rate
manual relevance rating
personalized vs baseline Recall@5
source diversity
overfitting to old interests
```

---

# Retrieval Strategy Comparison Matrix

Use this matrix to compare each major retrieval strategy.

| Strategy                 | Purpose                         | Best For                      | Main Risk               | Key Metrics                    |
| ------------------------ | ------------------------------- | ----------------------------- | ----------------------- | ------------------------------ |
| Vector search            | Semantic similarity             | Conceptual questions          | Vague near-matches      | Recall@K, MRR                  |
| BM25                     | Exact term search               | Proper nouns, tools, acronyms | Misses semantic matches | Proper noun Recall@K           |
| Metadata-enriched chunks | Adds context to chunks          | Ambiguous chunks              | Metadata pollution      | Recall@5, failure labels       |
| Article summaries        | Article discovery               | Broad questions               | Lossy summaries         | Article Recall@K               |
| Hybrid retrieval         | Combines semantic + lexical     | General quality               | Score tuning complexity | Recall@K, MRR                  |
| Parent-child retrieval   | Precise search + richer context | Better answer context         | More token usage        | Answer completeness            |
| Reranking                | Reorders candidates             | Top result quality            | Slower pipeline         | MRR, Recall@3                  |
| Query expansion          | Vocabulary mismatch             | Different wording             | More false positives    | Recall@10, false positive rate |

---

# Standard Evaluation Metrics

## Retrieval Metrics

Use these for search quality:

```text
Recall@3
Recall@5
Recall@10
MRR
Article Recall@K
Chunk Recall@K
duplicate article rate
false positive rate
```

## Context Metrics

Use these for context assembly quality:

```text
right evidence included
irrelevant context count
context token count
source diversity
article grouping quality
```

## Answer Metrics

Use these for final RAG answer quality:

```text
groundedness
citation correctness
answer completeness
unsupported claim rate
insufficient evidence handling
```

## Failure Categories

Use these for diagnosis:

```text
wrong_topic_retrieved
right_article_wrong_chunk
right_chunk_ranked_too_low
duplicate_chunks_crowded_results
chunk_lacks_context
query_uses_different_language_than_source
chunk_too_small
chunk_too_large
source_text_noisy
embedding_model_weak
keyword_match_needed
multi_article_answer_needed
no_good_answer_in_corpus
```

---

# Recommended Implementation Order

## Immediate Next Steps

```text
1. Freeze the current corpus                              — Complete
2. Create 25–50 golden questions                          — Complete
3. Build eval-retrieval command                           — Not started
4. Save top-k retrieval results                           — Not started
5. Add failure classification                           — Not started
6. Inspect source text quality                            — Not started
```

## Next Retrieval Improvements

```text
7. Test chunking strategies                               — In progress
8. Add metadata-enriched chunk headers                    — In progress
9. Generate article summaries                             — Not started
10. Add article summary search                            — Not started
11. Add BM25 / keyword search                             — Not started
12. Add hybrid retrieval                                  — Not started
13. Add article grouping and dedupe                       — Complete
14. Add parent-child retrieval                            — Not started
15. Add local reranking                                   — Not started
```

## Answer Quality Work

```text
16. Improve context assembly                              — In progress
17. Add grounded answer prompt                            — Complete
18. Evaluate answer quality separately                    — Not started
19. Validate citations                                    — Not started
20. Add regression tests                                  — Not started
```

## Later Learning Work

```text
21. Add query expansion                                   — Not started
22. Add multi-query retrieval                             — Not started
23. Track engagement                                      — Not started
24. Test personalized ranking                             — Not started
25. Add higher-level research workflows                   — Not started
```

---

# Version 1 Retrieval Success Criteria

Gester’s retrieval system should be considered meaningfully improved when:

```text
- A fixed evaluation corpus exists                              — Complete
- A golden question set exists                                    — Complete
- Retrieval quality can be measured repeatedly                    — Not started
- Retrieval failures can be classified                            — Not started
- Chunking strategies have been compared                          — In progress
- Metadata-enriched chunks have been tested                       — In progress
- Article summaries support article discovery                     — Not started
- BM25 keyword search works locally                               — Not started
- Hybrid retrieval beats vector-only retrieval                    — Not started
- Duplicate-heavy results are controlled                          — Complete
- Retrieved context includes source metadata                      — Complete
- Answers cite source material                                    — Complete
- Answer evaluation is separate from retrieval evaluation         — Not started
- Regression tests protect known-good queries                     — Not started
```

The goal is not to claim the system is perfect.

The goal is to make retrieval quality visible, measurable, and improvable.
