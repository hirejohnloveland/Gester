from typing import Annotated

from fastapi import APIRouter, Depends

from gester.api.dependencies import SettingsDep, get_answer_service, get_search_service
from gester.application.responses.answer_response import AnswerResponse
from gester.application.retrieval.answer_service import AnswerService
from gester.application.retrieval.search_service import SearchService

router = APIRouter(tags=["retrieval"])


@router.get("/search")
def search(
    query: str,
    settings: SettingsDep,
    service: Annotated[SearchService, Depends(get_search_service)],
    limit: int | None = None,
    min_score: float | None = None,
    dedupe_by_article: bool | None = None,
):
    retrieval = settings.retrieval

    return service.search(
        query,
        limit if limit is not None else retrieval.limit,
        min_score if min_score is not None else retrieval.min_score,
        dedupe_by_article if dedupe_by_article is not None else retrieval.dedupe_by_article,
    )


@router.get("/ask", response_model=AnswerResponse)
def ask(
    question: str,
    settings: SettingsDep,
    service: Annotated[AnswerService, Depends(get_answer_service)],
    limit: int | None = None,
    min_score: float | None = None,
):
    retrieval = settings.retrieval

    return service.answer(
        question,
        limit if limit is not None else retrieval.limit,
        min_score if min_score is not None else retrieval.min_score,
    )
