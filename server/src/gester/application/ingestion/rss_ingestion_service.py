from gester.application.ingestion.text_chunking_service import TextChunkingService
from gester.infrastructure.extraction.article_extractor import ArticleExtractor
from gester.infrastructure.feeds.rss_reader import RssReader
from gester.infrastructure.storage.sqlite.entities.source_item_chunk_entity import SourceItemChunkEntity
from gester.infrastructure.storage.sqlite.entities.source_item_entity import SourceItemEntity
from gester.infrastructure.storage.sqlite.source_item_chunk_repository import SourceItemChunkRepository
from gester.infrastructure.storage.sqlite.source_item_repository import SourceItemRepository


class RssIngestionService:
    def __init__(self) -> None:
        self._rss_reader = RssReader()
        self._article_extractor = ArticleExtractor()
        self._repository = SourceItemRepository()
        self._chunking_service = TextChunkingService()
        self._chunk_repository = SourceItemChunkRepository()

    def ingest(self, feed_url: str) -> int:
        rss_items = self._rss_reader.read(feed_url)

        saved_count = 0

        for rss_item in rss_items:
            raw_content = self._article_extractor.extract(rss_item.link)

            if raw_content is None:
                raw_content = rss_item.summary

            entity = SourceItemEntity(
                source_type=rss_item.source_type,
                title=rss_item.title,
                url=rss_item.link,
                raw_content=raw_content,
                published_at=rss_item.published_at,
            )

            saved = self._repository.add_if_not_exists(entity)

            if saved is not None:
                saved_count += 1


                chunks = self._chunking_service.chunk(saved.raw_content)

                for index, chunk in enumerate(chunks):
                    chunk_entity = SourceItemChunkEntity(
                        source_item_id=saved.id,
                        chunk_index=index,
                        chunk_text=chunk.chunk_text,
                        char_start=chunk.char_start,
                        char_end=chunk.char_end,
                    )

                    self._chunk_repository.add(chunk_entity)
        return saved_count