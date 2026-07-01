import logging
from datetime import datetime, timezone

from gester.application.evaluation.evaluation_corpus_service import EvaluationCorpusService
from gester.application.evaluation.golden_question_service import GoldenQuestionService
from gester.application.evaluation.retrieval_eval_metrics import (
    compute_question_metrics,
    compute_summary_metrics,
    format_chunking_strategy,
    is_expected_hit,
)
from gester.application.retrieval.search_service import SearchService
from gester.configuration.app_settings import AppSettings, EvalRetrievalSettings
from gester.domain.models.evaluation_corpus import EvaluationCorpus, EvaluationCorpusArticleSnapshot
from gester.domain.models.retrieval_eval_question import RetrievalEvalQuestion
from gester.domain.models.retrieval_eval_run import (
    RetrievalEvalQuestionResult,
    RetrievalEvalRetrievedResult,
    RetrievalEvalRun,
    RetrievalEvalSettingsSnapshot,
)
from gester.infrastructure.storage.eval.eval_run_file_store import EvalRunFileStore

logger = logging.getLogger(__name__)


class RetrievalEvalService:
    def __init__(
        self,
        settings: AppSettings,
        search_service: SearchService,
        golden_question_service: GoldenQuestionService,
        corpus_service: EvaluationCorpusService,
        run_file_store: EvalRunFileStore,
    ) -> None:
        self._settings = settings
        self._search_service = search_service
        self._golden_question_service = golden_question_service
        self._corpus_service = corpus_service
        self._run_file_store = run_file_store

    def run_eval(
        self,
        corpus_version: str,
        *,
        limit: int | None = None,
        min_score: float | None = None,
        dedupe_by_article: bool | None = None,
        question_ids: list[str] | None = None,
    ) -> RetrievalEvalRun:
        corpus = self._corpus_service.get_corpus(corpus_version)
        question_set = self._golden_question_service.load_questions()
        eval_settings = self._resolve_eval_settings(
            limit=limit,
            min_score=min_score,
            dedupe_by_article=dedupe_by_article,
        )

        validation = self._golden_question_service.validate_against_corpus(corpus_version)

        if not validation.valid:
            issue_messages = "; ".join(
                f"{issue.question_id}: {issue.message}" for issue in validation.issues
            )
            raise ValueError(f"Golden question validation failed: {issue_messages}")

        questions = question_set.questions

        if question_ids is not None:
            selected_ids = set(question_ids)
            questions = [question for question in questions if question.id in selected_ids]

            missing_ids = selected_ids - {question.id for question in questions}

            if missing_ids:
                missing = ", ".join(sorted(missing_ids))
                raise ValueError(f"Unknown golden question id(s): {missing}")

        if not questions:
            raise ValueError("No golden questions selected for retrieval evaluation.")

        chunking_strategy = format_chunking_strategy(corpus)
        embedding_model = corpus.embedding.model_name
        article_by_id = {article.id: article for article in corpus.articles}
        corpus_chunk_ids = set(corpus.chunk_ids)
        question_results: list[RetrievalEvalQuestionResult] = []

        for question in questions:
            question_results.append(
                self._evaluate_question(
                    question=question,
                    corpus=corpus,
                    corpus_chunk_ids=corpus_chunk_ids,
                    article_by_id=article_by_id,
                    eval_settings=eval_settings,
                    chunking_strategy=chunking_strategy,
                    embedding_model=embedding_model,
                )
            )

        created_at = datetime.now(timezone.utc)
        run_id = self._build_run_id(corpus_version, created_at)
        settings_snapshot = RetrievalEvalSettingsSnapshot(
            limit=eval_settings.limit,
            min_score=eval_settings.min_score,
            dedupe_by_article=eval_settings.dedupe_by_article,
            recall_k_values=eval_settings.recall_k_values,
            chunk_text_preview_length=eval_settings.chunk_text_preview_length,
            retrieval_strategy=eval_settings.retrieval_strategy,
        )
        summary = compute_summary_metrics(question_results, eval_settings.recall_k_values)
        run = RetrievalEvalRun(
            run_id=run_id,
            created_at=created_at,
            corpus_version=corpus_version,
            question_set_version=question_set.version,
            eval_settings=settings_snapshot,
            embedding_model=embedding_model,
            chunking_strategy=chunking_strategy,
            summary=summary,
            questions=question_results,
        )

        self._run_file_store.save(run)

        logger.info(
            "Completed retrieval eval run %s for corpus %s (%d question(s), mean MRR=%s)",
            run_id,
            corpus_version,
            summary.question_count,
            summary.mean_mrr,
        )

        return run

    def get_run(self, run_id: str) -> RetrievalEvalRun:
        return self._run_file_store.load(run_id)

    def list_runs(self) -> list[str]:
        return self._run_file_store.list_run_ids()

    def _evaluate_question(
        self,
        *,
        question: RetrievalEvalQuestion,
        corpus: EvaluationCorpus,
        corpus_chunk_ids: set[int],
        article_by_id: dict[int, EvaluationCorpusArticleSnapshot],
        eval_settings: EvalRetrievalSettings,
        chunking_strategy: str,
        embedding_model: str,
    ) -> RetrievalEvalQuestionResult:
        search_results = self._search_service.search(
            question.question,
            limit=eval_settings.limit,
            min_score=eval_settings.min_score,
            dedupe_by_article=eval_settings.dedupe_by_article,
        )
        expected_article_ids = set(question.expected_article_ids)
        expected_chunk_ids = set(question.expected_chunk_ids)
        retrieved_results: list[RetrievalEvalRetrievedResult] = []
        rank = 0

        for search_result in search_results:
            if search_result.chunk_id not in corpus_chunk_ids:
                continue

            rank += 1
            article = article_by_id.get(search_result.source_item_id)
            source_name = article.source_type if article is not None else "unknown"
            is_expected = is_expected_hit(
                search_result.source_item_id,
                search_result.chunk_id,
                expected_article_ids,
                expected_chunk_ids,
            )
            preview_length = eval_settings.chunk_text_preview_length
            chunk_text = search_result.chunk_text

            retrieved_results.append(
                RetrievalEvalRetrievedResult(
                    question_id=question.id,
                    query=question.question,
                    rank=rank,
                    score=search_result.score,
                    chunk_id=search_result.chunk_id,
                    article_id=search_result.source_item_id,
                    article_title=search_result.title,
                    source_name=source_name,
                    source_url=search_result.url,
                    chunk_text_preview=chunk_text[:preview_length],
                    full_chunk_text=chunk_text,
                    retrieval_strategy=eval_settings.retrieval_strategy,
                    corpus_version=corpus.version,
                    embedding_model=embedding_model,
                    chunking_strategy=chunking_strategy,
                    is_expected=is_expected,
                )
            )

        metrics = compute_question_metrics(
            question,
            retrieved_results,
            eval_settings.recall_k_values,
        )

        return RetrievalEvalQuestionResult(
            question_id=question.id,
            question=question.question,
            category=question.category,
            expected_article_ids=question.expected_article_ids,
            expected_chunk_ids=question.expected_chunk_ids,
            metrics=metrics,
            retrieved_results=retrieved_results,
        )

    def _resolve_eval_settings(
        self,
        *,
        limit: int | None,
        min_score: float | None,
        dedupe_by_article: bool | None,
    ) -> EvalRetrievalSettings:
        base_settings = self._settings.eval.retrieval

        return EvalRetrievalSettings(
            limit=limit if limit is not None else base_settings.limit,
            min_score=min_score if min_score is not None else base_settings.min_score,
            dedupe_by_article=(
                dedupe_by_article
                if dedupe_by_article is not None
                else base_settings.dedupe_by_article
            ),
            recall_k_values=base_settings.recall_k_values,
            chunk_text_preview_length=base_settings.chunk_text_preview_length,
            retrieval_strategy=base_settings.retrieval_strategy,
        )

    def _build_run_id(self, corpus_version: str, created_at: datetime) -> str:
        timestamp = created_at.strftime("%Y%m%dT%H%M%SZ")
        base_run_id = f"{corpus_version}_{timestamp}"
        run_id = base_run_id
        suffix = 2

        while run_id in self._run_file_store.list_run_ids():
            run_id = f"{base_run_id}_{suffix}"
            suffix += 1

        return run_id
