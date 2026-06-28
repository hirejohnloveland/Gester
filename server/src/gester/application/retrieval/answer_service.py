import logging
import time

from gester.application.retrieval.search_service import SearchService
from gester.infrastructure.llm.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class AnswerService:
    def __init__(
        self,
        search_service: SearchService,
        llm_client: OllamaClient,
    ) -> None:
        self._search_service = search_service
        self._llm_client = llm_client

    def answer(
        self,
        question: str,
        limit: int = 5,
        min_score: float = 0.6,
    ) -> dict:
        logger.info("Answer question received")

        total_start = time.perf_counter()

        search_start = time.perf_counter()
        search_results = self._search_service.search(
            query=question,
            limit=limit,
            min_score=min_score,
            dedupe_by_article=True,
        )
        search_ms = (time.perf_counter() - search_start) * 1000

        if not search_results:
            logger.info("No search results found; returning no-evidence response")
            return self._build_no_evidence_response(
                question,
                search_ms=search_ms,
                total_start=total_start,
            )

        if not self._has_direct_text_evidence(question, search_results):
            logger.info("No direct text evidence found; returning no-evidence response")
            return self._build_no_evidence_response(
                question,
                search_results,
                search_ms=search_ms,
                total_start=total_start,
            )

        context = self._build_context(search_results)
        prompt = self._build_prompt(question, context)

        generation_start = time.perf_counter()
        answer_text = self._llm_client.generate(prompt)
        generation_ms = (time.perf_counter() - generation_start) * 1000

        logger.info("Answer generation completed in %.1f ms", generation_ms)

        return {
            "question": question,
            "answer": answer_text,
            "sources": [
                {
                    "source_number": index,
                    "source_item_id": result.source_item_id,
                    "chunk_id": result.chunk_id,
                    "title": result.title,
                    "url": result.url,
                    "score": result.score,
                }
                for index, result in enumerate(search_results, start=1)
            ],
            "timing": self._build_timing(
                search_ms=search_ms,
                generation_ms=generation_ms,
                total_start=total_start,
            ),
        }

    def _build_context(self, search_results) -> str:
        context_parts: list[str] = []

        for index, result in enumerate(search_results, start=1):
            context_parts.append(
                f"[Source {index}]\n"
                f"Title: {result.title}\n"
                f"URL: {result.url}\n"
                f"Text:\n{result.chunk_text}"
            )

        return "\n\n".join(context_parts)

    def _build_prompt(self, question: str, context: str) -> str:
        return (
            "You are Gester, a local-first retrieval assistant.\n"
            "Answer using only the provided sources.\n"
            "Do not use outside knowledge.\n"
            "Do not rely on your training data.\n"
            "If the provided sources do not contain the answer, say exactly:\n"
            "\"The stored sources do not provide enough information to answer this question.\"\n"
            "Do not add explanation after that sentence.\n"
            "Cite sources inline using [Source 1], [Source 2], etc.\n\n"
            f"Question:\n{question}\n\n"
            f"Sources:\n{context}\n\n"
            "Answer:"
        )

    def _build_no_evidence_response(
        self,
        question: str,
        search_results=None,
        *,
        search_ms: float,
        total_start: float,
    ) -> dict:
        return {
            "question": question,
            "answer": "The stored sources do not provide enough information to answer this question.",
            "sources": [
                {
                    "source_number": index,
                    "source_item_id": result.source_item_id,
                    "chunk_id": result.chunk_id,
                    "title": result.title,
                    "url": result.url,
                    "score": result.score,
                }
                for index, result in enumerate(search_results or [], start=1)
            ],
            "timing": self._build_timing(
                search_ms=search_ms,
                generation_ms=0.0,
                total_start=total_start,
            ),
        }

    def _build_timing(
        self,
        *,
        search_ms: float,
        generation_ms: float,
        total_start: float,
    ) -> dict:
        total_ms = (time.perf_counter() - total_start) * 1000

        return {
            "search_ms": round(search_ms, 1),
            "generation_ms": round(generation_ms, 1),
            "total_ms": round(total_ms, 1),
        }


    def _has_direct_text_evidence(self, question: str, search_results) -> bool:
        question_terms = self._get_meaningful_terms(question)

        if not question_terms:
            return False

        combined_text = " ".join(
            result.chunk_text.lower()
            for result in search_results
        )

        return any(term in combined_text for term in question_terms)


    def _get_meaningful_terms(self, question: str) -> set[str]:
        stop_words = {
            "what",
            "who",
            "when",
            "where",
            "why",
            "how",
            "is",
            "are",
            "was",
            "were",
            "a",
            "an",
            "the",
            "about",
            "does",
            "do",
            "did",
            "tell",
            "me",
        }

        cleaned = (
            question.lower()
            .replace("?", " ")
            .replace(".", " ")
            .replace(",", " ")
            .replace("'", " ")
        )

        return {
            word
            for word in cleaned.split()
            if len(word) > 2 and word not in stop_words
        }