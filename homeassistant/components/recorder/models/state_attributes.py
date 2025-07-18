"""State attributes models."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.util.json import json_loads

EMPTY_JSON_OBJECT = "{}"
_LOGGER = logging.getLogger(__name__)


def decode_attributes_from_source(
    source: Any, attr_cache: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Decode attributes from a row source."""
    # Fast-path: nothing or explicit empty
    if not source or source == EMPTY_JSON_OBJECT:
        return {}

    # Fast cache hit
    cached = attr_cache.get(source)
    if cached is not None:
        return cached

    try:
        # Directly parse to dict only
        obj = json_loads(source)
        if type(obj) is dict:
            attr_cache[source] = obj
            return obj
        # Will fall through to log/return {} if not dict
        raise ValueError
    except Exception:
        _LOGGER.exception("Error converting row to state attributes: %s", source)
        attr_cache[source] = {}
        return {}
