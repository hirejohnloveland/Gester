import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_OWNED_HANDLER_ATTR = "_gester_owned"


def configure_logging(
    log_dir: Path,
    level: str,
    retention_days: int,
    filename: str,
    console: bool,
) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(level.upper())

    _remove_owned_handlers(root_logger)

    formatter = logging.Formatter(_LOG_FORMAT)

    file_handler = TimedRotatingFileHandler(
        log_dir / filename,
        when="midnight",
        backupCount=retention_days,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    _mark_owned(file_handler)
    root_logger.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        _mark_owned(console_handler)
        root_logger.addHandler(console_handler)


def _mark_owned(handler: logging.Handler) -> None:
    setattr(handler, _OWNED_HANDLER_ATTR, True)


def _remove_owned_handlers(logger: logging.Logger) -> None:
    for handler in list(logger.handlers):
        if getattr(handler, _OWNED_HANDLER_ATTR, False):
            logger.removeHandler(handler)
            handler.close()
