<p align=center>⚠️ Be careful dude this might be able to fuck shit up</p>

<p align=center> File Lots of Issues </p>

<p align=center><img src="https://github.com/doublemover/oneane/blob/main/screenshot.png" width=30% height=20%></img></p>

# Barnard Instrument Toolkit
[![CI](https://github.com/doublemover/oneane/actions/workflows/ci.yml/badge.svg)](https://github.com/doublemover/oneane/actions/workflows/ci.yml)

A small, practical toolkit for Vaonis instrument **local** APIs as used by the Barnard Android app (`com.vaonis.barnard`).

This repository contains:
- machine-readable API artifacts (OpenAPI, AsyncAPI, JSON Schemas, firmware-derived route catalogs)
- a minimal Python client (HTTP + optional Socket.IO + optional GUI)
- a minimal Node client (HTTP + Socket.IO + auth helper)

## Safety and legal

- Use only with devices you own or have explicit permission to control.
- Write/control endpoints can move hardware and disrupt observations.
- This repo does **not** ship any proprietary key material.

## Quick start (Python)

### 1) Install

From the repo root:

```bash
python -m pip install -r src/python/requirements.txt
python -m pip install -e src/python
```

Optional Socket.IO support:

```bash
python -m pip install -e "src/python[socketio]"
```

### 2) (Optional) Extract a local auth key

Many control endpoints require an `Authorization` header. If you have your own Barnard APK/ZIP artifacts, you can extract the embedded key to a local-only file:

```bash
python tools/extract_auth_key.py
```

By default this writes `src/python/.auth_key` (gitignored).

If you only have an APK, you can point the extractor at it (requires Java + apktool jar):

```bash
python tools/extract_auth_key.py --apk path/to/app.apk --apktool-jar path/to/apktool.jar
```

### 3) Read status

```python
from vaonis_instruments import UnifiedHTTPClient

client = UnifiedHTTPClient(host="10.0.0.1")
status = client.request("GET", "app/status")
print(status["success"], status["result"].get("version"))
```

### 4) Build Authorization and call a control route

```python
from vaonis_instruments import AuthContext, UnifiedHTTPClient, build_authorization_header

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
        # StartObservationBody fields
    },
)
print(resp)
```

### 5) Optional GUI

```bash
python -m vaonis_instruments.gui_app
```

Logs are written under `logs/`.

## Node client

```bash
cd src/node/vaonis_instruments_unified
npm install
```

```js
import { UnifiedHttpClient } from "./src/index.js";

const client = new UnifiedHttpClient({ host: "10.0.0.1" });
const status = await client.request("GET", "app/status");
console.log(status);
```

See `src/node/vaonis_instruments_unified/README.md` for auth and Socket.IO examples.

## Documentation and artifacts

- Instrument overview (ports, prefixes, auth): `docs/barnard-instrument-reference.md`
- Consolidated API reference: `src/unified/reference/API_REFERENCE_FULL.md`
- App-derived API reference: `src/unified/reference/API_REFERENCE.md`
- OpenAPI / AsyncAPI / schemas: `src/unified/`

