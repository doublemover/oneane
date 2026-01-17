# Vaonis instruments (Python)

A minimal Python client for Vaonis instrument **local** APIs as used by the Barnard Android app:
- method-per-endpoint HTTP client (`VaonisHTTPClient`)
- unified HTTP client that calls firmware-derived routes by `operationId` (`UnifiedHTTPClient`)
- optional Socket.IO client (`VaonisSocketClient`)
- optional Tkinter GUI explorer (`vaonis_instruments.gui_app`)

This package does **not** ship any proprietary key material. If you want to call write/control endpoints, you must provide your own locally extracted key (see `tools/extract_auth_key.py`).

## Install

From the repository root:

```bash
python -m pip install -r src/python/requirements.txt
python -m pip install -e src/python
```

Optional Socket.IO support:

```bash
python -m pip install -e "src/python[socketio]"
```

## Quick start

### Read status

```python
from vaonis_instruments import UnifiedHTTPClient

client = UnifiedHTTPClient(host="10.0.0.1")
status = client.request("GET", "app/status")
print(status["success"], status["result"].get("version"))
```

### Build Authorization and call a control endpoint

```python
from vaonis_instruments import (
    UnifiedHTTPClient,
    AuthContext,
    build_authorization_header,
    ensure_auth_key,
)

# Writes src/python/.auth_key if missing (gitignored)
ensure_auth_key(prompt=input)

client = UnifiedHTTPClient(host="10.0.0.1")
status = client.request("GET", "app/status")

ctx = AuthContext(
    challenge=status["result"]["challenge"],
    telescope_id=status["result"]["telescopeId"],
    boot_count=status["result"]["bootCount"],
)
auth = build_authorization_header(ctx)

resp = client.call_operation(
    "generalPostStartObservation",
    auth=auth,
    json_body={
        # StartObservationBody fields (see src/unified/schemas/http/StartObservationBody.json)
    },
)
print(resp)
```

### Socket.IO status feed

```python
from vaonis_instruments import VaonisSocketClient

sock = VaonisSocketClient(device_id="your-client-id", name="my-client", country_code="US")
sock.on_status_updated(lambda payload: print("STATUS_UPDATED", payload))
sock.on_control_error(lambda payload: print("CONTROL_ERROR", payload))
sock.connect()
```

## GUI

```bash
python -m vaonis_instruments.gui_app
```

The GUI:
- loads a single unified schema bundle (`src/unified/schemas/schema_bundle.json`)
- can prompt to extract the auth key if missing
- logs HTTP and Socket.IO traffic under `logs/`

## Notes

- `UnifiedHTTPClient` auto-detects base URL prefixes by probing `/app/status` across:
  - `""`, `/stellina/http`, `/vespera/http`
- `download_image()` is tolerant of non-2xx responses if the payload looks like an image.
- Set `VAONIS_AUTH_KEY_FILE` to override the default key location.

## Tests

```bash
python -m pip install -r src/python/requirements-dev.txt
pytest -q
```
