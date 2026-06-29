from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from gester.api.dependencies import get_evaluation_corpus_service
from gester.application.evaluation.evaluation_corpus_service import EvaluationCorpusService
from gester.application.responses.evaluation_corpus_response import (
    EvaluationCorpusDetailResponse,
    EvaluationCorpusSummaryResponse,
)

router = APIRouter(prefix="/eval", tags=["evaluation"])


@router.post("/corpora", response_model=EvaluationCorpusSummaryResponse)
def create_corpus(
    service: Annotated[EvaluationCorpusService, Depends(get_evaluation_corpus_service)],
    version: str | None = None,
):
    try:
        corpus = service.create_corpus(version)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    return EvaluationCorpusSummaryResponse.from_corpus(corpus)


@router.get("/corpora", response_model=list[EvaluationCorpusSummaryResponse])
def list_corpora(
    service: Annotated[EvaluationCorpusService, Depends(get_evaluation_corpus_service)],
):
    corpora = service.list_corpora()

    return [EvaluationCorpusSummaryResponse.from_corpus(corpus) for corpus in corpora]


@router.get("/corpora/{version}", response_model=EvaluationCorpusDetailResponse)
def get_corpus(
    version: str,
    service: Annotated[EvaluationCorpusService, Depends(get_evaluation_corpus_service)],
):
    try:
        corpus = service.get_corpus(version)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return EvaluationCorpusDetailResponse.from_corpus(corpus)
