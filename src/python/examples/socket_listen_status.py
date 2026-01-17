import argparse
import json
import time
from typing import Any, Optional

from vaonis_instruments import VaonisSocketClient
from vaonis_instruments.logging_utils import format_payload, setup_logging

# Replace with values from your setup.
# deviceId is sent in the Socket.IO query string as `id=...`.
DEVICE_ID = "<deviceId>"
NAME = "<name>"
COUNTRY = "<countryCode>"


def main() -> int:
    parser = argparse.ArgumentParser(description="Listen for Socket.IO status events.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    log = setup_logging("socket_example", also_console=not args.json)
    sock = VaonisSocketClient(
        device_id=DEVICE_ID,
        name=NAME,
        country_code=COUNTRY,
        event_logger=log.logger,
    )

    def emit(event: str, payload: Optional[Any] = None) -> None:
        if args.json:
            print(
                json.dumps(
                    {"event": event, "payload": payload},
                    ensure_ascii=True,
                )
            )
            return
        if payload is None:
            print(event)
            return
        print(event)
        try:
            print(format_payload(payload, color=True))
        except Exception:
            print(payload)

    def on_status(payload):
        emit("STATUS_UPDATED", payload)

    def on_control_error(payload):
        emit("CONTROL_ERROR", payload)

    def on_connect(*_args, **_kwargs):
        emit("connect")

    def on_disconnect(*_args, **_kwargs):
        emit("disconnect")

    sock.on_status_updated(on_status)
    sock.on_control_error(on_control_error)
    sock.on_connect(on_connect)
    sock.on_disconnect(on_disconnect)

    try:
        sock.connect()
        emit("listening")
    except Exception as exc:
        log.logger.exception("Socket connect failed: %s", exc)
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True))
            return 1
        raise

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            sock.disconnect()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
