"""
logging_config.py
Sets up file + console logging for the trading bot.
Log file is written to logs/trading_bot.log relative to project root.
"""

import logging
import os
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "trading_bot.log"


def setup_logger(name: str = "trading_bot") -> logging.Logger:
    """
    Create and return a logger that writes to both console (INFO)
    and a rotating log file (DEBUG).
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        # Avoid adding duplicate handlers on re-import
        return logger

    logger.setLevel(logging.DEBUG)

    # ── File handler (DEBUG and above) ──────────────────────────────────────
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh.setFormatter(file_fmt)

    # ── Console handler (INFO and above) ────────────────────────────────────
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    console_fmt = logging.Formatter("%(levelname)-8s | %(message)s")
    ch.setFormatter(console_fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
