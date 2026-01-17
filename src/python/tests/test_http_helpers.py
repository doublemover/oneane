from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
import requests

from vaonis_instruments.http_client import (
    _looks_like_image,
    _summarize_files,
    VaonisHTTPClient,
)
from vaonis_instruments.logging_utils import configure_logger


def test_looks_like_image_signatures() -> None:
    assert _looks_like_image(b"\xff\xd8\xff\x00", None)
    assert _looks_like_image(b"\x89PNG\r\n\x1a\n", None)
    assert _looks_like_image(b"GIF87a", None)
    assert not _looks_like_image(b"no", None)


def test_summarize_files_handles_named(tmp_path) -> None:
    class Dummy:
        def __init__(self, name: str) -> None:
            self.name = name

    summary = _summarize_files({"file": Dummy("file.txt")})
    assert summary == {"file": "file.txt"}


def test_request_error_logs(tmp_path) -> None:
    log_path = tmp_path / "http.log"
    logger = configure_logger("http_test", log_path)
    client = VaonisHTTPClient(logger=logger)

    with patch(
        "vaonis_instruments.http_client.requests.request",
        side_effect=requests.RequestException("boom"),
    ):
        with pytest.raises(requests.RequestException):
            client.get_status()

    assert log_path.read_text(encoding="utf-8")


def test_request_logs_payload(tmp_path) -> None:
    log_path = tmp_path / "http_payload.log"
    logger = configure_logger("http_payload", log_path)
    client = VaonisHTTPClient(logger=logger)
    fake_resp = Mock()
    fake_resp.content = b"{}"
    fake_resp.headers = {"content-type": "application/json"}
    fake_resp.text = "{}"
    fake_resp.raise_for_status.return_value = None
    fake_resp.json.return_value = {"ok": True}

    with patch(
        "vaonis_instruments.http_client.requests.request", return_value=fake_resp
    ):
        client.get_status()

    payload = log_path.read_text(encoding="utf-8")
    assert "HTTP response body" in payload
