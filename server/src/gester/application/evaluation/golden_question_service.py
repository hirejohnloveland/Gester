import logging
from collections import Counter

from pydantic import BaseModel, ConfigDict

from gester.application.evaluation.evaluation_corpus_service import EvaluationCorpusService
from gester.domain.models.retrieval_eval_question import GoldenQuestionSet, RetrievalEvalQuestion
from gester.infrastructure.storage.eval.golden_question_file_store import GoldenQuestionFileStore

logger = logging.getLogger(__name__)


class GoldenQuestionValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: str
    message: str


class GoldenQuestionValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    valid: bool
    corpus_version: str
    question_count: int
    category_counts: dict[str, int]
    issues: list[GoldenQuestionValidationIssue]


class GoldenQuestionService:
    def __init__(
        self,
        question_file_store: GoldenQuestionFileStore,
        corpus_service: EvaluationCorpusService,
    ) -> None:
        self._question_file_store = question_file_store
        self._corpus_service = corpus_service

    def load_questions(self) -> GoldenQuestionSet:
        return self._question_file_store.load()

    def get_question(self, question_id: str) -> RetrievalEvalQuestion:
        question_set = self.load_questions()

        for question in question_set.questions:
            if question.id == question_id:
                return question

        raise KeyError(f"Golden question not found: {question_id}")

    def validate_against_corpus(self, corpus_version: str) -> GoldenQuestionValidationResult:
        question_set = self.load_questions()
        corpus = self._corpus_service.get_corpus(corpus_version)

        article_ids = set(corpus.article_ids)
        chunk_ids = set(corpus.chunk_ids)
        issues: list[GoldenQuestionValidationIssue] = []

        for question in question_set.questions:
            for article_id in question.expected_article_ids:
                if article_id not in article_ids:
                    issues.append(
                        GoldenQuestionValidationIssue(
                            question_id=question.id,
                            message=(
                                f"Expected article {article_id} is not in corpus "
                                f"{corpus_version}."
                            ),
                        )
                    )

            for chunk_id in question.expected_chunk_ids:
                if chunk_id not in chunk_ids:
                    issues.append(
                        GoldenQuestionValidationIssue(
                            question_id=question.id,
                            message=(
                                f"Expected chunk {chunk_id} is not in corpus "
                                f"{corpus_version}."
                            ),
                        )
                    )

        category_counts = Counter(question.category.value for question in question_set.questions)

        return GoldenQuestionValidationResult(
            valid=not issues,
            corpus_version=corpus_version,
            question_count=question_set.question_count,
            category_counts=dict(sorted(category_counts.items())),
            issues=issues,
        )
