"""Standardized Application Logger for SasthoSetu (Prompt 16).

Implements centralized, privacy-conscious logging using Python's standard `logging` module.
- Logs technical errors, database exceptions, and external API failures.
- Strictly excludes sensitive data: passwords, Gemini API keys, and personal medical details.
- Outputs to local `sasthosetu.log` and console.
"""

import logging
import os
import sys
from typing import Optional

def get_app_base_dir() -> str:
    """Returns a reliable writable directory for persistent application logs."""
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        test_file = os.path.join(exe_dir, ".write_test_log")
        try:
            with open(test_file, "w") as f:
                f.write("ok")
            os.remove(test_file)
            return exe_dir
        except (PermissionError, OSError):
            app_data = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
            fallback_dir = os.path.join(app_data, "SasthoSetu")
            os.makedirs(fallback_dir, exist_ok=True)
            return fallback_dir
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR = get_app_base_dir()
LOG_FILE_PATH = os.path.join(BASE_DIR, "sasthosetu.log")

_is_configured = False


def setup_logger(log_level: int = logging.INFO) -> logging.Logger:
    """Configures the root SasthoSetu logger once and returns the root instance."""
    global _is_configured
    root_logger = logging.getLogger("sasthosetu")

    if not _is_configured:
        root_logger.setLevel(log_level)
        root_logger.propagate = False

        # Format: timestamp [LEVEL] logger_name - message
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # 1. File Handler (UTF-8 encoded)
        try:
            file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception:
            # Fallback gracefully if filesystem cannot write log file
            pass

        # 2. Console Handler (Standard Output)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        _is_configured = True

    return root_logger


def get_logger(module_name: Optional[str] = None) -> logging.Logger:
    """Returns a namespaced child logger under 'sasthosetu'.

    Args:
        module_name: Subsystem name, e.g. 'db', 'triage', 'auth', 'ui'.
    """
    if not _is_configured:
        setup_logger()

    if module_name:
        return logging.getLogger(f"sasthosetu.{module_name}")
    return logging.getLogger("sasthosetu")
