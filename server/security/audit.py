"""Audit logging utilities."""

from __future__ import annotations

import logging
import os
from typing import Any

from server.utils.config import CONFIG

os.makedirs(os.path.dirname(CONFIG.audit_log_path), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(CONFIG.audit_log_path),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("audit")


def log_event(event: str, metadata: dict[str, Any] | None = None) -> None:
    """Record an audit event with optional metadata."""

    payload = metadata or {}
    logger.info("%s | metadata=%s", event, payload)
