from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

import pytest

from vaonis_instruments import socket_client


class FakeSocketIOClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.handlers: Dict[str, Callable[..., None]] = {}
        self.emitted: List[tuple[str, Any]] = []
        self.connect_args: Optional[tuple[str, Optional[str], str]] = None
        self.disconnected = False

    def on(self, event: str, handler: Callable[..., None]) -> None:
        self.handlers[event] = handler

    def connect(
        self, url: str, *, socketio_path: Optional[str], query_string: str
    ) -> None:
        self.connect_args = (url, socketio_path, query_string)

    def disconnect(self) -> None:
        self.disconnected = True

    def emit(
        self, event: str, data: Any, callback: Optional[Callable[..., None]] = None
    ) -> None:
        self.emitted.append((event, data))
        if callback is not None:
            callback()


class FakeSocketIOModule:
    Client = FakeSocketIOClient


class FakeLogger:
    def __init__(self) -> None:
        self.messages: List[str] = []

    def info(self, message: str, *args: Any) -> None:
        self.messages.append(message % args if args else message)


@pytest.fixture
def socketio_client(
    monkeypatch: pytest.MonkeyPatch,
) -> socket_client.VaonisSocketClient:
    monkeypatch.setattr(socket_client, "socketio", FakeSocketIOModule)
    logger = FakeLogger()
    return socket_client.VaonisSocketClient(
        device_id="device-id",
        name="my-client",
        country_code="US",
        event_logger=logger,
    )


def test_socket_connect_and_emit(
    socketio_client: socket_client.VaonisSocketClient,
) -> None:
    socketio_client.connect()
    sio = socketio_client._sio
    assert isinstance(sio, FakeSocketIOClient)
    assert sio.connect_args == (
        "http://10.0.0.1:8083",
        "socket.io",
        "id=device-id&name=my-client&countryCode=US",
    )

    socketio_client.take_control()
    socketio_client.set_system_time(1234, use_object=True)
    socketio_client.set_user_name("alice")

    assert sio.emitted[0] == ("message", ["takeControl"])
    assert sio.emitted[1] == ("message", ["setSystemTime", {"timestamp": 1234}])
    assert sio.emitted[2] == (
        "message",
        ["setUserName", {"device": "device-id", "user": "alice"}],
    )


def test_socket_event_wrapping(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket_client, "socketio", FakeSocketIOModule)
    logger = FakeLogger()
    client = socket_client.VaonisSocketClient(event_logger=logger)
    received: List[Any] = []

    client.on_status_updated(lambda payload: received.append(payload))
    sio = client._sio
    handler = sio.handlers["STATUS_UPDATED"]
    handler({"ok": True})

    assert received == [{"ok": True}]
    assert any("STATUS_UPDATED" in msg for msg in logger.messages)
