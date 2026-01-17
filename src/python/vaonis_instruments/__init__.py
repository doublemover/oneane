"""Vaonis instrument control (Barnard app reverse engineered API surface).

This package is a lightweight, best-effort client generated from static analysis of the
com.vaonis.barnard Android app.

Important: Write/control endpoints require an Authorization header computed by the official
app. This package intentionally does not ship the vendor key material required to generate
that header.
"""

from .auth import AuthContext, build_authorization_header
from .auth_key_extractor import ensure_auth_key
from .logging_utils import format_payload, setup_logging
from .http_client import VaonisHTTPClient
from .socket_client import StellinaSocketV2Client, VaonisSocketClient
from .unified_client import UnifiedHTTPClient

__all__ = [
    "AuthContext",
    "VaonisHTTPClient",
    "VaonisSocketClient",
    "StellinaSocketV2Client",
    "build_authorization_header",
    "UnifiedHTTPClient",
    "ensure_auth_key",
    "format_payload",
    "setup_logging",
]
