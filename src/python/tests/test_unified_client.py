from unittest.mock import Mock

from vaonis_instruments.unified_client import UnifiedHTTPClient


def test_call_operation_uses_route_manifest():
    client = UnifiedHTTPClient()
    client.base_url = "http://example:8082/v1"

    fake_resp = Mock()
    fake_resp.json.return_value = {"ok": True}
    fake_resp.raise_for_status.return_value = None
    client.session.request = Mock(return_value=fake_resp)

    resp = client.call_operation("appGetStatus")

    assert resp == {"ok": True}
    args, kwargs = client.session.request.call_args
    assert args[0] == "GET"
    assert args[1] == "http://example:8082/v1/app/status"
    assert kwargs["headers"] == {}
