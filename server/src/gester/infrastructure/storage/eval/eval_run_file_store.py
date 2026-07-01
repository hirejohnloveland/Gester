import logging
import re
from pathlib import Path

from gester.domain.models.retrieval_eval_run import RetrievalEvalRun

logger = logging.getLogger(__name__)

_RUN_ID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")


class EvalRunFileStore:
    def __init__(self, runs_dir: Path) -> None:
        self._runs_dir = runs_dir

    def save(self, run: RetrievalEvalRun) -> Path:
        self._validate_run_id(run.run_id)
        self._runs_dir.mkdir(parents=True, exist_ok=True)

        path = self._path_for_run_id(run.run_id)
        path.write_text(
            run.model_dump_json(indent=2),
            encoding="utf-8",
        )

        logger.info("Saved retrieval eval run %s to %s", run.run_id, path)

        return path

    def load(self, run_id: str) -> RetrievalEvalRun:
        self._validate_run_id(run_id)

        path = self._path_for_run_id(run_id)

        if not path.is_file():
            raise FileNotFoundError(f"Retrieval eval run not found: {run_id}")

        return RetrievalEvalRun.model_validate_json(path.read_text(encoding="utf-8"))

    def list_run_ids(self) -> list[str]:
        if not self._runs_dir.is_dir():
            return []

        return sorted(
            path.stem
            for path in self._runs_dir.glob("*.json")
            if path.is_file()
        )

    def _path_for_run_id(self, run_id: str) -> Path:
        return self._runs_dir / f"{run_id}.json"

    def _validate_run_id(self, run_id: str) -> None:
        if not run_id or not _RUN_ID_PATTERN.match(run_id):
            raise ValueError(
                "Run id must start with a letter or digit and contain only "
                "letters, digits, underscores, and hyphens."
            )
