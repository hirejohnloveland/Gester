from fastapi import APIRouter

from gester.application.content.source_item_query_service import SourceItemQueryService
from gester.application.content.source_item_chunk_query_service import SourceItemChunkQueryService
from gester.application.responses.source_item_response import SourceItemResponse

router = APIRouter(tags=["content"])


@router.get("/items", response_model=list[SourceItemResponse])
def get_items():
    service = SourceItemQueryService()
    items = service.get_all()

    return [SourceItemResponse.model_validate(item) for item in items]


@router.get("/items/{item_id}/chunks")
def get_chunks(item_id: int):
    service = SourceItemChunkQueryService()

    return service.get_by_source_item_id(item_id)
