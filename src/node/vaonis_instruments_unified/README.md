# Vaonis instruments unified client (Node)

A small Node/JS client for Vaonis instrument **local** control:
- unified HTTP client with base URL/prefix detection
- Barnard-compatible Authorization header generation (Ed25519)
- minimal Socket.IO client mirroring Barnard's command semantics

This package is designed to work against the instrument's local API (commonly reachable at `10.0.0.1` when connected to the instrument AP). Use only on devices you own or have explicit permission to control.

## Prerequisites

- Node.js 18+ (built-in `fetch`)
- ESM (this package uses `import`)

## Install

```bash
npm install
```

## HTTP usage

### Create a client and read status

```js
import { UnifiedHttpClient } from "./src/index.js";

const client = new UnifiedHttpClient({ host: "10.0.0.1" });

// Auto-detects a working base URL by probing /app/status across known prefixes.
const statusResp = await client.request("GET", "app/status");

// StatusResponse shape is typically: { success: boolean, result: StellinaStatus }
console.log(statusResp.success, statusResp.result?.model, statusResp.result?.version);
```

### Call an operation by operationId

The unified client ships with a firmware-derived `http_routes_union.json` manifest.

```js
import { UnifiedHttpClient } from "./src/index.js";

const client = new UnifiedHttpClient();
const status = await client.callOperation("appGetStatus");
console.log(status);
```

### Download images (tolerant of non-2xx)

Barnard uses dynamic image URLs. `downloadImage()` returns bytes even if the HTTP status is non-2xx, as long as the payload looks like an image.

```js
const imageBytes = await client.downloadImage("stellina/http/v1/path/to/image");
// Buffer
console.log(imageBytes.length);
```

## Authentication

Many write/control endpoints require an `Authorization` header computed from:
- a server-provided `challenge` (from `GET /app/status`)
- the instrument `telescopeId` and `bootCount`
- an Ed25519 signature using key material extracted from your own Barnard app artifacts

### Build the Authorization header

```js
import { UnifiedHttpClient, buildAuthorizationHeader } from "./src/index.js";

const client = new UnifiedHttpClient();
const statusResp = await client.request("GET", "app/status");
const st = statusResp.result;

const auth = buildAuthorizationHeader({
  challenge: st.challenge,
  telescopeId: st.telescopeId,
  bootCount: st.bootCount,
});

await client.callOperation("generalPostStartObservation", {
  auth,
  jsonBody: {
    // StartObservationBody fields (see src/unified/schemas/http/StartObservationBody.json)
  },
});
```

### Key resolution rules

`buildAuthorizationHeader()` looks for key material in the following order:

1. `keyMaterial` option (base64 string, Buffer, or Uint8Array)
2. `keyFile` option
3. `VAONIS_AUTH_KEY_FILE` environment variable
4. `./.auth_key` (current working directory)
5. `src/node/vaonis_instruments_unified/.auth_key`
6. `src/python/.auth_key` (repo convention)

This package does not embed any proprietary key material.

## Socket.IO usage

Barnard also maintains a Socket.IO connection for real-time status and control coordination.

### Listen for status updates

```js
import { VaonisSocketClient } from "./src/index.js";

const socket = new VaonisSocketClient({
  deviceId: "your-client-id",
  name: "my-client",
  countryCode: "US",
});

socket.onStatusUpdated((payload) => console.log("STATUS_UPDATED", payload));
socket.onControlError((payload) => console.warn("CONTROL_ERROR", payload));

socket.connect();
```

### Send control commands

Commands are sent via the Socket.IO event name `message` with a single array payload:

```text
socket.emit('message', [<commandName>, <payload?>], <ack?>)
```

The helper exposes a few common commands:

```js
socket.takeControl();
socket.setSystemTime(Date.now());
socket.setUserName("my-user");
socket.releaseControl();
```

For less common commands, use `sendCommand` directly:

```js
socket.sendCommand("sendUserName", { userId: 123, user: "alice" }, (ack) => {
  console.log("ack", ack);
});
```

## Behavior notes

- **Base URL detection** probes: `""`, `/stellina/http`, `/vespera/http` with base path `/v1`.
- `request()` throws on non-2xx responses; `downloadImage()` is tolerant if bytes look like an image.
- Socket.IO uses `socket.io-client@2.x` for Engine.IO v3 compatibility.

## Tests

```bash
node --test
```
