from pydantic import BaseModel, ConfigDict

from gester.domain.models.retrieval_eval_run import (
    RetrievalEvalQuestionResult,
    RetrievalEvalRetrievedResult,
    RetrievalEvalRun,
    RetrievalEvalSettingsSnapshot,
    RetrievalEvalSummaryMetrics,
)


class RetrievalEvalRetrievedResultResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: str
    query: str
    rank: int
    score: float
    chunk_id: int
    article_id: int
    article_title: str
    source_name: str
    source_url: str | None
    chunk_text_preview: str
    full_chunk_text: str
    retrieval_strategy: str
    corpus_version: str
    embedding_model: str
    chunking_strategy: str
    is_expected: bool

    @classmethod
    def from_result(
        cls, result: RetrievalEvalRetrievedResult
    ) -> "RetrievalEvalRetrievedResultResponse":
        return cls(**result.model_dump())


class RetrievalEvalQuestionMetricsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recall_at_k: dict[str, bool | None]
    mrr: float | None
    expected_article_found: bool
    expected_chunk_found: bool
    first_expected_rank: int | None
    max_score: float | None


class RetrievalEvalQuestionResultResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: str
    question: str
    category: str
    expected_article_ids: list[int]
    expected_chunk_ids: list[int]
    metrics: RetrievalEvalQuestionMetricsResponse
    retrieved_results: list[RetrievalEvalRetrievedResultResponse]

    @classmethod
    def from_result(
        cls, result: RetrievalEvalQuestionResult
    ) -> "RetrievalEvalQuestionResultResponse":
        return cls(
            question_id=result.question_id,
            question=result.question,
            category=result.category.value,
            expected_article_ids=result.expected_article_ids,
            expected_chunk_ids=result.expected_chunk_ids,
            metrics=RetrievalEvalQuestionMetricsResponse(**result.metrics.model_dump()),
            retrieved_results=[
                RetrievalEvalRetrievedResultResponse.from_result(retrieved_result)
                for retrieved_result in result.retrieved_results
            ],
        )


class RetrievalEvalSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_count: int
    mean_mrr: float | None
    recall_at_k: dict[str, float | None]
    expected_article_found_rate: float
    expected_chunk_found_rate: float
    by_category: dict[str, dict[str, float | int | None]]

    @classmethod
    def from_summary(cls, summary: RetrievalEvalSummaryMetrics) -> "RetrievalEvalSummaryResponse":
        by_category = {
            category: {
                "question_count": metrics.question_count,
                "mean_mrr": metrics.mean_mrr,
                **{f"recall_at_{k}": v for k, v in metrics.recall_at_k.items()},
            }
            for category, metrics in summary.by_category.items()
        }

        return cls(
            question_count=summary.question_count,
            mean_mrr=summary.mean_mrr,
            recall_at_k=summary.recall_at_k,
            expected_article_found_rate=summary.expected_article_found_rate,
            expected_chunk_found_rate=summary.expected_chunk_found_rate,
            by_category=by_category,
        )


class RetrievalEvalRunSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    created_at: str
    corpus_version: str
    question_set_version: str
    eval_settings: RetrievalEvalSettingsSnapshot
    embedding_model: str
    chunking_strategy: str
    summary: RetrievalEvalSummaryResponse

    @classmethod
    def from_run(cls, run: RetrievalEvalRun) -> "RetrievalEvalRunSummaryResponse":
        return cls(
            run_id=run.run_id,
            created_at=run.created_at.isoformat(),
            corpus_version=run.corpus_version,
            question_set_version=run.question_set_version,
            eval_settings=run.eval_settings,
            embedding_model=run.embedding_model,
            chunking_strategy=run.chunking_strategy,
            summary=RetrievalEvalSummaryResponse.from_summary(run.summary),
        )


class RetrievalEvalRunDetailResponse(RetrievalEvalRunSummaryResponse):
    questions: list[RetrievalEvalQuestionResultResponse]

    @classmethod
    def from_run(cls, run: RetrievalEvalRun) -> "RetrievalEvalRunDetailResponse":
        return cls(
            **RetrievalEvalRunSummaryResponse.from_run(run).model_dump(),
            questions=[
                RetrievalEvalQuestionResultResponse.from_result(question)
                for question in run.questions
            ],
        )
