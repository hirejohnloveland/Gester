from gester.domain.models.source_item import SourceItem
from gester.infrastructure.storage.sqlite.source_item_repository import SourceItemRepository


class SourceItemQueryService:
    def __init__(self) -> None:
        self._repository = SourceItemRepository()

    def get_all(self) -> list[SourceItem]:
        return self._repository.get_all()
