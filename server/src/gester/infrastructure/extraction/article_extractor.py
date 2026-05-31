import trafilatura


class ArticleExtractor:
    def extract(self, url: str) -> str | None:
        downloaded = trafilatura.fetch_url(url)

        if downloaded is None:
            return None

        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
        )

        if text is None or text.strip() == "":
            return None

        return text.strip()