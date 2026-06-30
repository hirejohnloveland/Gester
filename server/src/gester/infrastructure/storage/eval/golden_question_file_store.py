import logging
from pathlib import Path

import yaml

from gester.domain.models.retrieval_eval_question import GoldenQuestionSet

logger = logging.getLogger(__name__)


class GoldenQuestionFileStore:
    def __init__(self, questions_path: Path) -> None:
        self._questions_path = questions_path

    def load(self) -> GoldenQuestionSet:
        if not self._questions_path.is_file():
            raise FileNotFoundError(f"Golden question set not found: {self._questions_path}")

        data = yaml.safe_load(self._questions_path.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            raise ValueError(f"Golden question set must be a mapping: {self._questions_path}")

        question_set = GoldenQuestionSet.model_validate(data)

        logger.info(
            "Loaded golden question set %s with %d question(s) from %s",
            question_set.version,
            question_set.question_count,
            self._questions_path,
        )

        return question_set

    def save(self, question_set: GoldenQuestionSet) -> Path:
        self._questions_path.parent.mkdir(parents=True, exist_ok=True)

        payload = question_set.model_dump(mode="json")
        self._questions_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

        logger.info(
            "Saved golden question set %s with %d question(s) to %s",
            question_set.version,
            question_set.question_count,
            self._questions_path,
        )

        return self._questions_path
