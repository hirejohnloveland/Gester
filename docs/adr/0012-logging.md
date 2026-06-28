# ADR-0012: Logging

## Status

Accepted

## Context

The application previously relied on uvicorn's default logging only.
Application services (ingestion, chunking, embedding, retrieval) and some
infrastructure components (article extraction, RSS reading) performed
meaningful work and silent failures with no durable record, making it
hard to troubleshoot a run after the fact. `docs/coding-standards.md`
calls for logging pipeline activity and failures, and roadmap milestone
0.1 requires basic logging to work.

A logging approach was needed that records pipeline activity to a file,
survives restarts, bounds disk usage, and adds no new dependency
(`agents/agents.md` discourages new frameworks without discussion).

## Decision

Gester uses the Python standard-library `logging` module, configured once
at startup from a validated `logging` settings section.

### Configuration source

- `config/settings.yaml` has a `logging` section: `level` (e.g. `INFO`),
  `retention_days`, `filename`, and `console`.
- These are validated into a `LoggingSettings` model on `AppSettings`
  (see ADR-0011). `AppSettings.log_dir` derives the log directory as
  `data_dir / "logs"`.

### Configurator

`infrastructure/logging/logging_configurator.py` exposes
`configure_logging(log_dir, level, retention_days, filename, console)`.
It takes explicit primitive parameters rather than importing
`AppSettings`, keeping infrastructure decoupled from the settings model
(consistent with ADR-0011's injection boundary). It:

- creates the log directory,
- attaches a `TimedRotatingFileHandler` that rotates at midnight and
  keeps `retention_days` backups (default 14),
- optionally attaches a console `StreamHandler`,
- applies a readable formatter
  (`"%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"`),
- and sets the root logger level.

The function is idempotent: it removes and closes only the handlers it
previously added before re-adding, so repeated calls (e.g. reload) do not
duplicate handlers.

### Composition root

`app.py` calls `configure_logging(...)` in `startup()` immediately after
`load_settings()` and then emits a startup `INFO` line. Modules obtain a
logger via `logging.getLogger(__name__)` and rely on root-logger
propagation rather than configuring handlers themselves.

### Log placement

Logs are written under `data/logs/` (e.g. `data/logs/gester.log`), which
is git-ignored alongside other generated runtime data.

## Consequences

### Benefits

- Durable, rotating record of pipeline activity and failures
- Bounded disk usage via daily rotation and retention
- No new dependency; uses the standard library
- Configurable level, retention, filename, and console output
- Previously silent extraction failures now surface as warnings

### Tradeoffs

- Logging is configured after settings load, so a `load_settings()`
  failure still surfaces only through uvicorn's own logging
- Capturing uvicorn's access/error loggers into the file is out of scope

## Guiding Rule

Log meaningful pipeline activity and failures through a module logger
(`logging.getLogger(__name__)`); do not add handler configuration outside
the configurator or read logging settings inside business logic.
