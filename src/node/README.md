# Node packages

This directory contains the repo's Node/JS deliverables:

- `vaonis_barnard_sdk_js/`
  - **Extracted schema bundle** from the Barnard Android app (best-effort).
  - Useful if you want DTO/type definitions for HTTP request/response bodies and Socket.IO event payloads.

- `vaonis_instruments_unified/`
  - A small, dependency-light **unified HTTP + Socket.IO client**.
  - Includes Barnard-compatible **Authorization** header generation (you must supply your own locally extracted key material).
  - Uses the firmware-derived route union manifest so you can call operations by `operationId`.

## Prerequisites

- Node.js 18+ (uses built-in `fetch` and ESM modules)

## Quick start

### Unified client (recommended)

```bash
cd src/node/vaonis_instruments_unified
npm install
```

See `src/node/vaonis_instruments_unified/README.md` for usage.

### Schema bundle (types and models)

```bash
cd src/node/vaonis_barnard_sdk_js
npm install
```

See:
- `src/node/vaonis_barnard_sdk_js/README.md`
- `src/node/vaonis_barnard_sdk_js/docs/SCHEMAS.md`

## Notes

- All clients and artifacts are intended for **instrument-local** control (typically on `10.0.0.1` when connected to the instrument's Wi-Fi AP).
- This repo does **not** ship any proprietary key material. If you use auth helpers, extract the key from your own Barnard APK artifacts and keep it private.
