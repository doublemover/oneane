from __future__ import annotations

import base64
import zipfile
from pathlib import Path

import pytest

from vaonis_instruments import auth_key_extractor


def _smali_with_key(key_b64: str) -> str:
    return (
        ".method public getAuthHeader()Ljava/lang/String;\n"
        "    .locals 1\n"
        f'    const-string v0, "{key_b64}"\n'
        "    return-object v0\n"
        ".end method\n"
    )


def test_extract_candidates_filters_by_length() -> None:
    key64 = base64.b64encode(b"A" * 64).decode("ascii")
    key32 = base64.b64encode(b"B" * 32).decode("ascii")
    text = (
        ".method public getAuthHeader()Ljava/lang/String;\n"
        "    .locals 1\n"
        f'    const-string v0, "{key32}"\n'
        f'    const-string v1, "{key64}"\n'
        "    return-object v0\n"
        ".end method\n"
    )
    candidates = auth_key_extractor._extract_candidates(text)
    assert key64 in candidates
    assert key32 not in candidates


def test_extract_key_from_smali_multiple_keys(tmp_path: Path) -> None:
    key1 = base64.b64encode(b"A" * 64).decode("ascii")
    key2 = base64.b64encode(b"B" * 64).decode("ascii")
    smali_one = tmp_path / "one.smali"
    smali_two = tmp_path / "two.smali"
    smali_one.write_text(_smali_with_key(key1), encoding="utf-8")
    smali_two.write_text(_smali_with_key(key2), encoding="utf-8")

    with pytest.raises(auth_key_extractor.MultipleAuthKeysFound):
        auth_key_extractor._extract_key_from_smali([smali_one, smali_two])


def test_ensure_auth_key_accepts_smali(tmp_path: Path) -> None:
    key = base64.b64encode(b"A" * 64).decode("ascii")
    smali_path = tmp_path / "InstrumentRepository.smali"
    smali_path.write_text(_smali_with_key(key), encoding="utf-8")
    output_path = tmp_path / "auth.key"

    result = auth_key_extractor.ensure_auth_key(
        input_path=smali_path,
        key_path=output_path,
    )

    assert result == output_path
    assert output_path.read_text(encoding="utf-8").strip() == key


def test_extract_key_from_smali_no_keys(tmp_path: Path) -> None:
    smali_path = tmp_path / "InstrumentRepository.smali"
    smali_path.write_text(".class public Lcom/vaonis/Nope;", encoding="utf-8")

    with pytest.raises(auth_key_extractor.AuthKeyNotFound):
        auth_key_extractor._extract_key_from_smali([smali_path])


def test_decode_base64_rejects_invalid() -> None:
    assert auth_key_extractor._decode_base64("not base64!") is None


def test_ensure_auth_key_short_circuits_existing(tmp_path: Path) -> None:
    key = base64.b64encode(b"A" * 64).decode("ascii")
    output_path = tmp_path / "auth.key"
    output_path.write_text(f"{key}\n", encoding="utf-8")

    result = auth_key_extractor.ensure_auth_key(
        input_path=tmp_path / "missing.zip",
        key_path=output_path,
    )

    assert result == output_path


def test_ensure_auth_key_from_zip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    key = base64.b64encode(b"A" * 64).decode("ascii")
    smali_content = _smali_with_key(key)
    smali_rel = Path("smali") / "InstrumentRepository.smali"
    zip_path = tmp_path / "bundle.zip"

    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(str(smali_rel), smali_content)

    monkeypatch.setattr(auth_key_extractor, "find_repo_root", lambda: tmp_path)
    output_path = tmp_path / "auth.key"

    result = auth_key_extractor.ensure_auth_key(
        input_path=zip_path,
        key_path=output_path,
    )

    assert result == output_path
    assert output_path.read_text(encoding="utf-8").strip() == key


def test_prompt_for_path_errors() -> None:
    with pytest.raises(auth_key_extractor.AuthKeyNotFound):
        auth_key_extractor._prompt_for_path(lambda _: "")


def test_score_apk() -> None:
    assert auth_key_extractor._score_apk(Path("base.apk")) == 0
    assert auth_key_extractor._score_apk(Path("com.vaonis.barnard.apk")) == 1
    assert auth_key_extractor._score_apk(Path("other.apk")) == 2
