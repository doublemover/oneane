import base64
from pathlib import Path

import pytest

from vaonis_instruments.auth import AuthContext, build_authorization_header
from vaonis_instruments.auth import _build_payload, _resolve_key_material, _sign_ed25519


def test_build_authorization_header_with_key_material():
    ctx = AuthContext(
        challenge="A" + base64.b64encode(b"abc").decode("ascii"),
        telescope_id="telescope",
        boot_count=2,
    )
    header = build_authorization_header(ctx, key_material=b"\x00" * 64)

    assert header.startswith("Basic android|A|")
    signature_b64 = header.split("|", 2)[2]
    signature = base64.b64decode(signature_b64)
    assert len(signature) == 128


def test_build_payload_validation():
    ctx = AuthContext(challenge="A", telescope_id="telescope", boot_count=1)
    with pytest.raises(ValueError):
        _build_payload(ctx)


def test_resolve_key_material_from_file(tmp_path: Path):
    key = base64.b64encode(b"\x01" * 64).decode("ascii")
    key_path = tmp_path / "auth.key"
    key_path.write_text(f"{key}\n", encoding="utf-8")

    resolved = _resolve_key_material(key_material=None, key_file=key_path)
    assert resolved == b"\x01" * 64


def test_sign_ed25519_with_seed():
    message = b"data"
    signature = _sign_ed25519(message, b"\x02" * 32)
    assert len(signature) == len(message) + 64
