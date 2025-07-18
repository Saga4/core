"""ONVIF util."""

from __future__ import annotations

from typing import Any

from zeep.exceptions import Fault


def extract_subcodes_as_strings(subcodes: Any) -> list[str]:
    """Stringify ONVIF subcodes."""
    # Fast-path for single string or None
    if isinstance(subcodes, list):
        # Using try-except is faster than hasattr in tight loop
        result = []
        append = result.append
        for code in subcodes:
            try:
                append(code.text)
            except AttributeError:
                append(str(code))
        return result
    return [str(subcodes)]


def stringify_onvif_error(error: Exception) -> str:
    """Stringify ONVIF error."""
    if isinstance(error, Fault):
        message = error.message
        if error.detail is not None:
            if isinstance(error.detail, bytes):
                detail = error.detail.decode("utf-8", "replace")
            else:
                detail = str(error.detail)
            message += ": " + detail
        if error.code is not None:
            message += f" (code:{error.code})"
        if error.subcodes is not None:
            # Inline extraction to avoid extra function call frame
            subcodes = error.subcodes
            if isinstance(subcodes, list):
                subcode_strs = []
                append = subcode_strs.append
                for code in subcodes:
                    try:
                        append(code.text)
                    except AttributeError:
                        append(str(code))
            else:
                subcode_strs = [str(subcodes)]
            message += f" (subcodes:{','.join(subcode_strs)})"
        if error.actor:
            message += f" (actor:{error.actor})"
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
    subcodes = error.subcodes
    if subcodes:
        # Only extract once per call
        subcode_strs = extract_subcodes_as_strings(subcodes)
        for code in subcode_strs:
            if "NotAuthorized" in code:
                return True
    # Only call onvif error string creation if not already matched
    # Extracts lower() for efficiency
    return "auth" in stringify_onvif_error(error).lower()
