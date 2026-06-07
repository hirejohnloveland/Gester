from gester.application.retrieval.search_service import SearchService
from gester.infrastructure.llm.ollama_client import OllamaClient


class AnswerService:
    def __init__(self) -> None:
        self._search_service = SearchService()
        self._llm_client = OllamaClient()

    def answer(
        self,
        question: str,
        limit: int = 5,
        min_score: float = 0.6,
    ) -> dict:
        search_results = self._search_service.search(
            query=question,
            limit=limit,
            min_score=min_score,
            dedupe_by_article=True,
        )

        if not search_results:
            return self._build_no_evidence_response(question)

        if not self._has_direct_text_evidence(question, search_results):
            return self._build_no_evidence_response(question, search_results)

        context = self._build_context(search_results)
        prompt = self._build_prompt(question, context)

        answer_text = self._llm_client.generate(prompt)

        return {
            "question": question,
            "answer": answer_text,
            "sources": [
                {
                    "source_item_id": result.source_item_id,
                    "chunk_id": result.chunk_id,
                    "title": result.title,
                    "url": result.url,
                    "score": result.score,
                }
                for result in search_results
            ],
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

    def _build_no_evidence_response(self, question: str, search_results=None) -> dict:
        return {
            "question": question,
            "answer": "The stored sources do not provide enough information to answer this question.",
            "sources": [
                {
                    "source_item_id": result.source_item_id,
                    "chunk_id": result.chunk_id,
                    "title": result.title,
                    "url": result.url,
                    "score": result.score,
                }
                for result in (search_results or [])
            ],
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