"""Logging helpers for HTTP/Socket instrumentation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import logging
from pathlib import Path
import re
from typing import Any, Optional


ANSI_RESET = "\033[0m"
ANSI_BLUE = "\033[94m"
ANSI_GREEN = "\033[92m"
ANSI_CYAN = "\033[96m"
ANSI_MAGENTA = "\033[95m"


def find_repo_root(start: Optional[Path] = None) -> Path:
    probe = start or Path(__file__).resolve()
    for parent in [probe, *probe.parents]:
        if (parent / ".git").exists() or (parent / "src").exists():
            return parent
    return Path.cwd()


def ensure_log_dir(root: Optional[Path] = None) -> Path:
    base = root or find_repo_root()
    log_dir = base / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def make_log_path(prefix: str, *, root: Optional[Path] = None) -> Path:
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    log_dir = ensure_log_dir(root)
    return log_dir / f"{prefix}_{stamp}.log"


def configure_logger(
    name: str,
    log_path: Path,
    *,
    level: int = logging.INFO,
    also_console: bool = False,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.handlers.clear()

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if also_console:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


@dataclass
class LogContext:
    name: str
    logger: logging.Logger
    log_path: Path


def setup_logging(prefix: str, *, also_console: bool = False) -> LogContext:
    log_path = make_log_path(prefix)
    logger = configure_logger(prefix, log_path, also_console=also_console)
    return LogContext(name=prefix, logger=logger, log_path=log_path)


def _colorize_json_line(line: str) -> str:
    key_match = re.match(r'(\s*)("[^"]+")(\s*:\s*)(.*)', line)
    if not key_match:
        return line
    indent, key, sep, rest = key_match.groups()
    key_colored = f"{ANSI_BLUE}{key}{ANSI_RESET}"
    value = rest
    value_match = re.match(r'"[^"]*"', value)
    if value_match:
        token = value_match.group(0)
        colored = f"{ANSI_GREEN}{token}{ANSI_RESET}"
        value = colored + value[len(token) :]
    else:
        value_match = re.match(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", value)
        if value_match:
            token = value_match.group(0)
            colored = f"{ANSI_CYAN}{token}{ANSI_RESET}"
            value = colored + value[len(token) :]
        else:
            value_match = re.match(r"(true|false|null)\b", value)
            if value_match:
                token = value_match.group(0)
                colored = f"{ANSI_MAGENTA}{token}{ANSI_RESET}"
                value = colored + value[len(token) :]
    return f"{indent}{key_colored}{sep}{value}"


def colorize_json(text: str) -> str:
    return "\n".join(_colorize_json_line(line) for line in text.splitlines())


def format_payload(value: Any, *, color: bool = False, max_len: int = 4000) -> str:
    if isinstance(value, (bytes, bytearray)):
        rendered = f"<{len(value)} bytes>"
    elif isinstance(value, (dict, list)):
        rendered = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)
    elif isinstance(value, str):
        raw = value.strip()
        if raw:
            try:
                parsed = json.loads(raw)
            except Exception:
                rendered = value
            else:
                rendered = json.dumps(
                    parsed, indent=2, sort_keys=True, ensure_ascii=True
                )
        else:
            rendered = value
    else:
        rendered = str(value)

    if max_len > 0 and len(rendered) > max_len:
        rendered = rendered[: max_len - 20] + "... (truncated)"

    if color:
        return colorize_json(rendered)
    return rendered
