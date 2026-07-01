from gester.domain.models.evaluation_corpus import EvaluationCorpus
from gester.domain.models.retrieval_eval_question import QuestionCategory, RetrievalEvalQuestion
from gester.domain.models.retrieval_eval_run import (
    RetrievalEvalCategoryMetrics,
    RetrievalEvalQuestionMetrics,
    RetrievalEvalQuestionResult,
    RetrievalEvalRetrievedResult,
    RetrievalEvalSummaryMetrics,
)


def format_chunking_strategy(corpus: EvaluationCorpus) -> str:
    chunking = corpus.chunking_strategy

    return f"{chunking.method}/{chunking.chunk_size}/{chunking.overlap}"


def is_expected_hit(
    article_id: int,
    chunk_id: int,
    expected_article_ids: set[int],
    expected_chunk_ids: set[int],
) -> bool:
    if chunk_id in expected_chunk_ids:
        return True

    return article_id in expected_article_ids


def compute_question_metrics(
    question: RetrievalEvalQuestion,
    retrieved_results: list[RetrievalEvalRetrievedResult],
    recall_k_values: list[int],
) -> RetrievalEvalQuestionMetrics:
    expected_article_ids = set(question.expected_article_ids)
    expected_chunk_ids = set(question.expected_chunk_ids)
    has_expected_targets = bool(expected_article_ids or expected_chunk_ids)

    first_expected_rank: int | None = None

    for result in retrieved_results:
        if is_expected_hit(
            result.article_id,
            result.chunk_id,
            expected_article_ids,
            expected_chunk_ids,
        ):
            first_expected_rank = result.rank
            break

    if has_expected_targets:
        mrr = 1.0 / first_expected_rank if first_expected_rank is not None else 0.0
    else:
        mrr = None

    recall_at_k: dict[str, bool | None] = {}

    for k in recall_k_values:
        key = str(k)

        if not has_expected_targets:
            recall_at_k[key] = None
            continue

        top_results = retrieved_results[:k]
        recall_at_k[key] = any(result.is_expected for result in top_results)

    expected_article_found = any(
        result.article_id in expected_article_ids for result in retrieved_results
    )
    expected_chunk_found = any(
        result.chunk_id in expected_chunk_ids for result in retrieved_results
    )
    max_score = max((result.score for result in retrieved_results), default=None)

    return RetrievalEvalQuestionMetrics(
        recall_at_k=recall_at_k,
        mrr=mrr,
        expected_article_found=expected_article_found,
        expected_chunk_found=expected_chunk_found,
        first_expected_rank=first_expected_rank,
        max_score=max_score,
    )


def compute_summary_metrics(
    question_results: list[RetrievalEvalQuestionResult],
    recall_k_values: list[int],
) -> RetrievalEvalSummaryMetrics:
    question_count = len(question_results)

    mrr_values = [
        result.metrics.mrr
        for result in question_results
        if result.metrics.mrr is not None
    ]
    mean_mrr = sum(mrr_values) / len(mrr_values) if mrr_values else None

    recall_at_k: dict[str, float | None] = {}

    for k in recall_k_values:
        key = str(k)
        values = [
            result.metrics.recall_at_k[key]
            for result in question_results
            if result.metrics.recall_at_k.get(key) is not None
        ]

        if not values:
            recall_at_k[key] = None
        else:
            recall_at_k[key] = sum(1 for value in values if value) / len(values)

    expected_article_found_rate = (
        sum(1 for result in question_results if result.metrics.expected_article_found)
        / question_count
        if question_count
        else 0.0
    )
    expected_chunk_found_rate = (
        sum(1 for result in question_results if result.metrics.expected_chunk_found)
        / question_count
        if question_count
        else 0.0
    )

    by_category: dict[str, RetrievalEvalCategoryMetrics] = {}

    for category in QuestionCategory:
        category_results = [
            result for result in question_results if result.category == category
        ]

        if not category_results:
            continue

        category_mrr_values = [
            result.metrics.mrr
            for result in category_results
            if result.metrics.mrr is not None
        ]
        category_recall: dict[str, float | None] = {}

        for k in recall_k_values:
            key = str(k)
            values = [
                result.metrics.recall_at_k[key]
                for result in category_results
                if result.metrics.recall_at_k.get(key) is not None
            ]

            if not values:
                category_recall[key] = None
            else:
                category_recall[key] = sum(1 for value in values if value) / len(values)

        by_category[category.value] = RetrievalEvalCategoryMetrics(
            question_count=len(category_results),
            mean_mrr=(
                sum(category_mrr_values) / len(category_mrr_values)
                if category_mrr_values
                else None
            ),
            recall_at_k=category_recall,
        )

    return RetrievalEvalSummaryMetrics(
        question_count=question_count,
        mean_mrr=mean_mrr,
        recall_at_k=recall_at_k,
        expected_article_found_rate=expected_article_found_rate,
        expected_chunk_found_rate=expected_chunk_found_rate,
        by_category=by_category,
    )
