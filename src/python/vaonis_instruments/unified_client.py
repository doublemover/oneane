"""Unified HTTP client covering firmware routes.

This client is intended to call any route listed in the firmware union manifest.
It can autodetect base path prefixes and call routes by operationId.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import requests

from .logging_utils import format_payload


def _looks_like_image(data: bytes, content_type: Optional[str]) -> bool:
    if content_type and content_type.lower().startswith("image/"):
        return True
    if len(data) < 4:
        return False
    if data[:3] == b"\xff\xd8\xff":
        return True  # JPEG
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return True  # PNG
    if data[:2] == b"BM":
        return True  # BMP
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return True  # GIF
    if data[:4] in (b"II*\x00", b"MM\x00*"):
        return True  # TIFF
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return True  # WEBP
    return False


DEFAULT_PREFIXES = ["", "/stellina/http", "/vespera/http"]


@dataclass
class UnifiedHTTPClient:
    host: str = "10.0.0.1"
    port: int = 8082
    api_base_path: str = "/v1"
    prefixes: Iterable[str] = field(default_factory=lambda: list(DEFAULT_PREFIXES))
    timeout_s: float = 10.0
    session: requests.Session = field(default_factory=requests.Session)
    base_url: Optional[str] = None
    logger: Optional[logging.Logger] = None
    log_payloads: bool = True
    log_payload_limit: int = 4000

    def _log(self, message: str, *args: Any) -> None:
        if self.logger is not None:
            self.logger.info(message, *args)

    def detect_base_url(self) -> str:
        for prefix in self.prefixes:
            candidate = self._make_base_url(prefix)
            try:
                resp = self.session.get(
                    f"{candidate}/app/status", timeout=self.timeout_s
                )
                if resp.ok:
                    self.base_url = candidate
                    return candidate
            except requests.RequestException:
                continue
        raise RuntimeError("Unable to detect a working base URL")

    def request(
        self,
        method: str,
        path: str,
        *,
        auth: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        json_body: Any = None,
        files: Any = None,
        stream: bool = False,
    ) -> Any:
        base = self.base_url or self.detect_base_url()
        url = base.rstrip("/") + "/" + path.lstrip("/")
        headers: Dict[str, str] = {}
        if auth is not None:
            headers["Authorization"] = auth
        body_repr: Optional[str] = None
        if json_body is not None:
            try:
                body_repr = json.dumps(json_body, ensure_ascii=True)
            except TypeError:
                body_repr = str(json_body)
        self._log(
            "HTTP request %s %s params=%s json=%s",
            method,
            url,
            params,
            body_repr,
        )
        start = time.monotonic()
        try:
            resp = self.session.request(
                method,
                url,
                params=params,
                json=json_body,
                files=files,
                headers=headers,
                timeout=self.timeout_s,
                stream=stream,
            )
        except requests.RequestException as exc:
            if self.logger is not None:
                self.logger.exception("HTTP error %s %s: %s", method, url, exc)
            raise
        elapsed_ms = (time.monotonic() - start) * 1000.0
        size: Optional[int]
        if stream:
            size = None
        else:
            try:
                size = len(resp.content)
            except Exception:
                size = None
        self._log(
            "HTTP response %s %s status=%s elapsed_ms=%.1f bytes=%s",
            method,
            url,
            resp.status_code,
            elapsed_ms,
            size,
        )
        if self.logger is not None and self.log_payloads and not stream:
            content_type = resp.headers.get("content-type", "")
            if (
                content_type.startswith("image/")
                or "application/octet-stream" in content_type
            ):
                payload = f"<{len(resp.content)} bytes>"
            else:
                payload = format_payload(
                    resp.text, color=False, max_len=self.log_payload_limit
                )
            self._log("HTTP response body %s %s payload=%s", method, url, payload)
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def call_operation(
        self,
        operation_id: str,
        *,
        auth: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        json_body: Any = None,
        files: Any = None,
        stream: bool = False,
    ) -> Any:
        route = _load_routes().get(operation_id)
        if route is None:
            raise KeyError(f"Unknown operationId: {operation_id}")
        return self.request(
            route["method"],
            route["path"],
            auth=auth,
            params=params,
            json_body=json_body,
            files=files,
            stream=stream,
        )

    def download_image(
        self, url: str, stream: bool = False, auth: Optional[str] = None
    ) -> Any:
        base = self.base_url or self.detect_base_url()
        if url.startswith("http://") or url.startswith("https://"):
            full_url = url
        else:
            full_url = base.rstrip("/") + "/" + url.lstrip("/")
        self._log("HTTP image request GET %s", full_url)
        headers: Dict[str, str] = {}
        if auth is not None:
            headers["Authorization"] = auth
        resp = self.session.get(
            full_url, timeout=self.timeout_s, stream=stream, headers=headers
        )
        if stream:
            return resp
        content = resp.content
        content_type = resp.headers.get("content-type")
        self._log(
            "HTTP image response %s status=%s bytes=%s",
            full_url,
            resp.status_code,
            len(content),
        )
        if resp.ok or _looks_like_image(content, content_type):
            return content
        resp.raise_for_status()
        return content

    def _make_base_url(self, prefix: str) -> str:
        return f"http://{self.host}:{self.port}{prefix}{self.api_base_path}".rstrip("/")


_ROUTES_CACHE: Optional[Dict[str, Dict[str, Any]]] = None


def _load_routes() -> Dict[str, Dict[str, Any]]:
    global _ROUTES_CACHE
    if _ROUTES_CACHE is not None:
        return _ROUTES_CACHE
    routes_path = Path(__file__).resolve().parent / "data" / "http_routes_union.json"
    data = json.loads(routes_path.read_text(encoding="utf-8"))
    _ROUTES_CACHE = {item["operationId"]: item for item in data}
    return _ROUTES_CACHE


__all__ = ["UnifiedHTTPClient"]
