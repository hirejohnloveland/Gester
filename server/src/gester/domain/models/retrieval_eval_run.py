from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from gester.domain.models.retrieval_eval_question import QuestionCategory


class RetrievalEvalSettingsSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int
    min_score: float
    dedupe_by_article: bool
    recall_k_values: list[int]
    chunk_text_preview_length: int
    retrieval_strategy: str


class RetrievalEvalRetrievedResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: str
    query: str
    rank: int
    score: float
    chunk_id: int
    article_id: int
    article_title: str
    source_name: str
    source_url: str | None = None
    chunk_text_preview: str
    full_chunk_text: str
    retrieval_strategy: str
    corpus_version: str
    embedding_model: str
    chunking_strategy: str
    is_expected: bool


class RetrievalEvalQuestionMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recall_at_k: dict[str, bool | None] = Field(default_factory=dict)
    mrr: float | None = None
    expected_article_found: bool
    expected_chunk_found: bool
    first_expected_rank: int | None = None
    max_score: float | None = None


class RetrievalEvalQuestionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: str
    question: str
    category: QuestionCategory
    expected_article_ids: list[int]
    expected_chunk_ids: list[int]
    metrics: RetrievalEvalQuestionMetrics
    retrieved_results: list[RetrievalEvalRetrievedResult]


class RetrievalEvalCategoryMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_count: int
    mean_mrr: float | None = None
    recall_at_k: dict[str, float | None] = Field(default_factory=dict)


class RetrievalEvalSummaryMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_count: int
    mean_mrr: float | None = None
    recall_at_k: dict[str, float | None] = Field(default_factory=dict)
    expected_article_found_rate: float
    expected_chunk_found_rate: float
    by_category: dict[str, RetrievalEvalCategoryMetrics] = Field(default_factory=dict)


class RetrievalEvalRun(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    created_at: datetime
    corpus_version: str
    question_set_version: str
    eval_settings: RetrievalEvalSettingsSnapshot
    embedding_model: str
    chunking_strategy: str
    summary: RetrievalEvalSummaryMetrics
    questions: list[RetrievalEvalQuestionResult]
