import logging

import trafilatura

logger = logging.getLogger(__name__)


class ArticleExtractor:
    def extract(self, url: str) -> str | None:
        downloaded = trafilatura.fetch_url(url)

        if downloaded is None:
            logger.warning("Article download failed for %s", url)
            return None

        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
        )

        if text is None or text.strip() == "":
            logger.warning("Article extraction returned empty content for %s", url)
            return None

        return text.strip()