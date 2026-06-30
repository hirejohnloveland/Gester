from pydantic import BaseModel, ConfigDict

from gester.domain.models.retrieval_eval_question import GoldenQuestionSet, RetrievalEvalQuestion


class GoldenQuestionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    question: str
    category: str
    expected_article_ids: list[int]
    expected_chunk_ids: list[int]
    expected_terms: list[str]
    notes: str | None

    @classmethod
    def from_question(cls, question: RetrievalEvalQuestion) -> "GoldenQuestionResponse":
        return cls(
            id=question.id,
            question=question.question,
            category=question.category.value,
            expected_article_ids=question.expected_article_ids,
            expected_chunk_ids=question.expected_chunk_ids,
            expected_terms=question.expected_terms,
            notes=question.notes,
        )


class GoldenQuestionSetResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    corpus_version: str | None
    description: str | None
    question_count: int
    questions: list[GoldenQuestionResponse]

    @classmethod
    def from_question_set(cls, question_set: GoldenQuestionSet) -> "GoldenQuestionSetResponse":
        return cls(
            version=question_set.version,
            corpus_version=question_set.corpus_version,
            description=question_set.description,
            question_count=question_set.question_count,
            questions=[
                GoldenQuestionResponse.from_question(question)
                for question in question_set.questions
            ],
        )
