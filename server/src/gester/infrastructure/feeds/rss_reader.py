import logging
from datetime import datetime

import feedparser

from gester.domain.models.rss_item import RssItem

logger = logging.getLogger(__name__)


class RssReader:
    def read(self, feed_url: str) -> list[RssItem]:
        feed = feedparser.parse(feed_url)

        items: list[RssItem] = []

        for entry in feed.entries:
            item = RssItem(
                title=entry.get("title", "").strip(),
                link=entry.get("link", "").strip(),
                summary=entry.get("summary"),
                published_at=self._parse_published_at(entry),
            )

            items.append(item)

        logger.info("Parsed %d entries from feed %s", len(items), feed_url)

        return items

    def _parse_published_at(self, entry) -> datetime | None:
        published_parsed = entry.get("published_parsed")

        if published_parsed is None:
            return None

        return datetime(*published_parsed[:6])