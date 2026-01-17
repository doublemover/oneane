from __future__ import annotations

import base64
import importlib.util
import json
from pathlib import Path


def _load_cli_module() -> object:
    root = Path(__file__).resolve().parents[3]
    module_path = root / "tools" / "extract_auth_key.py"
    spec = importlib.util.spec_from_file_location("extract_auth_key", module_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_extract_auth_key_cli_json(tmp_path: Path, capsys: object) -> None:
    key_bytes = b"A" * 64
    key_b64 = base64.b64encode(key_bytes).decode("ascii")
    smali = (
        ".method public getAuthHeader()Ljava/lang/String;\n"
        "    .locals 1\n"
        f'    const-string v0, "{key_b64}"\n'
        "    return-object v0\n"
        ".end method\n"
    )
    smali_path = tmp_path / "InstrumentRepository.smali"
    smali_path.write_text(smali, encoding="utf-8")
    output_path = tmp_path / "auth.key"

    module = _load_cli_module()
    rc = module.main(["--smali", str(smali_path), "--out", str(output_path), "--json"])
    assert rc == 0

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["ok"] is True
    assert payload["outputFile"] == output_path.name
    assert output_path.read_text(encoding="utf-8").strip() == key_b64
