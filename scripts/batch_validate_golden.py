"""Batch search for golden questions — outputs ranks for curation."""
import sys
from collections import Counter
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server" / "src"))

from gester.application.retrieval.search_service import SearchService
from gester.configuration.settings_loader import load_settings
from gester.domain.models.retrieval_eval_question import QuestionCategory
from gester.infrastructure.embeddings.embedding_service import EmbeddingService
from gester.infrastructure.storage.sqlite.source_item_chunk_repository import SourceItemChunkRepository
from gester.infrastructure.storage.sqlite.source_item_repository import SourceItemRepository
from gester.infrastructure.storage.sqlite.sqlite_db import (
    create_db_engine,
    create_session_factory,
    initialize_database,
)
from gester.infrastructure.storage.vector.qdrant_vector_store import QdrantVectorStore
from qdrant_client.models import Distance

LIMIT = 20
MIN_SCORE = 0.0


def build_search_service(settings):
    engine = create_db_engine(settings.database_path)
    initialize_database(engine)
    sf = create_session_factory(engine)
    vs = QdrantVectorStore(
        settings.qdrant_path,
        settings.vector_store.collection_name,
        settings.vector_store.vector_size,
        Distance.COSINE,
    )
    return SearchService(
        EmbeddingService(settings.embedding.model_name),
        vs,
        SourceItemChunkRepository(sf),
        SourceItemRepository(sf),
    )


def analyze_question(svc, qid, question, category, expected, dedupe: bool):
    results = svc.search(question, limit=LIMIT, min_score=MIN_SCORE, dedupe_by_article=dedupe)
    chunk_counts = Counter(r.source_item_id for r in results)
    deduped = []
    seen = set()
    for r in results:
        if r.source_item_id not in seen:
            seen.add(r.source_item_id)
            deduped.append(r)

    print(f"\n{'='*72}")
    print(f"ID: {qid} | {category} | dedupe={dedupe}")
    print(f"Q: {question}")
    print(f"Current expected: {expected}")
    print("Top chunks by article count:", dict(chunk_counts.most_common(5)))
    print("Deduped top 10:")
    for i, r in enumerate(deduped[:10], 1):
        mark = " *" if r.source_item_id in expected else ""
        title = r.title[:65].encode("ascii", "replace").decode("ascii")
        print(f"  {i:2} {r.score:.4f} art={r.source_item_id} cnt={chunk_counts[r.source_item_id]}{mark} | {title}")

    if expected:
        for aid in expected:
            ranks = [i for i, r in enumerate(deduped, 1) if r.source_item_id == aid]
            print(f"  expected {aid} deduped rank: {ranks[0] if ranks else 'not in top'}")


def main():
    settings = load_settings()
    path = settings.golden_questions_path
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    svc = build_search_service(settings)

    pending = [
        q for q in data["questions"]
        if "Validated" not in (q.get("notes") or "")
    ]

    print(f"Pending: {len(pending)} questions")

    for q in pending:
        cat = q["category"]
        dedupe = cat != "direct_lookup"  # direct: false per user workflow; concept often true
        if cat == "direct_lookup":
            dedupe = False
        elif cat in ("concept", "proper_noun", "near_miss"):
            dedupe = True
        else:
            dedupe = True

        analyze_question(
            svc,
            q["id"],
            q["question"],
            cat,
            q.get("expected_article_ids") or [],
            dedupe,
        )


if __name__ == "__main__":
    main()
