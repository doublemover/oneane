from unittest.mock import Mock, patch

from vaonis_instruments.http_client import VaonisHTTPClient


def test_get_status_builds_url():
    client = VaonisHTTPClient(base_url="http://example:8082/v1")
    fake_resp = Mock()
    fake_resp.json.return_value = {"ok": True}
    fake_resp.raise_for_status.return_value = None

    with patch(
        "vaonis_instruments.http_client.requests.request", return_value=fake_resp
    ) as request:
        resp = client.get_status()

    assert resp == {"ok": True}
    args, kwargs = request.call_args
    assert args[0] == "GET"
    assert args[1] == "http://example:8082/v1/app/status"
    assert kwargs["headers"] == {}


def test_auth_header_is_set():
    client = VaonisHTTPClient(base_url="http://example:8082/v1")
    fake_resp = Mock()
    fake_resp.json.return_value = {"ok": True}
    fake_resp.raise_for_status.return_value = None

    with patch(
        "vaonis_instruments.http_client.requests.request", return_value=fake_resp
    ) as request:
        client.start_observation("token", {})

    args, kwargs = request.call_args
    assert args[0] == "POST"
    assert args[1] == "http://example:8082/v1/general/startObservation"
    assert kwargs["headers"]["Authorization"] == "token"
    assert kwargs["json"] == {}
