from __future__ import annotations

from unittest.mock import Mock

import pytest
import requests

from vaonis_instruments.unified_client import UnifiedHTTPClient, _looks_like_image


def test_detect_base_url_success() -> None:
    client = UnifiedHTTPClient(prefixes=["", "/stellina/http"])
    good_resp = Mock()
    good_resp.ok = True
    bad_resp = Mock()
    bad_resp.ok = False
    client.session.get = Mock(side_effect=[bad_resp, good_resp])

    base = client.detect_base_url()

    assert base.endswith("/stellina/http/v1")
    assert client.base_url == base


def test_detect_base_url_failure() -> None:
    client = UnifiedHTTPClient(prefixes=["", "/stellina/http"])
    client.session.get = Mock(side_effect=requests.RequestException("boom"))
    with pytest.raises(RuntimeError):
        client.detect_base_url()


def test_download_image_accepts_bytes() -> None:
    client = UnifiedHTTPClient()
    client.base_url = "http://example:8082/v1"
    resp = Mock()
    resp.ok = False
    resp.content = b"\xff\xd8\xff\x00"
    resp.headers = {"content-type": "application/octet-stream"}
    client.session.get = Mock(return_value=resp)

    data = client.download_image("/path", auth="token")

    assert data == resp.content
    assert client.session.get.call_args.kwargs["headers"]["Authorization"] == "token"


def test_looks_like_image_false() -> None:
    assert not _looks_like_image(b"no", None)
