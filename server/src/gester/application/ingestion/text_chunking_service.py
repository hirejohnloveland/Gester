"""Splits raw article text into overlapping character-based chunks."""

from gester.domain.models.text_chunk import TextChunk


class TextChunkingService:
    """Fixed-size text chunker with overlap and word-boundary alignment.

    ``chunk_size`` and ``overlap`` defaults are for direct construction (e.g.
    tests). The running app supplies values from ``settings.chunking``.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if overlap < 0:
            raise ValueError("overlap cannot be negative.")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size.")

        self._chunk_size = chunk_size
        self._overlap = overlap
    def chunk(self, text: str) -> list[TextChunk]:
        """Return ordered chunks for ``text``, or an empty list when blank."""
        if text is None or text.strip() == "":
            return []

        chunks: list[TextChunk] = []

        text_length = len(text)
        start = 0

        while start < text_length:
            end = min(start + self._chunk_size, text_length)
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(TextChunk(char_start=start, char_end=end, chunk_text=chunk_text))

            if end == text_length:
                break

            start = self._move_start_to_word_boundary(text, end - self._overlap)

        return chunks

    def _move_start_to_word_boundary(self, text: str, start: int) -> int:
        if start == 0:
            return start

        if text[start - 1].isspace():
            return start

        while start < len(text) and not text[start].isspace():
            start += 1

        while start < len(text) and text[start].isspace():
            start += 1

        return start