from __future__ import annotations

import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _load_module() -> Any:
    root = Path(__file__).resolve().parents[3]
    module_path = root / "tools" / "build_schema_bundle.py"
    spec = spec_from_file_location("build_schema_bundle", module_path)
    assert spec is not None
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_build_schema_bundle_routes_from_extracted(tmp_path: Path) -> None:
    module = _load_module()

    module.ROOT = tmp_path
    module.SCHEMAS_ROOT = tmp_path / "src" / "unified" / "schemas"
    module.HTTP_SCHEMA_DIR = module.SCHEMAS_ROOT / "http"
    module.EVENTS_SCHEMA_DIR = module.SCHEMAS_ROOT / "events"
    module.SOCKET_SCHEMA_DIR = module.SCHEMAS_ROOT / "socket"
    module.HTTP_ENDPOINTS = (
        tmp_path / "src" / "unified" / "data" / "api_full" / "http_endpoints.json"
    )
    module.EXTRACTED_ENDPOINTS = (
        tmp_path
        / "src"
        / "unified"
        / "data"
        / "api_extracted"
        / "stellina_api_endpoints.json"
    )
    module.OUT_PATH = module.SCHEMAS_ROOT / "schema_bundle.json"

    _write_json(module.HTTP_SCHEMA_DIR / "SettingsBody.json", {"title": "SettingsBody"})
    _write_json(module.HTTP_SCHEMA_DIR / "ThingBody.json", {"title": "ThingBody"})
    _write_json(
        module.EVENTS_SCHEMA_DIR / "STATUS_UPDATED.json", {"title": "STATUS_UPDATED"}
    )
    _write_json(
        module.SOCKET_SCHEMA_DIR / "getStatus.response.json",
        {"title": "getStatus.response"},
    )

    _write_json(
        module.HTTP_ENDPOINTS,
        [
            {
                "method": "POST",
                "path": "/app/setSettings",
                "requestBodyRef": "#/components/schemas/SettingsBody",
                "responses": {},
            }
        ],
    )

    _write_json(
        module.EXTRACTED_ENDPOINTS,
        [
            {
                "http_method": "POST",
                "path": "app/setSettings",
                "params": [
                    {
                        "index": 0,
                        "type": "Ljava/lang/String;",
                        "annotations": [
                            {
                                "kind": "query",
                                "elements": {"value": "includeDefaults"},
                            }
                        ],
                    },
                    {
                        "index": 1,
                        "type": "Lcom/vaonis/instruments/sdk/models/body/SettingsBody;",
                        "annotations": [{"kind": "body", "elements": {}}],
                    },
                ],
            },
            {
                "http_method": "GET",
                "path": "app/logs",
                "params": [
                    {
                        "index": 0,
                        "type": "Ljava/lang/String;",
                        "annotations": [
                            {"kind": "query", "elements": {"value": "level"}}
                        ],
                    }
                ],
            },
            {
                "http_method": "POST",
                "path": "app/doThing",
                "params": [
                    {
                        "index": 0,
                        "type": "Lcom/vaonis/instruments/sdk/models/body/ThingBody;",
                        "annotations": [{"kind": "body", "elements": {}}],
                    }
                ],
            },
        ],
    )

    module.main()

    bundle = json.loads(module.OUT_PATH.read_text(encoding="utf-8"))
    http_routes = bundle["http"]["routes"]
    assert http_routes["POST /app/setSettings"]["request"] == "SettingsBody"
    assert "includeDefaults" in http_routes["POST /app/setSettings"]["queryParams"]
    assert http_routes["GET /app/logs"]["queryParams"] == ["level"]
    assert http_routes["POST /app/doThing"]["request"] == "ThingBody"
