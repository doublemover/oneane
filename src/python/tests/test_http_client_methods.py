from __future__ import annotations

import inspect
from typing import Any

import pytest
import requests

from vaonis_instruments.http_client import VaonisHTTPClient


class DummyResponse:
    def __init__(self, *, json_raises: bool = True, status: int = 200) -> None:
        self.status_code = status
        self.ok = status < 400
        self._json_raises = json_raises
        self.content = b"{}"
        self.text = "{}"
        self.headers = {"content-type": "application/json"}

    def json(self) -> Any:
        if self._json_raises:
            raise ValueError("no json")
        return {"ok": True}

    def raise_for_status(self) -> None:
        if not self.ok:
            raise requests.HTTPError("bad")


def _dummy_value(name: str) -> Any:
    lowered = name.lower()
    if "auth" in lowered:
        return "auth"
    if "body" in lowered:
        return {"dummy": True}
    if "file" in lowered:
        if "file_name" in lowered:
            return "update.bin"
        return object()
    if "model" in lowered:
        return "stellina"
    return "value"


def test_http_client_methods_cover(monkeypatch: pytest.MonkeyPatch) -> None:
    client = VaonisHTTPClient(base_url="http://example")
    calls: list[tuple[str, str]] = []

    def fake_request(self, method: str, path: str, **_kwargs: Any) -> DummyResponse:
        calls.append((method, path))
        return DummyResponse()

    monkeypatch.setattr(VaonisHTTPClient, "_request", fake_request)

    for name, func in inspect.getmembers(
        VaonisHTTPClient, predicate=inspect.isfunction
    ):
        if name.startswith("_") or name == "download_image":
            continue
        params = list(inspect.signature(func).parameters.values())[1:]
        args = [_dummy_value(param.name) for param in params]
        getattr(client, name)(*args)

    assert calls


def test_download_image_accepts_image_like_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = VaonisHTTPClient(base_url="http://example")
    seen: dict[str, Any] = {}

    class ImageResponse:
        def __init__(self) -> None:
            self.ok = False
            self.status_code = 500
            self.content = b"\xff\xd8\xff\x00"
            self.headers = {"content-type": "application/octet-stream"}

        def raise_for_status(self) -> None:
            raise requests.HTTPError("bad")

    monkeypatch.setattr(
        "vaonis_instruments.http_client.requests.get",
        lambda *args, **kwargs: seen.update(kwargs) or ImageResponse(),
    )

    content = client.download_image("/image", auth="token")
    assert content.startswith(b"\xff\xd8\xff")
    assert seen["headers"]["Authorization"] == "token"


def test_download_image_raises_for_non_image(monkeypatch: pytest.MonkeyPatch) -> None:
    client = VaonisHTTPClient(base_url="http://example")

    class TextResponse:
        def __init__(self) -> None:
            self.ok = False
            self.status_code = 500
            self.content = b"no"
            self.headers = {"content-type": "text/plain"}

        def raise_for_status(self) -> None:
            raise requests.HTTPError("bad")

    monkeypatch.setattr(
        "vaonis_instruments.http_client.requests.get",
        lambda *args, **kwargs: TextResponse(),
    )

    with pytest.raises(requests.HTTPError):
        client.download_image("http://example/image")
