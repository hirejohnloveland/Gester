from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class QuestionCategory(StrEnum):
    DIRECT_LOOKUP = "direct_lookup"
    CONCEPT = "concept"
    PROPER_NOUN = "proper_noun"
    NEAR_MISS = "near_miss"
    NEGATIVE = "negative"


class RetrievalEvalQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    question: str
    category: QuestionCategory
    expected_article_ids: list[int] = Field(default_factory=list)
    expected_chunk_ids: list[int] = Field(default_factory=list)
    expected_terms: list[str] = Field(default_factory=list)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_expected_targets(self) -> "RetrievalEvalQuestion":
        if self.category in (QuestionCategory.NEGATIVE, QuestionCategory.NEAR_MISS):
            return self

        if not self.expected_article_ids and not self.expected_chunk_ids:
            raise ValueError(
                f"Question '{self.id}' must specify expected_article_ids or expected_chunk_ids."
            )

        return self


class GoldenQuestionSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    corpus_version: str | None = None
    description: str | None = None
    questions: list[RetrievalEvalQuestion]

    @property
    def question_count(self) -> int:
        return len(self.questions)
