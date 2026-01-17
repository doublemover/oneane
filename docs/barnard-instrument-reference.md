# Barnard Instrument Reference (HTTP + Socket.IO)

This document is the **technical overview** for the instrument-local control plane used by the Vaonis **Barnard** Android application.

It explains:
- how the repository's artifacts were derived (APK + firmware bundles)
- how to connect (ports, base paths, prefixes)
- how Barnard-style **challenge-response authentication** works
- how the **HTTP** and **Socket.IO** surfaces fit together

If you only want to get running quickly, start with the root `README.md`.

## Scope, provenance, and guardrails

**Scope:** instrument-local APIs (direct-to-device over the instrument Wi-Fi / LAN). Cloud APIs are mentioned only for completeness.

**Provenance (best-effort reverse engineering):**
- Barnard APK (base + splits)
- Firmware update bundles embedded in the app:
  - Stellina `v2.35.7`
  - Vespera `v3.0.12`

Common tooling used when regenerating artifacts:
- `apktool` (resources/smali decode)
- `jadx` (Kotlin/Java decompile)
- `protoc` (for APK-bundled `.proto` files)

**Guardrails:**
- Use only on devices you own or have explicit permission to control.
- This repo **does not ship** any proprietary key material. If you extract a key from your own Barnard artifacts, keep it local and private.

## Where the important artifacts live

- Canonical human-readable docs:
  - `docs/barnard-instrument-reference.md` (this file)
  - `src/unified/reference/API_REFERENCE_FULL.md` (consolidated reference)

- HTTP routes and schema catalogs:
  - `src/unified/openapi/vaonis_instrument_http_api_openapi_fixed.yaml` (most corrected OpenAPI)
  - `src/unified/routes/http_routes_union.json` (firmware-derived route union)
  - `src/unified/routes/HTTP_ROUTES.md` (same union, rendered as Markdown)
  - `src/unified/mappings/MAPPINGS_HTTP_ROUTES.md` (route -> operationId mapping)

- Socket.IO contracts:
  - `src/unified/asyncapi/vaonis_instrument_socket_api.asyncapi.yaml`
  - `src/unified/schemas/events/*.json` and `src/unified/schemas/socket/*.json`

- Clients and tooling:
  - Python: `src/python/vaonis_instruments/`
  - Node: `src/node/vaonis_instruments_unified/`
  - Auth key extraction: `tools/extract_auth_key.py`, `tools/extract_auth_key.js`

## Connection defaults

When connected to the instrument access point, Barnard typically uses:

- **Host:** `10.0.0.1`
- **HTTP:** port `8082`
  - base path: `/v1`
- **Socket.IO:** port `8083`
  - Socket.IO (Engine.IO v3) path: `/socket.io`

### Prefixes (Stellina/Vespera simulation roots)

The Barnard app and this repo's unified clients can probe optional prefixes:

- HTTP prefixes: `""`, `/stellina/http`, `/vespera/http`
- Socket prefixes (mainly for simulation/debug contexts): `/stellina/socket`, `/vespera/socket`

Practical guidance: do not hardcode a single base URL if you want portability across environments.

## Authentication

Many write/control HTTP endpoints require an `Authorization` header.

### Inputs

Call:

- `GET /v1/app/status`

It returns a `StatusResponse` object with:

- `success` (boolean)
- `result` (status snapshot), which includes:
  - `challenge` (string)
  - `telescopeId` (string)
  - `bootCount` (integer)

### Algorithm (Barnard semantics)

At a high level, Barnard constructs an `Authorization` header as follows:

1. Let `prefix = challenge[0]`.
2. Base64-decode the remainder: `challengeBytes = base64(challenge[1:])`.
3. Append ASCII: `|telescopeId|bootCount`.
4. Compute `digest = SHA-512(challengeBytes + tail)`.
5. Ed25519-sign the digest using Barnard's embedded key material.
6. Base64-encode the **signed message** (TweetNaCl/PyNaCl semantics: `signature || digest`).
7. Format:

```text
Authorization: Basic android|<prefix>|<base64(signedMessage)>
```

### Key material handling

This repo's clients can generate the header, but they require you to supply a key that you extracted from **your own** Barnard artifacts.

Default local key file locations:
- Python package: `src/python/.auth_key` (gitignored)
- Override: `VAONIS_AUTH_KEY_FILE=/absolute/path/to/.auth_key`

Extraction:

```bash
python tools/extract_auth_key.py
# or
node tools/extract_auth_key.js
```

## HTTP API surface

The Barnard APK's Retrofit interface exposes a stable subset of routes (settings, observation workflow, storage, logs, updates).

The firmware-derived route union expands the catalog with additional internal and debug routes.

Recommended sources-of-truth:
- Barnard-focused reference: `src/unified/reference/API_REFERENCE.md`
- Consolidated + corrected reference: `src/unified/reference/API_REFERENCE_FULL.md`
- Full route union: `src/unified/routes/http_routes_union.json`

### Safety note on debug/internal routes

Routes under namespaces such as `/debug`, `*/debug_*`, and similar are often not intended for external use and may:
- crash the instrument
- corrupt internal state
- invalidate calibration/operation workflows

Treat them as unsafe unless you have explicit vendor guidance and a recovery plan.

## Socket.IO behavior

Barnard uses Socket.IO primarily for:
- live status feed (`STATUS_UPDATED`)
- control coordination (master controller semantics)

**Connection:**
- URL: `http://10.0.0.1:8083`
- path: `/socket.io` (Engine.IO v3)
- query params (as observed): `id`, `name`, `countryCode`

**Common events:**
- `STATUS_UPDATED` (payload: status snapshot)
- `CONTROL_ERROR` (payload shape varies)

**Commands:**
This repo's clients send commands using the Socket.IO event name `message` with a single array argument:

```text
socket.emit('message', [<commandName>, <payload?>], <ack?>)
```

Observed command names include (not exhaustive):
- `takeControl`, `releaseControl`
- `getStatus`
- `setSystemTime`
- `setUserName` (Barnard-style)
- `sendUserName` (firmware schema variant)
- `restartApp`, `shutdown` (observed in client code; may vary by firmware)

## Cloud endpoints bundled in Barnard

Barnard contains references to several internet services (login, content, weather, logging). They are not required for local control.

See:
- `src/unified/artifacts/cloud_urls.txt`

## Compatibility notes

- Firmware versions differ; treat most fields in status objects as optional.
- Route coverage differs by model and firmware; prefer the unified clients for base URL detection and route lookup.
- Socket command schemas in `src/unified/schemas/socket/` are best-effort; some commands are observed in app code but not present in the firmware schema extraction (and vice versa).
