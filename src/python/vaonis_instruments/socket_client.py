"""Socket.IO client for Vaonis instruments.

The Barnard Android app uses a Socket.IO connection (Engine.IO) for live status updates and
control coordination.

Default connection parameters (direct-to-device):
- url: http://10.0.0.1:8083
- path: /socket.io
- query: id={deviceId}&name={name}&countryCode={countryCode}

Events of interest (observed in the app):
- STATUS_UPDATED (payload: JSON object)
- CONTROL_ERROR (payload: unknown)
- connect / disconnect / reconnect / error (Socket.IO lifecycle)

Outbound messages are emitted on event "message" with an "action" string:
- takeControl
- releaseControl
- setSystemTime (payload: int64 epoch ms?)
- setUserName (payload: {device: <id>, user: <name or "null">})

This file purposefully does NOT embed any proprietary credentials.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from typing import Any, Callable, Optional

try:
    import socketio  # type: ignore
except Exception as e:  # pragma: no cover
    socketio = None  # type: ignore
    _import_error = e


@dataclass
class VaonisSocketClient:
    """Thin wrapper around python-socketio's client."""

    url: str = "http://10.0.0.1:8083"
    path: str = "/socket.io"
    device_id: str = ""
    name: str = ""
    country_code: str = ""
    logger: bool = False
    event_logger: Optional[logging.Logger] = None

    def __post_init__(self) -> None:
        if socketio is None:
            raise ImportError(
                "python-socketio is required for Socket.IO support. "
                "Install with: pip install python-socketio python-engineio"
            ) from _import_error
        self._sio = socketio.Client(logger=self.logger, engineio_logger=self.logger)

    def _log_event(self, event: str, payload: Any) -> None:
        if self.event_logger is None:
            return
        try:
            payload_repr = json.dumps(payload, ensure_ascii=True)
        except TypeError:
            payload_repr = str(payload)
        self.event_logger.info("SOCKET event %s payload=%s", event, payload_repr)

    def _wrap_handler(
        self, event: str, handler: Callable[..., None]
    ) -> Callable[..., None]:
        def wrapped(*args: Any, **kwargs: Any) -> None:
            payload: Any
            if kwargs:
                payload = kwargs
            elif len(args) == 1:
                payload = args[0]
            else:
                payload = args
            self._log_event(event, payload)
            handler(*args, **kwargs)

        return wrapped

    def on_status_updated(self, handler: Callable[[Any], None]) -> None:
        self._sio.on("STATUS_UPDATED", self._wrap_handler("STATUS_UPDATED", handler))

    def on_control_error(self, handler: Callable[[Any], None]) -> None:
        self._sio.on("CONTROL_ERROR", self._wrap_handler("CONTROL_ERROR", handler))

    def on_connect(self, handler: Callable[..., None]) -> None:
        self._sio.on("connect", self._wrap_handler("connect", handler))

    def on_disconnect(self, handler: Callable[..., None]) -> None:
        self._sio.on("disconnect", self._wrap_handler("disconnect", handler))

    def on_reconnect(self, handler: Callable[..., None]) -> None:
        self._sio.on("reconnect", self._wrap_handler("reconnect", handler))

    def on_error(self, handler: Callable[..., None]) -> None:
        self._sio.on("error", self._wrap_handler("error", handler))

    def on_connect_error(self, handler: Callable[..., None]) -> None:
        self._sio.on("connect_error", self._wrap_handler("connect_error", handler))

    def on_event(self, event: str, handler: Callable[..., None]) -> None:
        self._sio.on(event, self._wrap_handler(event, handler))

    def connect(self) -> None:
        query = f"id={self.device_id}&name={self.name}&countryCode={self.country_code}"
        if self.event_logger is not None:
            self.event_logger.info(
                "SOCKET connect url=%s path=%s query=%s",
                self.url,
                self.path,
                query,
            )
        self._sio.connect(
            self.url, socketio_path=self.path.lstrip("/"), query_string=query
        )

    def disconnect(self) -> None:
        if self.event_logger is not None:
            self.event_logger.info("SOCKET disconnect")
        self._sio.disconnect()

    def send_command(
        self,
        command: str,
        payload: Optional[Any] = None,
        *,
        callback: Optional[Callable[..., None]] = None,
    ) -> None:
        if payload is None:
            data = [command]
        else:
            data = [command, payload]
        if self.event_logger is not None:
            try:
                payload_repr = json.dumps(data, ensure_ascii=True)
            except TypeError:
                payload_repr = str(data)
            self.event_logger.info("SOCKET send %s", payload_repr)
        self._sio.emit("message", data, callback=callback)

    def take_control(self, user_id: Optional[str] = None) -> None:
        payload = {"userId": user_id} if user_id else None
        self.send_command("takeControl", payload)

    def release_control(self, user_id: Optional[str] = None) -> None:
        payload = {"userId": user_id} if user_id else None
        self.send_command("releaseControl", payload)

    def set_system_time(self, epoch_ms: int, *, use_object: bool = False) -> None:
        if use_object:
            payload = {"timestamp": int(epoch_ms)}
        else:
            payload = int(epoch_ms)
        self.send_command("setSystemTime", payload)

    def set_user_name(self, user_name: Optional[str]) -> None:
        payload = {
            "device": self.device_id,
            "user": user_name if user_name is not None else "null",
        }
        self.send_command("setUserName", payload)

    def send_user_name(self, user_id: str, user: str) -> None:
        payload = {"userId": user_id, "user": user}
        self.send_command("sendUserName", payload)

    def get_status(self, *, callback: Optional[Callable[..., None]] = None) -> None:
        self.send_command("getStatus", callback=callback)

    def restart_app(self, *, callback: Optional[Callable[..., None]] = None) -> None:
        self.send_command("restartApp", callback=callback)

    def shutdown(self, *, callback: Optional[Callable[..., None]] = None) -> None:
        self.send_command("shutdown", callback=callback)


StellinaSocketV2Client = VaonisSocketClient

__all__ = ["VaonisSocketClient", "StellinaSocketV2Client"]
