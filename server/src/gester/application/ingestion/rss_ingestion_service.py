import logging
from datetime import datetime, timedelta, timezone

from gester.application.ingestion.text_chunking_service import TextChunkingService
from gester.domain.models.rss_item import RssItem
from gester.domain.models.source_item import SourceItem
from gester.domain.models.source_item_chunk import SourceItemChunk
from gester.infrastructure.extraction.article_extractor import ArticleExtractor
from gester.infrastructure.feeds.rss_reader import RssReader
from gester.infrastructure.storage.sqlite.source_item_chunk_repository import SourceItemChunkRepository
from gester.infrastructure.storage.sqlite.source_item_repository import SourceItemRepository

logger = logging.getLogger(__name__)


class RssIngestionService:
    def __init__(
        self,
        rss_reader: RssReader,
        article_extractor: ArticleExtractor,
        repository: SourceItemRepository,
        chunking_service: TextChunkingService,
        chunk_repository: SourceItemChunkRepository,
        max_age_days: int,
        max_items_per_feed: int,
    ) -> None:
        self._rss_reader = rss_reader
        self._article_extractor = article_extractor
        self._repository = repository
        self._chunking_service = chunking_service
        self._chunk_repository = chunk_repository
        self._max_age_days = max_age_days
        self._max_items_per_feed = max_items_per_feed

    def ingest(
        self,
        feed_url: str,
        max_age_days: int | None = None,
        max_items_per_feed: int | None = None,
    ) -> int:
        effective_max_age_days = (
            max_age_days if max_age_days is not None else self._max_age_days
        )
        effective_max_items = (
            max_items_per_feed
            if max_items_per_feed is not None
            else self._max_items_per_feed
        )

        logger.info(
            "Ingestion started for feed %s (max_age_days=%d, max_items_per_feed=%d)",
            feed_url,
            effective_max_age_days,
            effective_max_items,
        )

        rss_items = self._rss_reader.read(feed_url)
        rss_items = self._apply_ingestion_limits(
            rss_items, effective_max_age_days, effective_max_items
        )

        saved_count = 0

        for rss_item in rss_items:
            raw_content = self._article_extractor.extract(rss_item.link)

            if raw_content is None:
                logger.warning(
                    "Extraction returned no content for %s; falling back to feed summary",
                    rss_item.link,
                )
                raw_content = rss_item.summary

            source_item = SourceItem(
                source_type=rss_item.source_type,
                title=rss_item.title,
                url=rss_item.link,
                raw_content=raw_content,
                published_at=rss_item.published_at,
            )

            saved = self._repository.add_if_not_exists(source_item)

            if saved is None:
                logger.debug("Skipped duplicate source item %s", rss_item.link)
                continue

            saved_count += 1

            chunks = self._chunking_service.chunk(saved.raw_content)

            for index, chunk in enumerate(chunks):
                source_item_chunk = SourceItemChunk(
                    source_item_id=saved.id,
                    chunk_index=index,
                    chunk_text=chunk.chunk_text,
                    char_start=chunk.char_start,
                    char_end=chunk.char_end,
                )

                self._chunk_repository.add(source_item_chunk)

            logger.debug(
                "Created %d chunk(s) for source item %s", len(chunks), saved.url
            )

        logger.info(
            "Ingestion finished for feed %s; %d new item(s) saved", feed_url, saved_count
        )

        return saved_count

    def _apply_ingestion_limits(
        self,
        items: list[RssItem],
        max_age_days: int,
        max_items_per_feed: int,
    ) -> list[RssItem]:
        # RSS published dates are parsed as naive UTC; compare against a
        # naive UTC cutoff. Items with no published date are kept because
        # their age cannot be determined.
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
            days=max_age_days
        )

        within_age = [
            item
            for item in items
            if item.published_at is None or item.published_at >= cutoff
        ]

        limited = within_age[:max_items_per_feed]

        logger.info(
            "Feed yielded %d entries; %d within %d-day window; %d kept after cap of %d",
            len(items),
            len(within_age),
            max_age_days,
            len(limited),
            max_items_per_feed,
        )

        return limited
