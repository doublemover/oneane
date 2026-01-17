from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_ROOT = ROOT / "src" / "unified" / "schemas"
HTTP_SCHEMA_DIR = SCHEMAS_ROOT / "http"
EVENTS_SCHEMA_DIR = SCHEMAS_ROOT / "events"
SOCKET_SCHEMA_DIR = SCHEMAS_ROOT / "socket"
HTTP_ENDPOINTS = ROOT / "src" / "unified" / "data" / "api_full" / "http_endpoints.json"
EXTRACTED_ENDPOINTS = (
    ROOT / "src" / "unified" / "data" / "api_extracted" / "stellina_api_endpoints.json"
)
OUT_PATH = SCHEMAS_ROOT / "schema_bundle.json"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_route_key(method: str, path: str) -> str:
    normalized_path = "/" + path.lstrip("/")
    return f"{method.upper()} {normalized_path}"


def _schema_name_from_ref(ref: str) -> str:
    return str(ref).split("/")[-1]


def _load_schemas_by_name(schema_dir: Path) -> Dict[str, Dict[str, Any]]:
    schemas: Dict[str, Dict[str, Any]] = {}
    if not schema_dir.exists():
        return schemas
    for schema_path in sorted(schema_dir.glob("*.json")):
        if not schema_path.is_file():
            continue
        name = schema_path.stem
        schemas[name] = _load_json(schema_path)
    return schemas


def _class_name_from_descriptor(descriptor: Optional[str]) -> Optional[str]:
    if not descriptor:
        return None
    value = str(descriptor).strip()
    if value.startswith("L") and value.endswith(";"):
        value = value[1:-1]
    value = value.replace(";", "")
    name = value.split("/")[-1]
    return name or None


def _load_routes(http_schemas: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    routes: Dict[str, Dict[str, Any]] = {}
    if HTTP_ENDPOINTS.exists():
        endpoints = _load_json(HTTP_ENDPOINTS)
        for endpoint in endpoints:
            method = str(endpoint.get("method", "")).upper()
            path = str(endpoint.get("path", ""))
            if not method or not path:
                continue
            key = _normalize_route_key(method, path)
            entry = routes.setdefault(key, {})
            request_ref = endpoint.get("requestBodyRef")
            if request_ref:
                request_name = _schema_name_from_ref(request_ref)
                if request_name in http_schemas:
                    entry["request"] = request_name
            responses = endpoint.get("responses") or {}
            response_map: Dict[str, str] = {}
            for status, response in responses.items():
                schema_ref = (response or {}).get("schemaRef")
                if not schema_ref:
                    continue
                response_name = _schema_name_from_ref(schema_ref)
                if response_name in http_schemas:
                    response_map[str(status)] = response_name
            if response_map:
                entry["responses"] = response_map
    if EXTRACTED_ENDPOINTS.exists():
        endpoints = _load_json(EXTRACTED_ENDPOINTS)
        for endpoint in endpoints:
            method = str(endpoint.get("http_method", "")).upper()
            path = str(endpoint.get("path", ""))
            if not method or not path:
                continue
            key = _normalize_route_key(method, path)
            entry = routes.setdefault(key, {})
            query_params: List[str] = []
            for param in endpoint.get("params", []) or []:
                annotations = param.get("annotations", []) or []
                for annotation in annotations:
                    kind = str(annotation.get("kind", "")).lower()
                    if kind == "query":
                        elements = annotation.get("elements") or {}
                        name = elements.get("value")
                        if isinstance(name, str) and name.strip():
                            query_params.append(name)
                    elif kind == "body":
                        body_type = _class_name_from_descriptor(param.get("type"))
                        if body_type and "request" not in entry:
                            if body_type in http_schemas:
                                entry["request"] = body_type
            if query_params:
                existing = entry.get("queryParams", [])
                if not isinstance(existing, list):
                    existing = []
                for name in query_params:
                    if name not in existing:
                        existing.append(name)
                entry["queryParams"] = existing
    return {key: value for key, value in routes.items() if value}


def main() -> None:
    http_schemas = _load_schemas_by_name(HTTP_SCHEMA_DIR)
    events_schemas = _load_schemas_by_name(EVENTS_SCHEMA_DIR)
    socket_schemas = _load_schemas_by_name(SOCKET_SCHEMA_DIR)
    routes = _load_routes(http_schemas)
    bundle = {
        "version": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "http": {
            "schemasByName": http_schemas,
            "routes": routes,
        },
        "events": {
            "schemasByName": events_schemas,
        },
        "socket": {
            "schemasByName": socket_schemas,
        },
    }
    OUT_PATH.write_text(
        json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
