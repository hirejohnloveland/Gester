from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from gester.api.dependencies import (
    get_evaluation_corpus_service,
    get_golden_question_service,
    get_retrieval_eval_service,
)
from gester.application.evaluation.evaluation_corpus_service import EvaluationCorpusService
from gester.application.evaluation.golden_question_service import (
    GoldenQuestionService,
    GoldenQuestionValidationResult,
)
from gester.application.evaluation.retrieval_eval_service import RetrievalEvalService
from gester.application.responses.evaluation_corpus_response import (
    EvaluationCorpusDetailResponse,
    EvaluationCorpusSummaryResponse,
)
from gester.application.responses.golden_question_response import (
    GoldenQuestionResponse,
    GoldenQuestionSetResponse,
)
from gester.application.responses.retrieval_eval_response import RetrievalEvalRunDetailResponse

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


@router.get("/questions", response_model=GoldenQuestionSetResponse)
def get_questions(
    service: Annotated[GoldenQuestionService, Depends(get_golden_question_service)],
):
    try:
        question_set = service.load_questions()
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return GoldenQuestionSetResponse.from_question_set(question_set)


@router.get("/questions/validate", response_model=GoldenQuestionValidationResult)
def validate_questions(
    corpus_version: str,
    service: Annotated[GoldenQuestionService, Depends(get_golden_question_service)],
):
    try:
        return service.validate_against_corpus(corpus_version)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/questions/{question_id}", response_model=GoldenQuestionResponse)
def get_question(
    question_id: str,
    service: Annotated[GoldenQuestionService, Depends(get_golden_question_service)],
):
    try:
        question = service.get_question(question_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return GoldenQuestionResponse.from_question(question)


@router.post("/retrieval/run", response_model=RetrievalEvalRunDetailResponse)
def run_retrieval_eval(
    corpus_version: str,
    service: Annotated[RetrievalEvalService, Depends(get_retrieval_eval_service)],
    limit: int | None = None,
    min_score: float | None = None,
    dedupe_by_article: bool | None = None,
    question_ids: list[str] | None = None,
):
    try:
        run = service.run_eval(
            corpus_version,
            limit=limit,
            min_score=min_score,
            dedupe_by_article=dedupe_by_article,
            question_ids=question_ids,
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return RetrievalEvalRunDetailResponse.from_run(run)


@router.get("/retrieval/runs", response_model=list[str])
def list_retrieval_eval_runs(
    service: Annotated[RetrievalEvalService, Depends(get_retrieval_eval_service)],
):
    return service.list_runs()


@router.get("/retrieval/runs/{run_id}", response_model=RetrievalEvalRunDetailResponse)
def get_retrieval_eval_run(
    run_id: str,
    service: Annotated[RetrievalEvalService, Depends(get_retrieval_eval_service)],
):
    try:
        run = service.get_run(run_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return RetrievalEvalRunDetailResponse.from_run(run)
