from pydantic import BaseModel

from gester.application.responses.answer_source_response import AnswerSourceResponse
from gester.application.responses.answer_timing_response import AnswerTimingResponse


class AnswerResponse(BaseModel):
    question: str
    answer: str
    thinking: str | None = None
    sources: list[AnswerSourceResponse]
    timing: AnswerTimingResponse