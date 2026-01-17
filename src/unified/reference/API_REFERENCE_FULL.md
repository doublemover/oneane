# Vaonis Barnard Instrument API (HTTP + Socket.IO) — Reverse‑Engineered Reference

This package contains a corrected, consolidated API reference intended for building reliable third‑party control software for **Vaonis Stellina and Vespera family instruments**.

It combines:
- The HTTP API surface (OpenAPI) exported from the Barnard mobile app reverse‑engineering output.
- Corrected **push/event** and **Socket.IO command** contracts derived from instrument firmware sources.
- Fixed/augmented schemas where the previous extraction produced Kotlin implementation artifacts (e.g., `*$delegate`).

## Scope and firmware baselines

This reference was validated against the firmware sources embedded in:
- **Stellina** firmware package: `v2.35.7`
- **Vespera** firmware package: `v3.0.12`

Where the two differ, the schema is written to be **forward‑compatible** (optional fields) and the differences are called out.

## Network endpoints

### HTTP API

- **Base URL (real instrument):** `http://10.0.0.1:8082/v1/`
- **OpenAPI file:** `openapi/vaonis_instrument_http_api_openapi.fixed.yaml`

The instrument is typically reachable at `10.0.0.1` when connected to its Wi‑Fi access point.

### Socket.IO push channel

- **Base URL:** `http://10.0.0.1:8083`
- **Namespace `/` (default):** control channel + `STATUS_UPDATED`
- **Namespace `/debug`:** debug push channel + `DEBUG_STATUS_UPDATED`

### Battery service

Firmware reserves `8084` as a battery-related service port (not required for the Barnard control surface; battery status is included in `STATUS_UPDATED`).

## Authentication

Most HTTP endpoints require an `Authorization` header. The instrument exposes a **challenge string** in status (`challenge`), which is used by the official client to compute an authorization value.

This package documents where `Authorization` is required, but **does not include key material**.

## Contents of this package

- `openapi/vaonis_instrument_http_api_openapi.fixed.yaml`
  - Corrected OpenAPI spec, including a fixed `StellinaStatus` schema and additional status-related schemas.

- `data/http_endpoints.json`
  - Convenience index: each HTTP endpoint with request/response schema refs.

- `schemas/http/*.json`
  - One JSON Schema file per OpenAPI component schema.

- `asyncapi/vaonis_instrument_socket_api.asyncapi.yaml`
  - AsyncAPI description of the Socket.IO events + control messages.

- `schemas/events/*.json`
  - JSON Schemas for server-emitted Socket.IO events.

- `schemas/socket/*.json`
  - JSON Schemas for Socket.IO control messages (command payloads and acknowledgements).

## HTTP API

Use the OpenAPI file as the authoritative catalog:

- `openapi/vaonis_instrument_http_api_openapi.fixed.yaml`

Key groups (paths) include:
- `general/*` – status, power/shutdown, settings
- `observation/*` – target selection, observation workflow, autofocus/focus, search
- `files/*` – user storage, capture store, reports, update upload

### Notes

- The firmware runs the API under `/v1/`.
- In some simulation environments there are path prefixes such as `/stellina/http` and `/vespera/http`. Those are not used on the physical instrument at `10.0.0.1`.

## Socket.IO API

### Connection handshake

Connect to the Socket.IO server on port `8083` with the following query parameters:

- `id` (required): a **client device identifier** (string)
- `name` (optional): client display name
- `isDebugUi` (optional): when truthy, marks the client as a debug UI (excluded from normal connected device lists)
- `countryCode` (optional): 2-letter country code used by region logic

Example (conceptual):

- `http://10.0.0.1:8083/?id=YOUR_CLIENT_ID&name=MyController`
- Debug namespace: `http://10.0.0.1:8083/debug?id=YOUR_CLIENT_ID&isDebugUi=true`

### Server-emitted events

#### `STATUS_UPDATED`

- Payload schema: `schemas/events/STATUS_UPDATED.json`
- Underlying type: `schemas/http/StellinaStatus.json`

Top-level fields include (non-exhaustive):
- Identity: `apiVersion`, `version`, `telescopeId`, `model`
- Boot/health: `bootCount`, `initError`, `previousBootError`, `boardInitError`, `boardError`, `boardInDebugMode`
- Time/position: `timestamp`, `elapsedTime`, `position`
- Control: `connectedDevices`, `masterDeviceId`
- Status blocks: `settings`, `logs`, `update`, `storage`, `internalBattery`, `sensors`, `motors`, `network`, `captureStore`
- Operations: `currentOperation`, `otherCurrentOperations`, `previousOperations`

#### `DEBUG_STATUS_UPDATED`

- Payload schema: `schemas/events/DEBUG_STATUS_UPDATED.json`

This event is emitted on the `/debug` namespace.

#### `CONNECTION_ERROR`

- Payload schema: `schemas/events/CONNECTION_ERROR.json`

Used to signal an invalid/insufficient handshake (e.g., missing `id`).

### Client control messages

The control channel uses the Socket.IO event name **`message`** with positional arguments:

```text
socket.emit('message', <commandName>, <payload?>, <ackCallback?>)
```

The firmware handler interprets:
- First argument: command name (string)
- Second argument: payload (optional; depends on command)
- Third argument: acknowledgement callback (optional)

#### Command catalog

| Command | Purpose | Request schema | Ack schema |
|---|---|---|---|
| `getStatus` | Return a single status snapshot | (none) | `schemas/socket/getStatus.response.json` |
| `takeControl` | Become master controller | (none) | `schemas/socket/takeControl.response.json` |
| `releaseControl` | Release master controller | (none) | `schemas/socket/releaseControl.response.json` |
| `setSystemTime` | Set instrument system time (ms epoch) | `schemas/socket/setSystemTime.request.json` | `schemas/socket/setSystemTime.response.json` |
| `sendUserName` | Associate a user name with a client userId | `schemas/socket/sendUserName.request.json` | `schemas/socket/sendUserName.response.json` |

#### Acknowledgement error shape

Errors are instances of a firmware error class serialized as a plain object. A client may see either:

- A **bare error object** (callback invoked with an error directly), or
- A wrapper object such as `{ "error": <StelError> }`

Error schema: `schemas/http/StelError.json`

## Stellina vs Vespera differences

### `STATUS_UPDATED`

The top-level schema is common across both firmware baselines.

### `DEBUG_STATUS_UPDATED`

Vespera firmware includes additional debug blocks (optional in the schema):
- `boardDebug`
- `stellarium`
- `darkManager`

## Practical integration guidance

1. Use Socket.IO `STATUS_UPDATED` as the primary real-time status feed.
2. Use `takeControl`/`releaseControl` to coordinate “master” semantics across clients.
3. Use HTTP for long-running operations that require uploads/downloads (reports, firmware update upload, capture-store file access).
4. Treat all status fields as potentially optional/nullable across firmware versions.

