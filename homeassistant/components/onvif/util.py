"""ONVIF util."""

from __future__ import annotations

from typing import Any

from zeep.exceptions import Fault


def extract_subcodes_as_strings(subcodes: Any) -> list[str]:
    """Stringify ONVIF subcodes."""
    # Fast path for list input using attribute getter for better speed than hasattr
    if isinstance(subcodes, list):
        _get_text = _safe_get_text  # Local for speed
        return [_get_text(code) for code in subcodes]
    return [str(subcodes)]


def stringify_onvif_error(error: Exception) -> str:
    """Stringify ONVIF error."""
    if isinstance(error, Fault):
        message = error.message
        if error.detail is not None:
            # Detail may be bytes, decode if so
            detail = (
                error.detail.decode("utf-8", "replace")
                if isinstance(error.detail, bytes)
                else str(error.detail)
            )
            message = f"{message}: {detail}"
        if error.code is not None:
            message = f"{message} (code:{error.code})"
        if error.subcodes is not None:
            # Avoid recomputing and double formatting
            subcodes_str = ",".join(extract_subcodes_as_strings(error.subcodes))
            message = f"{message} (subcodes:{subcodes_str})"
        if error.actor:
            message = f"{message} (actor:{error.actor})"
    else:
        message = str(error)
    return message or f"Device sent empty error with type {type(error)}"


def is_auth_error(error: Exception) -> bool:
    """Return True if error is an authentication error.

    Most of the tested cameras do not return a proper error code when
    authentication fails, so we need to check the error message as well.
    """
    if not isinstance(error, Fault):
        return False
    return (
        any(
            "NotAuthorized" in code
            for code in extract_subcodes_as_strings(error.subcodes)
        )
        or "auth" in stringify_onvif_error(error).lower()
    )


def _safe_get_text(code: Any) -> str:
    """Efficient attribute getter for code.text or fallback to str(code)."""
    try:
        return code.text
    except AttributeError:
        return str(code)
