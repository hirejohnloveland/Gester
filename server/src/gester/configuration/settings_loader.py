import os
from pathlib import Path

import yaml

from gester.configuration.app_settings import AppSettings

_DEFAULT_CONFIG_RELATIVE_PATH = Path("config") / "settings.yaml"


def _resolve_project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _resolve_config_path(project_root: Path) -> Path:
    override = os.environ.get("GESTER_CONFIG_PATH")

    if override:
        return Path(override).expanduser().resolve()

    return project_root / _DEFAULT_CONFIG_RELATIVE_PATH


def _read_yaml(config_path: Path) -> dict:
    if not config_path.is_file():
        raise FileNotFoundError(f"Settings file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as config_file:
        data = yaml.safe_load(config_file)

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise ValueError(f"Settings file must contain a mapping: {config_path}")

    return data


def _resolve_data_dir(project_root: Path, paths_section: dict) -> Path:
    override = os.environ.get("GESTER_DATA_DIR")
    raw_data_dir = override if override else paths_section.get("data_dir", "data")

    data_dir = Path(raw_data_dir).expanduser()

    if not data_dir.is_absolute():
        data_dir = project_root / data_dir

    return data_dir.resolve()


def _apply_llm_overrides(llm_section: dict) -> dict:
    base_url_override = os.environ.get("GESTER_OLLAMA_BASE_URL")

    if base_url_override:
        llm_section = {**llm_section, "base_url": base_url_override}

    return llm_section


def load_settings() -> AppSettings:
    project_root = _resolve_project_root()
    config_path = _resolve_config_path(project_root)

    data = _read_yaml(config_path)

    data_dir = _resolve_data_dir(project_root, data.get("paths", {}))
    llm_section = _apply_llm_overrides(data.get("llm", {}))

    return AppSettings(
        project_root=project_root,
        data_dir=data_dir,
        feeds=data.get("feeds", []),
        chunking=data.get("chunking", {}),
        embedding=data.get("embedding", {}),
        vector_store=data.get("vector_store", {}),
        llm=llm_section,
        retrieval=data.get("retrieval", {}),
    )
