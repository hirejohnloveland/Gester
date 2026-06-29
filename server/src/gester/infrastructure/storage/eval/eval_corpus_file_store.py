import logging
import re
from pathlib import Path

from gester.domain.models.evaluation_corpus import EvaluationCorpus

logger = logging.getLogger(__name__)

_VERSION_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")


class EvalCorpusFileStore:
    def __init__(self, corpora_dir: Path) -> None:
        self._corpora_dir = corpora_dir

    def save(self, corpus: EvaluationCorpus) -> Path:
        self._validate_version(corpus.version)
        self._corpora_dir.mkdir(parents=True, exist_ok=True)

        path = self._path_for_version(corpus.version)
        path.write_text(
            corpus.model_dump_json(indent=2),
            encoding="utf-8",
        )

        logger.info("Saved evaluation corpus %s to %s", corpus.version, path)

        return path

    def load(self, version: str) -> EvaluationCorpus:
        self._validate_version(version)

        path = self._path_for_version(version)

        if not path.is_file():
            raise FileNotFoundError(f"Evaluation corpus not found: {version}")

        return EvaluationCorpus.model_validate_json(path.read_text(encoding="utf-8"))

    def list_versions(self) -> list[str]:
        if not self._corpora_dir.is_dir():
            return []

        versions = sorted(
            path.stem
            for path in self._corpora_dir.glob("*.json")
            if path.is_file()
        )

        return versions

    def exists(self, version: str) -> bool:
        self._validate_version(version)

        return self._path_for_version(version).is_file()

    def _path_for_version(self, version: str) -> Path:
        return self._corpora_dir / f"{version}.json"

    def _validate_version(self, version: str) -> None:
        if not version or not _VERSION_PATTERN.match(version):
            raise ValueError(
                "Corpus version must start with a letter or digit and contain "
                "only letters, digits, underscores, and hyphens."
            )
