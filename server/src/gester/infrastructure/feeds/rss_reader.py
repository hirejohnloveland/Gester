from datetime import datetime

import feedparser

from gester.domain.models.rss_item import RssItem


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

        return items

    def _parse_published_at(self, entry) -> datetime | None:
        published_parsed = entry.get("published_parsed")

        if published_parsed is None:
            return None

        return datetime(*published_parsed[:6])