"""Authentication helpers.

Many write/control endpoints require an `Authorization` header.

Barnard computes a custom `Basic ...` value derived from:
- a server-provided `challenge` (from `GET /app/status`),
- telescope identifier + boot count,
- an Ed25519 signature using embedded key material.

This file reads key material from a local-only file (default: `.auth_key`).
Do NOT attempt to access devices you do not own or have explicit permission to control.
"""

from __future__ import annotations

from dataclasses import dataclass
import base64
import hashlib
import os
import tempfile
from pathlib import Path
from typing import Optional, Union


@dataclass
class AuthContext:
    challenge: str
    telescope_id: str
    boot_count: int


def build_authorization_header(
    ctx: AuthContext,
    *,
    key_material: Optional[Union[bytes, str]] = None,
    key_file: Optional[Union[str, Path]] = None,
) -> str:
    """Build the `Authorization` header.

    Returns:
        A full header value, e.g. `"Basic ..."`.
    """
    key_bytes = _resolve_key_material(key_material=key_material, key_file=key_file)
    payload = _build_payload(ctx)
    digest = hashlib.sha512(payload).digest()
    signed_message = _sign_ed25519(digest, key_bytes)
    signature_b64 = base64.b64encode(signed_message).decode("ascii")
    prefix = ctx.challenge[0]
    return f"Basic android|{prefix}|{signature_b64}"


def _resolve_key_material(
    *,
    key_material: Optional[Union[bytes, str]],
    key_file: Optional[Union[str, Path]],
) -> bytes:
    if key_material is not None:
        if isinstance(key_material, str):
            return base64.b64decode(key_material)
        return key_material

    key_path = _default_key_path(key_file)
    if not key_path.exists():
        raise FileNotFoundError(
            f"Authorization key file not found: {key_path}. "
            "Set VAONIS_AUTH_KEY_FILE or pass key_material."
        )
    raw = key_path.read_text(encoding="utf-8").strip()
    return base64.b64decode(raw)


def _is_within_root(root: Path, target: Path) -> bool:
    try:
        target.relative_to(root)
        return True
    except ValueError:
        return False


def _allowed_key_roots() -> list[Path]:
    roots = [Path.cwd(), Path.home(), Path(tempfile.gettempdir())]
    roots.append(Path(__file__).resolve().parents[1])
    try:
        from .logging_utils import find_repo_root

        roots.append(find_repo_root())
    except Exception:
        pass
    return roots


def _normalize_key_path(path: Union[str, Path]) -> Path:
    candidate = Path(path).expanduser()
    resolved = candidate.resolve(strict=False)
    for root in _allowed_key_roots():
        try:
            root_resolved = root.resolve(strict=False)
        except Exception:
            continue
        if _is_within_root(root_resolved, resolved):
            return resolved
    raise ValueError(f"Key file path is outside allowed roots: {resolved}")


def _default_key_path(key_file: Optional[Union[str, Path]]) -> Path:
    if key_file is not None:
        return _normalize_key_path(key_file)
    env_path = os.environ.get("VAONIS_AUTH_KEY_FILE")
    if env_path:
        return _normalize_key_path(env_path)
    cwd = Path.cwd()
    candidates = [cwd / ".auth_key", cwd / "src" / "python" / ".auth_key"]
    for candidate in candidates:
        if candidate.exists():
            return _normalize_key_path(candidate)
    try:
        from .logging_utils import find_repo_root

        repo_root = find_repo_root()
        repo_candidate = repo_root / "src" / "python" / ".auth_key"
        if repo_candidate.exists():
            return _normalize_key_path(repo_candidate)
    except Exception:
        pass
    return _normalize_key_path(candidates[0])


def _build_payload(ctx: AuthContext) -> bytes:
    if not ctx.challenge or len(ctx.challenge) < 2:
        raise ValueError("challenge must include a prefix + base64 payload")
    challenge_bytes = base64.b64decode(ctx.challenge[1:])
    tail = f"|{ctx.telescope_id}|{ctx.boot_count}".encode("utf-8")
    return challenge_bytes + tail


def _sign_ed25519(message: bytes, key_bytes: bytes) -> bytes:
    try:
        from nacl import bindings, signing  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise ImportError(
            "PyNaCl is required for Ed25519 signatures. "
            "Install with: pip install pynacl"
        ) from exc

    if len(key_bytes) == 64:
        return bindings.crypto_sign(message, key_bytes)
    if len(key_bytes) == 32:
        return bytes(signing.SigningKey(key_bytes).sign(message))
    raise ValueError(f"Unexpected Ed25519 key length: {len(key_bytes)} bytes")


__all__ = ["AuthContext", "build_authorization_header"]
