from fastapi import APIRouter

from gester.application.retrieval.search_service import SearchService
from gester.application.retrieval.answer_service import AnswerService
from gester.application.responses.answer_response import AnswerResponse

router = APIRouter(tags=["retrieval"])


@router.get("/search")
def search(
    query: str,
    limit: int = 5,
    min_score: float = 0.6,
    dedupe_by_article: bool = True,
):
    service = SearchService()

    results = service.search(query, limit, min_score, dedupe_by_article)

    return results


@router.get("/ask", response_model=AnswerResponse)
def ask(
    question: str,
    limit: int = 5,
    min_score: float = 0.6,
):
    service = AnswerService()

    return service.answer(question, limit, min_score)
